"""Runtime configuration tests."""

from backend.config import Settings


def test_cors_origins_accept_comma_separated_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://frontend.example.com, http://localhost:3000")

    settings = Settings(_env_file=None)

    assert settings.CORS_ORIGINS == ["https://frontend.example.com", "http://localhost:3000"]


def test_cors_origins_accept_json_array_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", '["https://frontend.example.com","http://localhost:3000"]')

    settings = Settings(_env_file=None)

    assert settings.CORS_ORIGINS == ["https://frontend.example.com", "http://localhost:3000"]


def test_database_url_defaults_to_sqlite_without_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SYNC_DATABASE_URL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.DATABASE_URL == "sqlite+aiosqlite:///./data/skillradar.db"
    assert settings.SYNC_DATABASE_URL == "sqlite:///./data/skillradar.db"
