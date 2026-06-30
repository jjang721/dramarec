"""Ingest Korean dramas from TMDB into Postgres.

Idempotent: re-running updates existing rows (upsert) rather than duplicating,
so it is safe to run repeatedly while building up the catalog. Each show is
ingested in its own transaction, so one bad record never rolls back the batch.

    python -m pipeline.ingest --pages 10
"""

from __future__ import annotations

import argparse
from datetime import date, datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from app.db import engine, init_db
from app.models import Genre, Keyword, Person, Show, show_cast, show_genres, show_keywords
from pipeline.tmdb_client import TMDBClient

# Cap cast per show to the top-billed names; deeper credits add noise.
MAX_CAST = 10


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _dedupe_by_id(rows: list[dict]) -> list[dict]:
    """Last-wins dedupe. ON CONFLICT DO UPDATE rejects duplicate ids in one
    statement (e.g. TMDB lists the same actor twice for different roles)."""
    return list({r["id"]: r for r in rows}.values())


def _upsert_genres(conn: Connection, genres: list[dict]) -> None:
    if not genres:
        return
    rows = _dedupe_by_id([{"id": g["id"], "name": g["name"]} for g in genres])
    stmt = insert(Genre.__table__).values(rows)
    stmt = stmt.on_conflict_do_update(index_elements=["id"], set_={"name": stmt.excluded.name})
    conn.execute(stmt)


def _upsert_keywords(conn: Connection, keywords: list[dict]) -> None:
    if not keywords:
        return
    rows = _dedupe_by_id([{"id": k["id"], "name": k["name"]} for k in keywords])
    stmt = insert(Keyword.__table__).values(rows)
    stmt = stmt.on_conflict_do_update(index_elements=["id"], set_={"name": stmt.excluded.name})
    conn.execute(stmt)


def _trailer_key(details: dict) -> str | None:
    """Best YouTube trailer key: prefer an official Trailer, then any Trailer."""
    videos = [
        v for v in details.get("videos", {}).get("results", [])
        if v.get("site") == "YouTube" and v.get("key")
    ]
    for matches in (
        lambda v: v.get("type") == "Trailer" and v.get("official"),
        lambda v: v.get("type") == "Trailer",
        lambda v: True,
    ):
        for v in videos:
            if matches(v):
                return v["key"]
    return None


def _upsert_show(conn: Connection, details: dict) -> None:
    row = {
        "id": details["id"],
        "title": details.get("name") or details.get("original_name") or "Untitled",
        "original_title": details.get("original_name"),
        "overview": details.get("overview") or None,
        "first_air_date": _parse_date(details.get("first_air_date")),
        "original_language": details.get("original_language"),
        "popularity": details.get("popularity"),
        "vote_average": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "poster_path": details.get("poster_path"),
        "trailer_key": _trailer_key(details),
    }
    stmt = insert(Show.__table__).values(row)
    # Update everything except the embedding (preserve it across re-ingests).
    update_cols = {c: stmt.excluded[c] for c in row if c != "id"}
    stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=update_cols)
    conn.execute(stmt)


def _link(conn: Connection, table, left_col: str, right_col: str, left_id: int, right_ids) -> None:
    rows = [{left_col: left_id, right_col: rid} for rid in dict.fromkeys(right_ids)]
    if not rows:
        return
    conn.execute(insert(table).values(rows).on_conflict_do_nothing())


def _upsert_people(conn: Connection, cast: list[dict]) -> None:
    if not cast:
        return
    rows = _dedupe_by_id(
        [{"id": c["id"], "name": c["name"], "profile_path": c.get("profile_path")} for c in cast]
    )
    stmt = insert(Person.__table__).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={"name": stmt.excluded.name, "profile_path": stmt.excluded.profile_path},
    )
    conn.execute(stmt)


def _link_cast(conn: Connection, show_id: int, cast: list[dict]) -> None:
    seen: set[int] = set()
    rows = []
    for i, c in enumerate(cast):
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        rows.append({"show_id": show_id, "person_id": c["id"], "billing_order": c.get("order", i)})
    if not rows:
        return
    conn.execute(insert(show_cast).values(rows).on_conflict_do_nothing())


def _ingest_show(details: dict) -> None:
    """Persist one show and its relations in a single transaction."""
    with engine.begin() as conn:
        _upsert_show(conn, details)
        _link(conn, show_genres, "show_id", "genre_id",
              details["id"], [g["id"] for g in details.get("genres", [])])

        keywords = details.get("keywords", {}).get("results", [])
        _upsert_keywords(conn, keywords)
        _link(conn, show_keywords, "show_id", "keyword_id",
              details["id"], [k["id"] for k in keywords])

        cast = details.get("credits", {}).get("cast", [])[:MAX_CAST]
        _upsert_people(conn, cast)
        _link_cast(conn, details["id"], cast)


def ingest(pages: int) -> int:
    init_db()
    count, skipped = 0, 0
    with TMDBClient() as tmdb:
        with engine.begin() as conn:
            _upsert_genres(conn, tmdb.tv_genres())

        for page in range(1, pages + 1):
            results = tmdb.discover_korean_tv(page).get("results", [])
            if not results:
                break
            for summary in results:
                try:
                    details = tmdb.tv_details(summary["id"])
                    _ingest_show(details)
                    count += 1
                    print(f"  [{count:>4}] {details.get('name')}")
                except Exception as exc:  # noqa: BLE001 — skip & continue on any one show
                    skipped += 1
                    print(f"  skip {summary.get('name')!r}: {exc}")
            print(f"-- page {page} done --")
    if skipped:
        print(f"({skipped} shows skipped)")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Korean dramas from TMDB.")
    parser.add_argument("--pages", type=int, default=10, help="TMDB pages to fetch (20 shows each)")
    args = parser.parse_args()

    total = ingest(args.pages)
    print(f"\nDone. Ingested/updated {total} shows.")


if __name__ == "__main__":
    main()
