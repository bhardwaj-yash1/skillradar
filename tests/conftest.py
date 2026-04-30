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
        weekly_rows = [
            ("PyTorch", "framework", "ml_engineer", 50 + week, 140),
            ("Docker", "tool", "ml_engineer", 45 + (week // 2), 140),
            ("Python", "language", "ml_engineer", 65, 140),
            ("MLflow", "tool", "ml_engineer", 28 + week, 140),
            ("LangChain", "framework", "llm_engineer", 40 + week, 120),
            ("Large Language Models", "concept", "llm_engineer", 55 + week, 120),
            ("Prompt Engineering", "concept", "llm_engineer", 49 + week, 120),
            ("SQL", "language", "data_scientist", 64, 130),
            ("Pandas", "framework", "data_scientist", 58, 130),
            ("PyTorch", "framework", "all", 46 + week, 390),
            ("Docker", "tool", "all", 43, 390),
            ("Python", "language", "all", 70, 390),
            ("LangChain", "framework", "all", 31 + week, 390),
            ("MLflow", "tool", "all", 22 + week, 390),
        ]
        for skill_name, category, role_filter, freq, total_postings in weekly_rows:
            test_db.add(
                SkillFrequency(
                    skill_name=skill_name,
                    category=category,
                    role_filter=role_filter,
                    week_start=start + timedelta(weeks=week),
                    count=int((freq / 100) * total_postings),
                    total_postings=total_postings,
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
