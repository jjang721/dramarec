# dramarec

A personalized **Korean-drama recommendation engine** that recommends shows by
how they *feel* — not just by genre — explains *why* it picked each one, and
learns your taste as you go.

Built as an end-to-end ML system: ingestion → embeddings → vector search →
re-ranking → evaluation → a personalized, interactive web app.

> This product uses the TMDB API but is not endorsed or certified by TMDB.

## What it does
- **"For You" feed** — like a few shows; the app models your taste as the
  centroid of your liked-show embeddings and serves live recommendations (with
  optimistic UI and graceful cold-start).
- **"Because you liked X"** — content-based similar shows with a short, derived
  explanation ("shares the thriller theme").
- **Browse by cast** — a second recommendation signal: follow an actor to see
  their other shows (a people graph alongside the content embeddings).
- **Instant search**, **trailer playback** (TMDB → YouTube), a scroll-away hero,
  and light (editorial) / dark (cinema) themes.

## Architecture

```
TMDB API ─▶ ingestion ─▶ Postgres + pgvector ◀─ embeddings (bge, offline job)
                              │
                 FastAPI: content similarity + cast graph
                          + MMR re-ranking + popularity prior
                              │
                 Next.js (server + client) ─ taste loop, search, trailers
```

### Key decisions & trade-offs
- **Postgres + `pgvector`, not a dedicated vector DB** — one system to operate at
  this scale; ANN search is fast enough. Revisit past millions of vectors.
- **Content-based first** — sidesteps cold start; the personalized feed is the
  mean of liked-show embeddings, so it works from the first like.
- **Hybrid signals** — content embeddings *and* a cast graph, so it's more than a
  single cosine query.
- **MMR re-ranking + popularity prior** — pure nearest-neighbour returns
  near-duplicates; re-ranking trades a little precision for diversity/coverage
  (measured — see Evaluation).
- **Heavy ML deps isolated** — `torch`/`transformers` live in an `[ml]` extra used
  only by the offline embedding job, so the API image stays small.
- **API split from browser via CORS** — SSR calls the backend internally; the
  browser calls its public address.

## Tech stack
**Backend:** Python, FastAPI, SQLAlchemy 2.0, PostgreSQL + pgvector, NumPy,
sentence-transformers (BAAI/bge-base-en-v1.5).
**Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind v4,
Framer Motion.
**Ops:** Docker, docker-compose.

## Local development

Prereqs: Docker, Python 3.10+, Node 20+, and a TMDB API read access token
(free: themoviedb.org/settings/api → "API Read Access Token").

```bash
# 1. database
docker compose up -d db

# 2. backend (API + pipeline)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[ml]"           # ml extra = embedding deps
cp ../.env.example .env           # paste TMDB_API_TOKEN
python -m pipeline.ingest --pages 10   # ~200 dramas + cast + trailers
python -m pipeline.embed               # generate embeddings
uvicorn api.main:app --reload --port 8000

# 3. frontend (new terminal)
cd frontend
npm install
npm run dev                       # http://localhost:3000
```

## Data pipeline
- `pipeline.ingest` — idempotent upsert from TMDB (retry/backoff on rate limits,
  per-show transactions, dedup). Drama-only (`with_genres=18`).
- `pipeline.embed` — composite text per show (title + overview + genres + themes)
  → normalized bge embeddings → `pgvector`.

## Evaluation

```bash
python -m pipeline.evaluate --k 10
```

Reports precision@k, intra-list diversity, and catalogue coverage for the
baseline (nearest-neighbour) vs the re-ranked recommender. On the real catalogue,
re-ranking improves diversity and coverage for a small precision cost — the
relevance-vs-diversity trade-off, quantified.

## Deployment (Docker)

The whole stack runs with one command:

```bash
docker compose up --build           # db + backend + frontend
# frontend: http://localhost:3000   backend: http://localhost:8000
```

The API image excludes `torch`; embeddings are produced by the offline pipeline
against the database (data persists in the `dramarec-pgdata` volume).

### Hosting on Render
A `render.yaml` Blueprint provisions Postgres + backend + frontend. Steps:

1. Push this repo to GitHub.
2. Render → **New → Blueprint** → pick the repo (it reads `render.yaml`).
3. After services build, set **`BACKEND_URL`** on the frontend service to the
   backend's public URL (e.g. `https://dramarec-backend.onrender.com`).
4. Load data once, locally against the hosted DB (uses the `[ml]` extra):
   ```bash
   DATABASE_URL="<render external db url>" python -m pipeline.ingest --pages 10
   DATABASE_URL="<render external db url>" python -m pipeline.embed
   ```

The app needs just **one** env var per service: `DATABASE_URL` (backend, wired
automatically) and `BACKEND_URL` (frontend). The browser calls the frontend
same-origin; a runtime proxy route forwards `/api/*` to the backend — no CORS,
no build-time URLs.
