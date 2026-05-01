"""Application configuration."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    APP_NAME: str = "SkillRadar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
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

    DATABASE_URL: str
    SYNC_DATABASE_URL: str

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

    @field_validator("SCRAPE_DELAY_MAX_SECONDS")
    @classmethod
    def validate_delay_range(cls, value: float, info: object) -> float:
        """Ensure scrape delay max is not lower than min."""
        min_delay = info.data.get("SCRAPE_DELAY_MIN_SECONDS", 0.0)  # type: ignore[attr-defined]
        if value < min_delay:
            raise ValueError("SCRAPE_DELAY_MAX_SECONDS must be >= SCRAPE_DELAY_MIN_SECONDS")
        return value

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

    @field_validator("OPENROUTER_HTTP_REFERER")
    @classmethod
    def validate_openrouter_referer(cls, value: str) -> str:
        """Keep the OpenRouter referer header URL-shaped."""
        parsed = urlparse(value)
        if value and not (parsed.scheme and parsed.netloc):
            raise ValueError("OPENROUTER_HTTP_REFERER must be an absolute URL")
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
