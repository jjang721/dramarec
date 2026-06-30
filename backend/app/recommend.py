"""Content-based recommendations via pgvector, with a re-ranking stage.

Two entry points:
  * `similar_shows` — the baseline: raw nearest neighbours by cosine distance.
  * `recommend`     — production: pulls a larger candidate pool, then re-ranks
                      with MMR (for diversity) and a small popularity prior.

Keeping both lets the evaluation harness measure one against the other.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Show


@dataclass
class Recommendation:
    show: Show
    similarity: float  # cosine similarity in [-1, 1]; higher is closer


def _load_target(session: Session, show_id: int) -> Show:
    target = session.get(
        Show, show_id, options=[selectinload(Show.genres), selectinload(Show.keywords)]
    )
    if target is None:
        raise LookupError(f"show {show_id} not found")
    if target.embedding is None:
        raise ValueError(f"show {show_id} has no embedding yet — run pipeline.embed")
    return target


def _candidates(session: Session, target: Show, limit: int) -> list[tuple[Show, float]]:
    """Nearest `limit` shows to `target` as (show, cosine_similarity) pairs."""
    distance = Show.embedding.cosine_distance(target.embedding).label("distance")
    stmt = (
        select(Show, distance)
        .where(Show.id != target.id, Show.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
        .options(selectinload(Show.genres), selectinload(Show.keywords))
    )
    return [(show, 1.0 - dist) for show, dist in session.execute(stmt).all()]


def similar_shows(session: Session, show_id: int, k: int = 12) -> list[Recommendation]:
    """Baseline: the k nearest neighbours by cosine distance."""
    target = _load_target(session, show_id)
    return [Recommendation(show=s, similarity=sim) for s, sim in _candidates(session, target, k)]


def recommend(
    session: Session,
    show_id: int,
    k: int = 12,
    pool: int = 40,
    lambda_: float = 0.75,
    pop_weight: float = 0.15,
) -> list[Recommendation]:
    """Re-ranked recommendations.

    1. Pull `pool` nearest candidates.
    2. Blend cosine relevance with a normalized popularity prior (`pop_weight`).
    3. Greedily select `k` with MMR: each pick maximizes
       `lambda_ * score - (1 - lambda_) * max similarity to already-picked`,
       so near-duplicates are pushed down in favour of variety.

    The reported `similarity` stays the true cosine relevance (for the UI's
    match %), not the blended ranking score.
    """
    target = _load_target(session, show_id)
    candidates = _candidates(session, target, pool)
    if not candidates:
        return []

    shows = [c[0] for c in candidates]
    relevance = np.array([c[1] for c in candidates])

    # Embeddings are L2-normalized, so the dot product is cosine similarity.
    embeddings = np.array([np.asarray(s.embedding, dtype=float) for s in shows])
    pair_sim = embeddings @ embeddings.T

    pops = np.array([s.popularity or 0.0 for s in shows])
    span = pops.max() - pops.min()
    pop_norm = (pops - pops.min()) / span if span > 0 else np.zeros_like(pops)
    score = (1 - pop_weight) * relevance + pop_weight * pop_norm

    remaining = list(range(len(shows)))
    selected: list[int] = []
    while remaining and len(selected) < k:
        if not selected:
            best = max(remaining, key=lambda i: score[i])
        else:
            best = max(
                remaining,
                key=lambda i: lambda_ * score[i]
                - (1 - lambda_) * max(pair_sim[i][j] for j in selected),
            )
        selected.append(best)
        remaining.remove(best)

    # MMR picks the *set*; present it sorted by relevance so match % reads cleanly.
    selected.sort(key=lambda i: relevance[i], reverse=True)
    return [Recommendation(show=shows[i], similarity=float(relevance[i])) for i in selected]


def explain_match(source: Show, target: Show) -> str:
    """A short, human reason for the match, derived from what the two shows share.

    Rule-based for now (shared themes, then shared genres). Phase 6 swaps this for
    an LLM-generated explanation.
    """
    source_themes = {k.name for k in source.keywords}
    shared_themes = [k.name for k in target.keywords if k.name in source_themes]
    if shared_themes:
        picked = shared_themes[:2]
        noun = "themes" if len(picked) > 1 else "theme"
        return f"shares the {' and '.join(picked)} {noun}"

    source_genres = {g.name for g in source.genres}
    shared_genres = [g.name for g in target.genres if g.name in source_genres]
    if shared_genres:
        return f"a similar {' and '.join(shared_genres[:2]).lower()} feel"

    return "a similar tone and pace"
