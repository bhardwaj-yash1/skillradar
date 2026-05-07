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
    monkeypatch.delenv("DATABASE_PRIVATE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PUBLIC_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("PGHOST", raising=False)
    monkeypatch.delenv("PGPORT", raising=False)
    monkeypatch.delenv("PGUSER", raising=False)
    monkeypatch.delenv("PGPASSWORD", raising=False)
    monkeypatch.delenv("PGDATABASE", raising=False)

    settings = Settings(_env_file=None)

    assert settings.DATABASE_URL == "sqlite+aiosqlite:///./data/skillradar.db"
    assert settings.SYNC_DATABASE_URL == "sqlite:///./data/skillradar.db"


def test_database_url_normalizes_postgres_and_derives_sync(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@db.example.com:5432/skillradar")
    monkeypatch.delenv("SYNC_DATABASE_URL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@db.example.com:5432/skillradar"
    assert settings.SYNC_DATABASE_URL == "postgresql://user:pass@db.example.com:5432/skillradar"


def test_pg_variables_override_localhost_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://skillradar:skillradar@localhost:5432/skillradar")
    monkeypatch.setenv("PGHOST", "db.railway.internal")
    monkeypatch.setenv("PGPORT", "5432")
    monkeypatch.setenv("PGUSER", "railway")
    monkeypatch.setenv("PGPASSWORD", "secret")
    monkeypatch.setenv("PGDATABASE", "railway")

    settings = Settings(_env_file=None)

    assert settings.DATABASE_URL == "postgresql+asyncpg://railway:secret@db.railway.internal:5432/railway"
    assert settings.SYNC_DATABASE_URL == "postgresql://railway:secret@db.railway.internal:5432/railway"
