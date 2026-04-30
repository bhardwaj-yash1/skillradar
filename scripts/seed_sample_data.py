"""Seed SkillRadar with sample market data."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import crud
from backend.db.database import AsyncSessionLocal, init_db

BASE_SKILLS = [
    ("PyTorch", "framework", 67),
    ("LangChain", "framework", 54),
    ("Docker", "tool", 48),
    ("FastAPI", "framework", 43),
    ("Hugging Face", "tool", 41),
    ("TensorFlow", "framework", 40),
    ("Kubernetes", "tool", 30),
    ("Python", "language", 72),
]


async def seed(synthetic_only: bool) -> None:
    """Insert 12 weeks of synthetic frequency snapshots."""
    await init_db()
    start = date.today() - timedelta(weeks=11)
    async with AsyncSessionLocal() as session:
        count = 0
        for week_offset in range(12):
            week_start = start + timedelta(weeks=week_offset)
            for skill_name, category, baseline in BASE_SKILLS:
                if skill_name == "LangChain":
                    frequency = 20 + (week_offset * 3)
                elif skill_name == "TensorFlow":
                    frequency = 55 - week_offset
                else:
                    frequency = baseline
                await crud.upsert_skill_frequency(
                    session,
                    {
                        "skill_name": skill_name,
                        "category": category,
                        "role_filter": "all",
                        "week_start": week_start,
                        "count": int(frequency),
                        "total_postings": 100,
                        "frequency_pct": float(frequency),
                        "yoy_change_pct": None,
                    },
                )
                count += 1
    print(f"Seeded {count} frequency records")
    if synthetic_only:
        return
    print("Synthetic seed completed. Scrape pipeline can be triggered separately for live data.")


def main() -> None:
    """Parse CLI args and seed the database."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args()
    asyncio.run(seed(args.synthetic_only))


if __name__ == "__main__":
    main()
