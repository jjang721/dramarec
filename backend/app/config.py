"""Application configuration, loaded from environment / .env."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),  # works from repo root or backend/
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://dramarec:dramarec@localhost:5433/dramarec"

    # TMDB API v4 read access token (sent as a Bearer header).
    tmdb_api_token: str = ""
    tmdb_base_url: str = "https://api.themoviedb.org/3"

    # pgvector column dimension. Fixed once tables are created.
    embedding_dim: int = 768


settings = Settings()
