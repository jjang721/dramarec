"""Database engine and session factory."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Base


def _normalize(url: str) -> str:
    """Coerce platform-style URLs (postgres://, postgresql://) to the psycopg3
    driver SQLAlchemy expects. Hosts like Render/Heroku emit the bare forms."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix) and not url.startswith("postgresql+psycopg://"):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


engine = create_engine(_normalize(settings.database_url), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create the pgvector extension and all tables (idempotent)."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
