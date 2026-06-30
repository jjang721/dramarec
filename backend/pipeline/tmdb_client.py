"""A thin, retrying TMDB API client.

Handles the two real-world concerns of calling a third-party API: transient
failures and rate limiting (HTTP 429). Retries with exponential backoff via
tenacity; respects the Retry-After header when TMDB sends one.
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings


class TMDBError(RuntimeError):
    pass


class _RetryableStatus(Exception):
    """Raised for 429/5xx so tenacity retries them."""


class TMDBClient:
    def __init__(self, token: str | None = None, base_url: str | None = None) -> None:
        token = token or settings.tmdb_api_token
        if not token:
            raise TMDBError(
                "No TMDB token. Set TMDB_API_TOKEN in .env "
                "(https://www.themoviedb.org/settings/api)."
            )
        self._client = httpx.Client(
            base_url=base_url or settings.tmdb_base_url,
            headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
            timeout=15.0,
        )

    def __enter__(self) -> "TMDBClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self._client.close()

    @retry(
        retry=retry_if_exception_type(_RetryableStatus),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        resp = self._client.get(path, params=params)
        if resp.status_code == 429 or resp.status_code >= 500:
            raise _RetryableStatus(f"{resp.status_code} on {path}")
        if resp.status_code != 200:
            raise TMDBError(f"{resp.status_code} on {path}: {resp.text[:200]}")
        return resp.json()

    # --- endpoints -----------------------------------------------------------

    def tv_genres(self) -> list[dict[str, Any]]:
        return self._get("/genre/tv/list", language="en-US")["genres"]

    def discover_korean_tv(self, page: int) -> dict[str, Any]:
        # with_genres=18 (Drama) filters out Korean variety/talk/reality shows.
        return self._get(
            "/discover/tv",
            with_original_language="ko",
            with_genres="18",
            sort_by="popularity.desc",
            include_adult="false",
            page=page,
        )

    def tv_details(self, tv_id: int) -> dict[str, Any]:
        """Show details plus keywords and cast in a single request."""
        return self._get(
            f"/tv/{tv_id}", language="en-US", append_to_response="keywords,credits,videos"
        )
