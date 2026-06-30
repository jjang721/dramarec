"""dramarec HTTP API (FastAPI).

    uvicorn api.main:app --reload --port 8000

Endpoints:
    GET /api/shows                  most popular shows
    GET /api/shows/{id}             one show
    GET /api/shows/{id}/similar     content-based recommendations + match score
"""

from __future__ import annotations

import os

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.db import SessionLocal
from app.models import Person, Show, show_cast
from app.recommend import explain_match, recommend

app = FastAPI(title="dramarec API", version="0.1.0")

# Comma-separated list of allowed browser origins (set FRONTEND_ORIGIN in prod).
_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ShowOut(BaseModel):
    id: int
    title: str
    overview: str | None
    year: int | None
    poster_path: str | None
    vote_average: float | None
    genres: list[str]


class CastMember(BaseModel):
    id: int
    name: str
    profile_path: str | None


class ShowDetail(ShowOut):
    trailer_key: str | None
    cast: list[CastMember]


class ScoredShow(ShowOut):
    match: int  # 0-100, cosine similarity rescaled
    reason: str  # short human explanation of the match


class SimilarResponse(BaseModel):
    source: ShowOut
    results: list[ScoredShow]


class RecommendRequest(BaseModel):
    liked_ids: list[int]
    k: int = 12


class ActorOut(BaseModel):
    id: int
    name: str
    profile_path: str | None
    show_count: int


class ActorDetail(BaseModel):
    actor: ActorOut
    shows: list[ShowOut]


def _to_show_out(show: Show) -> ShowOut:
    return ShowOut(
        id=show.id,
        title=show.title,
        overview=show.overview,
        year=show.first_air_date.year if show.first_air_date else None,
        poster_path=show.poster_path,
        vote_average=show.vote_average,
        genres=[g.name for g in show.genres],
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/shows")
def list_shows(limit: int = 60) -> list[ShowOut]:
    with SessionLocal() as session:
        stmt = (
            select(Show)
            .options(selectinload(Show.genres))
            .order_by(Show.popularity.desc().nullslast())
            .limit(limit)
        )
        return [_to_show_out(s) for s in session.scalars(stmt)]


@app.get("/api/search")
def search(q: str, limit: int = 8) -> list[ShowOut]:
    term = q.strip()
    if not term:
        return []
    pattern = f"%{term}%"
    with SessionLocal() as session:
        stmt = (
            select(Show)
            .options(selectinload(Show.genres))
            .where(or_(Show.title.ilike(pattern), Show.original_title.ilike(pattern)))
            .order_by(Show.popularity.desc().nullslast())
            .limit(limit)
        )
        return [_to_show_out(s) for s in session.scalars(stmt)]


@app.get("/api/shows/{show_id}")
def get_show(show_id: int) -> ShowDetail:
    with SessionLocal() as session:
        show = session.get(
            Show, show_id, options=[selectinload(Show.genres), selectinload(Show.cast)]
        )
        if show is None:
            raise HTTPException(status_code=404, detail="show not found")
        cast = [
            CastMember(id=p.id, name=p.name, profile_path=p.profile_path)
            for p in show.cast
        ]
        return ShowDetail(
            **_to_show_out(show).model_dump(), trailer_key=show.trailer_key, cast=cast
        )


def _popular(session, k: int) -> list[ScoredShow]:
    stmt = (
        select(Show)
        .options(selectinload(Show.genres))
        .order_by(Show.popularity.desc().nullslast())
        .limit(k)
    )
    return [
        ScoredShow(**_to_show_out(s).model_dump(), match=0, reason="popular right now")
        for s in session.scalars(stmt)
    ]


@app.post("/api/recommend")
def recommend_for_user(req: RecommendRequest) -> list[ScoredShow]:
    """Personalized feed: recommend from a taste vector (mean of liked embeddings).

    Cold start (no likes / no embeddings) falls back to popular shows.
    """
    with SessionLocal() as session:
        if not req.liked_ids:
            return _popular(session, req.k)

        liked = session.scalars(
            select(Show)
            .where(Show.id.in_(req.liked_ids), Show.embedding.is_not(None))
            .options(selectinload(Show.genres), selectinload(Show.keywords))
        ).all()
        if not liked:
            return _popular(session, req.k)

        liked_vecs = np.array([np.asarray(s.embedding, dtype=float) for s in liked])
        taste = liked_vecs.mean(axis=0)
        norm = np.linalg.norm(taste)
        if norm:
            taste = taste / norm

        distance = Show.embedding.cosine_distance(taste.tolist()).label("distance")
        rows = session.execute(
            select(Show, distance)
            .where(Show.embedding.is_not(None), Show.id.notin_(req.liked_ids))
            .order_by(distance)
            .limit(req.k)
            .options(selectinload(Show.genres), selectinload(Show.keywords))
        ).all()

        results = []
        for show, dist in rows:
            cand = np.asarray(show.embedding, dtype=float)
            # nearest liked show drives the explanation ("shares the X theme")
            nearest = liked[int(np.argmax(liked_vecs @ cand))]
            results.append(
                ScoredShow(
                    **_to_show_out(show).model_dump(),
                    match=round((1 - dist) * 100),
                    reason=explain_match(nearest, show),
                )
            )
        return results


@app.get("/api/actors")
def list_actors(limit: int = 12) -> list[ActorOut]:
    """Actors with the most shows in the catalogue."""
    count = func.count(show_cast.c.show_id).label("show_count")
    with SessionLocal() as session:
        stmt = (
            select(Person, count)
            .join(show_cast, Person.id == show_cast.c.person_id)
            .group_by(Person.id)
            .order_by(count.desc(), Person.name)
            .limit(limit)
        )
        return [
            ActorOut(
                id=p.id, name=p.name, profile_path=p.profile_path, show_count=n
            )
            for p, n in session.execute(stmt)
        ]


@app.get("/api/actors/{actor_id}")
def get_actor(actor_id: int) -> ActorDetail:
    with SessionLocal() as session:
        person = session.get(Person, actor_id)
        if person is None:
            raise HTTPException(status_code=404, detail="actor not found")
        stmt = (
            select(Show)
            .join(show_cast, Show.id == show_cast.c.show_id)
            .where(show_cast.c.person_id == actor_id)
            .options(selectinload(Show.genres))
            .order_by(Show.popularity.desc().nullslast())
        )
        shows = [_to_show_out(s) for s in session.scalars(stmt)]
        actor = ActorOut(
            id=person.id,
            name=person.name,
            profile_path=person.profile_path,
            show_count=len(shows),
        )
        return ActorDetail(actor=actor, shows=shows)


@app.get("/api/shows/{show_id}/similar")
def get_similar(show_id: int, k: int = 12) -> SimilarResponse:
    with SessionLocal() as session:
        source = session.get(
            Show, show_id, options=[selectinload(Show.genres), selectinload(Show.keywords)]
        )
        if source is None:
            raise HTTPException(status_code=404, detail="show not found")
        try:
            recs = recommend(session, show_id, k)
        except ValueError as exc:  # embeddings not generated yet
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        results = [
            ScoredShow(
                **_to_show_out(r.show).model_dump(),
                match=round(r.similarity * 100),
                reason=explain_match(source, r.show),
            )
            for r in recs
        ]
        return SimilarResponse(source=_to_show_out(source), results=results)
