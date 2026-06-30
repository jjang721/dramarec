"""Seed the database with a small, curated set of real Korean dramas.

This is development/demo data so the embedding + recommendation pipeline and the
frontend can be built and demoed without a TMDB token. Synthetic ids live in a
high range (9_000_000+) so they don't collide with real TMDB ids if you later
run `python -m pipeline.ingest`.

    python -m pipeline.seed
"""

from __future__ import annotations

from app.db import engine, init_db
from pipeline.ingest import (
    _link,
    _link_cast,
    _upsert_genres,
    _upsert_keywords,
    _upsert_people,
    _upsert_show,
)
from app.models import show_genres, show_keywords

# TMDB TV genre ids (real), so seeded rows are consistent with ingested rows.
G = {
    "Drama": 18,
    "Comedy": 35,
    "Crime": 80,
    "Mystery": 9648,
    "Sci-Fi & Fantasy": 10765,
    "Action & Adventure": 10759,
    "Family": 10751,
    "War & Politics": 10768,
}

# Synthetic keyword vocabulary (ids in a private range).
K = {name: 8_000_001 + i for i, name in enumerate([
    "romance", "melodrama", "found family", "slice of life", "nostalgia",
    "coming of age", "friendship", "healing", "mental health", "revenge",
    "chaebol", "time travel", "detective", "medical", "historical",
    "zombie", "military", "north korea", "survival game", "fantasy",
])}


def _show(id, name, original, year, overview, genres, keywords, votes, vote_avg, pop):
    return {
        "id": id,
        "name": name,
        "original_name": original,
        "overview": overview,
        "first_air_date": f"{year}-01-01",
        "original_language": "ko",
        "popularity": pop,
        "vote_average": vote_avg,
        "vote_count": votes,
        "poster_path": None,  # real posters arrive via TMDB ingestion
        "genres": [{"id": G[g], "name": g} for g in genres],
        "keywords": [{"id": K[k], "name": k} for k in keywords],
    }


SHOWS = [
    _show(9_000_001, "Crash Landing on You", "사랑의 불시착", 2019,
          "A South Korean heiress paraglides off course and crash-lands in North Korea, "
          "where a stern army officer hides and protects her.",
          ["Drama", "Comedy"], ["romance", "melodrama", "north korea"], 4200, 8.7, 95),
    _show(9_000_002, "Guardian: The Lonely and Great God", "쓸쓸하고 찬란하神 도깨비", 2016,
          "An immortal goblin cursed to live forever searches for the human bride who can "
          "end his life, and finds her in a cheerful girl who can see ghosts.",
          ["Sci-Fi & Fantasy", "Drama"], ["romance", "fantasy", "historical"], 3100, 8.6, 88),
    _show(9_000_003, "Reply 1988", "응답하라 1988", 2015,
          "Five families in a working-class Seoul neighborhood in the late 1980s share "
          "laughter, first love, and the ache of growing up.",
          ["Comedy", "Drama", "Family"],
          ["slice of life", "nostalgia", "found family", "friendship", "coming of age"],
          2600, 9.1, 80),
    _show(9_000_004, "My Mister", "나의 아저씨", 2018,
          "A weary middle-aged engineer and a hardened young woman crushed by debt find "
          "quiet, unexpected solace in each other's company.",
          ["Drama"], ["slice of life", "healing", "melodrama", "mental health"],
          1500, 9.0, 60),
    _show(9_000_005, "Signal", "시그널", 2016,
          "A profiler in the present and a detective in the past communicate through a "
          "mysterious old radio to solve long-cold cases.",
          ["Crime", "Mystery", "Sci-Fi & Fantasy"],
          ["detective", "time travel", "revenge"], 1900, 9.0, 72),
    _show(9_000_006, "Hospital Playlist", "슬기로운 의사생활", 2020,
          "Five doctors who have been friends since medical school navigate life, work, "
          "and a band on the side.",
          ["Drama", "Comedy"], ["medical", "friendship", "slice of life", "healing"],
          1700, 8.9, 70),
    _show(9_000_007, "Kingdom", "킹덤", 2019,
          "A crown prince investigates a mysterious plague raising the dead across the "
          "kingdom during Korea's Joseon era.",
          ["Sci-Fi & Fantasy", "Mystery", "Action & Adventure"],
          ["zombie", "historical", "survival game"], 2400, 8.3, 82),
    _show(9_000_008, "Vincenzo", "빈센조", 2021,
          "A Korean-Italian mafia consigliere returns to Seoul and turns mob tactics "
          "against a ruthless, corrupt conglomerate.",
          ["Crime", "Drama", "Action & Adventure"],
          ["revenge", "chaebol"], 2900, 8.4, 90),
    _show(9_000_009, "Itaewon Class", "이태원 클라쓰", 2020,
          "An ex-convict opens a bar in Itaewon, determined to topple the food empire "
          "whose heir destroyed his family.",
          ["Drama"], ["revenge", "coming of age", "chaebol"], 2100, 8.2, 78),
    _show(9_000_010, "SKY Castle", "SKY 캐슬", 2018,
          "Wealthy families in an elite enclave go to ruthless extremes to push their "
          "children into the country's top universities.",
          ["Drama", "Mystery"], ["chaebol", "melodrama"], 1300, 8.5, 64),
    _show(9_000_011, "It's Okay to Not Be Okay", "사이코지만 괜찮아", 2020,
          "A selfless psychiatric-ward caregiver and a children's-book author with an "
          "antisocial streak slowly heal each other's wounds.",
          ["Drama"], ["romance", "mental health", "healing"], 2200, 8.6, 76),
    _show(9_000_012, "Twenty-Five Twenty-One", "스물다섯 스물하나", 2022,
          "In the late 1990s, an aspiring fencer and a young man rebuilding his life from "
          "his family's ruin grow up alongside each other.",
          ["Drama", "Comedy"],
          ["romance", "coming of age", "nostalgia", "friendship"], 1600, 8.5, 74),
    _show(9_000_013, "Move to Heaven", "무브 투 헤븐", 2021,
          "A young man with Asperger's and his gruff ex-convict guardian run a "
          "trauma-cleaning business, telling the stories the dead left behind.",
          ["Drama"], ["found family", "healing", "slice of life"], 1100, 8.7, 55),
    _show(9_000_014, "D.P.", "디피", 2021,
          "Two army police soldiers chase down deserters and confront the harsh "
          "realities of why the men ran in the first place.",
          ["Drama", "Action & Adventure", "War & Politics"],
          ["military", "coming of age"], 1400, 8.3, 68),
    _show(9_000_015, "Mr. Sunshine", "미스터 션샤인", 2018,
          "Born into slavery, a man returns to Korea as a U.S. Marine officer and falls "
          "for an aristocrat amid the fight for independence.",
          ["Drama", "War & Politics"],
          ["historical", "romance", "melodrama"], 1500, 8.7, 66),
    _show(9_000_016, "Squid Game", "오징어 게임", 2021,
          "Hundreds of desperate, cash-strapped players accept an invitation to compete "
          "in deadly children's games for a tempting cash prize.",
          ["Drama", "Mystery", "Action & Adventure"],
          ["survival game", "revenge"], 14000, 7.8, 99),
]


# Cast per show. Note the deliberate overlaps — Lee Je-hoon (Signal + Move to
# Heaven) and Kim Tae-ri (Twenty-Five Twenty-One + Mr. Sunshine) — so following
# an actor surfaces more than one title.
CAST = {
    9_000_001: ["Hyun Bin", "Son Ye-jin"],
    9_000_002: ["Gong Yoo", "Kim Go-eun", "Lee Dong-wook"],
    9_000_003: ["Lee Hye-ri", "Park Bo-gum", "Ryu Jun-yeol"],
    9_000_004: ["Lee Sun-kyun", "IU"],
    9_000_005: ["Lee Je-hoon", "Kim Hye-soo", "Cho Jin-woong"],
    9_000_006: ["Jo Jung-suk", "Yoo Yeon-seok", "Jung Kyung-ho"],
    9_000_007: ["Ju Ji-hoon", "Bae Doona", "Ryu Seung-ryong"],
    9_000_008: ["Song Joong-ki", "Jeon Yeo-been"],
    9_000_009: ["Park Seo-joon", "Kim Da-mi"],
    9_000_010: ["Yum Jung-ah", "Lee Tae-ran"],
    9_000_011: ["Kim Soo-hyun", "Seo Ye-ji"],
    9_000_012: ["Kim Tae-ri", "Nam Joo-hyuk"],
    9_000_013: ["Lee Je-hoon", "Tang Jun-sang"],
    9_000_014: ["Jung Hae-in", "Koo Kyo-hwan"],
    9_000_015: ["Lee Byung-hun", "Kim Tae-ri"],
    9_000_016: ["Lee Jung-jae", "Park Hae-soo", "Jung Ho-yeon"],
}

# Stable synthetic ids for the unique actors above.
PEOPLE = {
    name: 7_000_001 + i
    for i, name in enumerate(dict.fromkeys(n for names in CAST.values() for n in names))
}


def seed() -> int:
    init_db()
    with engine.begin() as conn:
        _upsert_genres(conn, [{"id": gid, "name": name} for name, gid in G.items()])
        _upsert_keywords(conn, [{"id": kid, "name": name} for name, kid in K.items()])
        for details in SHOWS:
            _upsert_show(conn, details)
            _link(conn, show_genres, "show_id", "genre_id",
                  details["id"], [g["id"] for g in details["genres"]])
            _link(conn, show_keywords, "show_id", "keyword_id",
                  details["id"], [k["id"] for k in details["keywords"]])

            cast = [
                {"id": PEOPLE[name], "name": name, "profile_path": None, "order": i}
                for i, name in enumerate(CAST.get(details["id"], []))
            ]
            _upsert_people(conn, cast)
            _link_cast(conn, details["id"], cast)
    return len(SHOWS)


if __name__ == "__main__":
    n = seed()
    print(f"Seeded {n} Korean dramas.")
