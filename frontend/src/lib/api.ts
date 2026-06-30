// Client for the dramarec backend API. Types mirror the FastAPI response models.

// Browser: same-origin ("" → /api/*), forwarded by the runtime proxy route.
// Server (SSR): call the backend directly via BACKEND_URL.
const API_BASE =
  typeof window === "undefined" ? process.env.BACKEND_URL ?? "http://localhost:8000" : "";

export type Show = {
  id: number;
  title: string;
  overview: string | null;
  year: number | null;
  poster_path: string | null;
  vote_average: number | null;
  genres: string[];
};

export type ScoredShow = Show & { match: number; reason: string };

export type SimilarResponse = { source: Show; results: ScoredShow[] };

export type CastMember = { id: number; name: string; profile_path: string | null };

export type ShowDetail = Show & { trailer_key: string | null; cast: CastMember[] };

export type Actor = {
  id: number;
  name: string;
  profile_path: string | null;
  show_count: number;
};

export type ActorDetail = { actor: Actor; shows: Show[] };

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API ${res.status} for ${path}`);
  }
  return res.json() as Promise<T>;
}

export function getShows(limit = 24): Promise<Show[]> {
  return getJSON<Show[]>(`/api/shows?limit=${limit}`);
}

export function getShow(id: number): Promise<ShowDetail> {
  return getJSON<ShowDetail>(`/api/shows/${id}`);
}

export function getSimilar(id: number, k = 12): Promise<SimilarResponse> {
  return getJSON<SimilarResponse>(`/api/shows/${id}/similar?k=${k}`);
}

export async function recommendForUser(
  likedIds: number[],
  k = 12
): Promise<ScoredShow[]> {
  const res = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ liked_ids: likedIds, k }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API ${res.status} for /api/recommend`);
  return res.json() as Promise<ScoredShow[]>;
}

export function getActors(limit = 12): Promise<Actor[]> {
  return getJSON<Actor[]>(`/api/actors?limit=${limit}`);
}

export function getActor(id: number): Promise<ActorDetail> {
  return getJSON<ActorDetail>(`/api/actors/${id}`);
}

export function searchShows(q: string, limit = 8): Promise<Show[]> {
  return getJSON<Show[]>(`/api/search?q=${encodeURIComponent(q)}&limit=${limit}`);
}
