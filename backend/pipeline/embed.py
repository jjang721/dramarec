"""Generate content embeddings for shows and store them in pgvector.

For each show, builds a composite text (title + overview + genres + themes) and
embeds it with a local sentence-transformer (bge-base-en-v1.5, 768-dim, L2
normalized so cosine similarity is just a dot product). The vector is written to
shows.embedding.

    python -m pipeline.embed          # embed only shows missing an embedding
    python -m pipeline.embed --all    # re-embed everything
"""

from __future__ import annotations

import argparse

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import SessionLocal, init_db
from app.models import Show

MODEL_NAME = "BAAI/bge-base-en-v1.5"


def composite_text(show: Show) -> str:
    """The text we embed. Genres + themes give the vector its 'feel', not just plot."""
    parts = [show.title]
    if show.overview:
        parts.append(show.overview)
    if show.genres:
        parts.append("Genres: " + ", ".join(g.name for g in show.genres) + ".")
    if show.keywords:
        parts.append("Themes: " + ", ".join(k.name for k in show.keywords) + ".")
    return " ".join(parts)


def embed(all_: bool = False, batch_size: int = 32) -> int:
    init_db()
    # Imported lazily: loading torch/transformers is slow and only needed here.
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)

    with SessionLocal() as session:
        stmt = select(Show).options(
            selectinload(Show.genres), selectinload(Show.keywords)
        )
        if not all_:
            stmt = stmt.where(Show.embedding.is_(None))
        shows = session.scalars(stmt).all()

        if not shows:
            print("Nothing to embed.")
            return 0

        texts = [composite_text(s) for s in shows]
        vectors = model.encode(
            texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True
        )
        for show, vec in zip(shows, vectors):
            show.embedding = vec.tolist()
        session.commit()
        return len(shows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed shows into pgvector.")
    parser.add_argument("--all", action="store_true", help="re-embed every show")
    args = parser.parse_args()

    n = embed(all_=args.all)
    print(f"Embedded {n} shows with {MODEL_NAME}.")


if __name__ == "__main__":
    main()
