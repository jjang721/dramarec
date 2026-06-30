"""SQLAlchemy ORM models — the schema source of truth.

A show has many genres and many keywords (both many-to-many). The `embedding`
column holds the content vector populated in Phase 2; it is nullable so that
ingestion (Phase 1) can run before any embeddings exist.
"""

from __future__ import annotations

from datetime import date

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.config import settings


class Base(DeclarativeBase):
    pass


# Association tables (composite PKs => inserts are naturally idempotent).
show_genres = Table(
    "show_genres",
    Base.metadata,
    Column("show_id", ForeignKey("shows.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

show_keywords = Table(
    "show_keywords",
    Base.metadata,
    Column("show_id", ForeignKey("shows.id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True),
)

# Cast carries billing order (lead actors first), so it is more than a plain join.
show_cast = Table(
    "show_cast",
    Base.metadata,
    Column("show_id", ForeignKey("shows.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", ForeignKey("people.id", ondelete="CASCADE"), primary_key=True),
    Column("billing_order", Integer),
)


class Show(Base):
    __tablename__ = "shows"

    # TMDB id is used directly as the primary key.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    title: Mapped[str] = mapped_column(String(500))
    original_title: Mapped[str | None] = mapped_column(String(500))
    overview: Mapped[str | None] = mapped_column(Text)
    first_air_date: Mapped[date | None] = mapped_column(Date)
    original_language: Mapped[str | None] = mapped_column(String(10))
    popularity: Mapped[float | None] = mapped_column(Float)
    vote_average: Mapped[float | None] = mapped_column(Float)
    vote_count: Mapped[int | None] = mapped_column(Integer)
    poster_path: Mapped[str | None] = mapped_column(String(255))
    trailer_key: Mapped[str | None] = mapped_column(String(20))  # YouTube key

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.embedding_dim), nullable=True
    )

    genres: Mapped[list["Genre"]] = relationship(secondary=show_genres, back_populates="shows")
    keywords: Mapped[list["Keyword"]] = relationship(
        secondary=show_keywords, back_populates="shows"
    )
    cast: Mapped[list["Person"]] = relationship(
        secondary=show_cast,
        back_populates="shows",
        order_by=show_cast.c.billing_order,
    )


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(100))

    shows: Mapped[list[Show]] = relationship(secondary=show_genres, back_populates="genres")


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(200))

    shows: Mapped[list[Show]] = relationship(secondary=show_keywords, back_populates="keywords")


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(200))
    profile_path: Mapped[str | None] = mapped_column(String(255))

    shows: Mapped[list[Show]] = relationship(secondary=show_cast, back_populates="cast")
