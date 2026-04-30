"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.db.database import get_db as app_get_db
from backend.db.models import Base, SkillFrequency
from backend.main import app


@pytest_asyncio.fixture
async def test_db():
    """Provide an isolated SQLite database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def sample_resume_bytes() -> bytes:
    """Return a minimal PDF containing resume-like text."""
    return b"Python PyTorch NLP Docker FastAPI"


@pytest_asyncio.fixture
async def sample_skill_frequencies(test_db):
    """Insert sample weekly trend data."""
    start = date.today() - timedelta(weeks=9)
    for week in range(10):
        for skill_name, category, freq in [
            ("PyTorch", "framework", 50 + week),
            ("TensorFlow", "framework", 60 - week),
            ("LangChain", "framework", 20 + (week * 3)),
            ("Docker", "tool", 45),
            ("FastAPI", "framework", 40 + (week // 2)),
        ]:
            test_db.add(
                SkillFrequency(
                    skill_name=skill_name,
                    category=category,
                    role_filter="all",
                    week_start=start + timedelta(weeks=week),
                    count=freq,
                    total_postings=100,
                    frequency_pct=float(freq),
                    yoy_change_pct=None,
                )
            )
    await test_db.commit()
    return test_db


@pytest.fixture
def api_client(test_db):
    """Provide a FastAPI test client with DB override."""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[app_get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
