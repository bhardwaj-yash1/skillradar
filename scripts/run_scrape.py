"""Manual scrape trigger script."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import get_settings
from backend.core.scraper.scraper_manager import ScraperManager
from backend.db.database import AsyncSessionLocal, init_db


async def run(source: str | None, role: str, limit: int) -> None:
    """Run the scrape pipeline manually."""
    await init_db()
    manager = ScraperManager(get_settings())
    async with AsyncSessionLocal() as session:
        result = await manager.run_scrape_pipeline(
            session,
            role=role,
            location="india",
            max_results=limit,
            sources=[source] if source else None,
        )
    print(result)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["naukri", "indeed", "linkedin"], default=None)
    parser.add_argument("--role", default="ml engineer")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    asyncio.run(run(args.source, args.role, args.limit))


if __name__ == "__main__":
    main()
