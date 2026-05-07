"""Application configuration."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Literal
from urllib.parse import quote_plus, urlparse

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_DB_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _normalize_postgres_prefix(url: str) -> str:
    """Expand legacy postgres:// URLs to SQLAlchemy-friendly prefixes."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _to_async_database_url(url: str) -> str:
    """Convert a DB URL to the async driver form used by the app."""
    normalized = _normalize_postgres_prefix(url)
    if normalized.startswith("postgresql://"):
        return normalized.replace("postgresql://", "postgresql+asyncpg://", 1)
    if normalized.startswith("sqlite:///"):
        return normalized.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return normalized


def _to_sync_database_url(url: str) -> str:
    """Convert a DB URL to the sync driver form used by Alembic."""
    normalized = _normalize_postgres_prefix(url)
    if normalized.startswith("postgresql+asyncpg://"):
        return normalized.replace("postgresql+asyncpg://", "postgresql://", 1)
    if normalized.startswith("sqlite+aiosqlite:///"):
        return normalized.replace("sqlite+aiosqlite:///", "sqlite:///", 1)
    return normalized


def _is_local_postgres_url(url: str | None) -> bool:
    """Return whether the URL points at a localhost Postgres instance."""
    if not url:
        return False
    parsed = urlparse(_normalize_postgres_prefix(url))
    return parsed.hostname in LOCAL_DB_HOSTS


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    APP_NAME: str = "SkillRadar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: Any = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    LLM_PROVIDER: Literal["groq", "openrouter", "openai"] = "groq"
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.0

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_APP_NAME: str = "SkillRadar"
    OPENROUTER_HTTP_REFERER: str = "http://localhost:8501"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/skillradar.db"
    SYNC_DATABASE_URL: str | None = None
    DATABASE_PRIVATE_URL: str = ""
    DATABASE_PUBLIC_URL: str = ""
    POSTGRES_URL: str = ""
    PGHOST: str = ""
    PGPORT: str = "5432"
    PGUSER: str = ""
    PGPASSWORD: str = ""
    PGDATABASE: str = ""

    SCRAPE_DELAY_MIN_SECONDS: float = 2.0
    SCRAPE_DELAY_MAX_SECONDS: float = 5.0
    MAX_JDS_PER_SCRAPE_RUN: int = 50
    SCRAPE_USER_AGENT_ROTATE: bool = True

    WEEKLY_SCRAPE_DAY: Literal[
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ] = "monday"
    WEEKLY_SCRAPE_HOUR: int = 2
    WEEKLY_DIGEST_DAY: Literal[
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ] = "monday"
    WEEKLY_DIGEST_HOUR: int = 9

    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "SkillRadar <noreply@skillradar.dev>"
    EMAIL_DIGEST_SUBJECT: str = "Your Weekly AI/ML Job Market Update"

    UPLOAD_DIR: str = "./data/uploads"
    MAX_RESUME_SIZE_MB: int = 10

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """Accept JSON arrays or comma-separated strings from deployment env vars."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError("CORS_ORIGINS must be a JSON array or comma-separated list") from exc
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @field_validator("SCRAPE_DELAY_MAX_SECONDS")
    @classmethod
    def validate_delay_range(cls, value: float, info: object) -> float:
        """Ensure scrape delay max is not lower than min."""
        min_delay = info.data.get("SCRAPE_DELAY_MIN_SECONDS", 0.0)  # type: ignore[attr-defined]
        if value < min_delay:
            raise ValueError("SCRAPE_DELAY_MAX_SECONDS must be >= SCRAPE_DELAY_MIN_SECONDS")
        return value

    @field_validator("OPENROUTER_HTTP_REFERER")
    @classmethod
    def validate_openrouter_referer(cls, value: str) -> str:
        """Keep the OpenRouter referer header URL-shaped."""
        parsed = urlparse(value)
        if value and not (parsed.scheme and parsed.netloc):
            raise ValueError("OPENROUTER_HTTP_REFERER must be an absolute URL")
        return value

    @model_validator(mode="after")
    def setup_database_urls(self) -> "Settings":
        """Auto-configure database URLs for async runtime and sync migrations."""
        resolved_source_url = self._resolve_database_source_url()
        self.DATABASE_URL = _to_async_database_url(resolved_source_url)

        sync_source = self.SYNC_DATABASE_URL or resolved_source_url
        if not sync_source or _is_local_postgres_url(sync_source):
            sync_source = resolved_source_url
        self.SYNC_DATABASE_URL = _to_sync_database_url(sync_source)
        return self

    def _resolve_database_source_url(self) -> str:
        """Choose the best available source URL, preferring non-local cloud values."""
        cloud_candidates = [
            self.DATABASE_PRIVATE_URL,
            self.DATABASE_PUBLIC_URL,
            self.POSTGRES_URL,
            self._build_pg_url(),
        ]

        for candidate in cloud_candidates:
            if candidate and not _is_local_postgres_url(candidate):
                return candidate

        if self.DATABASE_URL and not _is_local_postgres_url(self.DATABASE_URL):
            return self.DATABASE_URL

        if self.DATABASE_URL:
            return self.DATABASE_URL

        return "sqlite+aiosqlite:///./data/skillradar.db"

    def _build_pg_url(self) -> str:
        """Build a URL from Railway-style PG* variables when present."""
        if not all([self.PGHOST, self.PGUSER, self.PGPASSWORD, self.PGDATABASE]):
            return ""
        port = self.PGPORT or "5432"
        return (
            "postgresql://"
            f"{quote_plus(self.PGUSER)}:{quote_plus(self.PGPASSWORD)}@"
            f"{self.PGHOST}:{port}/{self.PGDATABASE}"
        )

    @property
    def llm_api_key(self) -> str:
        """Return the API key for the active provider."""
        return {
            "groq": self.GROQ_API_KEY,
            "openrouter": self.OPENROUTER_API_KEY,
            "openai": self.OPENAI_API_KEY,
        }[self.LLM_PROVIDER]

    @property
    def llm_model(self) -> str:
        """Return the model for the active provider."""
        return {
            "groq": self.GROQ_MODEL,
            "openrouter": self.OPENROUTER_MODEL,
            "openai": self.OPENAI_MODEL,
        }[self.LLM_PROVIDER]

    @property
    def llm_base_url(self) -> str:
        """Return the base URL for the active provider."""
        return {
            "groq": self.GROQ_BASE_URL,
            "openrouter": self.OPENROUTER_BASE_URL,
            "openai": self.OPENAI_BASE_URL,
        }[self.LLM_PROVIDER]

    @property
    def llm_default_headers(self) -> dict[str, str]:
        """Return provider-specific request headers."""
        if self.LLM_PROVIDER == "openrouter":
            return {
                "HTTP-Referer": self.OPENROUTER_HTTP_REFERER,
                "X-Title": self.OPENROUTER_APP_NAME,
            }
        return {}

    @property
    def llm_enabled(self) -> bool:
        """Return whether the active provider has a usable API key."""
        key = (self.llm_api_key or "").strip()
        return bool(key and key.lower() not in {"replace_me", "your_api_key_here"})

    @property
    def safe_temperature(self) -> float:
        """Normalize temperature for providers with stricter bounds."""
        if self.LLM_PROVIDER == "groq" and self.LLM_TEMPERATURE <= 0:
            return 1e-8
        return self.LLM_TEMPERATURE


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
