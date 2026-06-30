"""Offline evaluation of recommendation quality.

Runs every show as a query and reports three metrics for the baseline
(nearest-neighbour) vs the re-ranked (MMR + popularity) recommender:

  * precision@k   — fraction of recommendations that share >=1 theme with the
                    query. A proxy for relevance in the absence of user data.
  * diversity     — intra-list diversity: mean pairwise (1 - cosine) within a
                    recommendation list. Higher = less repetitive.
  * coverage      — fraction of the catalogue that appears across all lists.
                    Higher = the recommender isn't funnelling everyone to the
                    same few shows.

    python -m pipeline.evaluate
    python -m pipeline.evaluate --k 5

The point: re-ranking should trade a little precision for noticeably more
diversity and coverage — and now you can show the numbers.
"""

from __future__ import annotations

import argparse

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import SessionLocal
from app.models import Show
from app.recommend import Recommendation, recommend, similar_shows


def _is_relevant(query: Show, candidate: Show) -> bool:
    query_themes = {k.name for k in query.keywords}
    return any(k.name in query_themes for k in candidate.keywords)


def precision_at_k(query: Show, recs: list[Recommendation], k: int) -> float:
    top = recs[:k]
    if not top:
        return 0.0
    return sum(_is_relevant(query, r.show) for r in top) / len(top)


def intra_list_diversity(recs: list[Recommendation]) -> float:
    embs = [np.asarray(r.show.embedding, dtype=float) for r in recs if r.show.embedding is not None]
    if len(embs) < 2:
        return 0.0
    matrix = np.array(embs)
    sims = matrix @ matrix.T
    n = len(embs)
    iu = np.triu_indices(n, k=1)
    return float(np.mean(1.0 - sims[iu]))


def evaluate(k: int = 5, pool: int = 40) -> None:
    with SessionLocal() as session:
        shows = session.scalars(
            select(Show)
            .where(Show.embedding.is_not(None))
            .options(selectinload(Show.keywords), selectinload(Show.genres))
        ).all()
        total = len(shows)
        if total == 0:
            print("No embedded shows. Run pipeline.seed and pipeline.embed first.")
            return

        methods = {
            "baseline (NN)": lambda sid: similar_shows(session, sid, k),
            "re-ranked (MMR+pop)": lambda sid: recommend(session, sid, k, pool),
        }

        print(f"Evaluated {total} shows · k={k}\n")
        print(f"{'method':<24}{'precision@k':>13}{'diversity':>12}{'coverage':>11}")
        print("-" * 60)
        for label, fn in methods.items():
            precisions, diversities, covered = [], [], set()
            for query in shows:
                recs = fn(query.id)
                precisions.append(precision_at_k(query, recs, k))
                diversities.append(intra_list_diversity(recs))
                covered.update(r.show.id for r in recs)
            print(
                f"{label:<24}"
                f"{np.mean(precisions):>13.3f}"
                f"{np.mean(diversities):>12.3f}"
                f"{len(covered) / total:>11.1%}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate recommendation quality.")
    parser.add_argument("--k", type=int, default=5, help="recommendations per query")
    parser.add_argument("--pool", type=int, default=40, help="candidate pool for re-ranking")
    args = parser.parse_args()
    evaluate(k=args.k, pool=args.pool)


if __name__ == "__main__":
    main()
