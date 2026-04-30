"""Dependency injection helpers."""

from backend.config import Settings, get_settings
from backend.db.database import get_db


def get_app_settings() -> Settings:
    """Return application settings dependency."""
    return get_settings()


__all__ = ["get_app_settings", "get_db"]
