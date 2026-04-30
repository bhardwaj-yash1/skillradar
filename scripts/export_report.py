"""Export skill frequency data as CSV or JSON."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from backend.db.database import AsyncSessionLocal, init_db
from backend.db.models import SkillFrequency


async def export_data(fmt: str, role: str, output: str) -> None:
    """Write current skill frequency rows to disk."""
    await init_db()
    async with AsyncSessionLocal() as session:
        rows = (
            await session.execute(
                select(SkillFrequency).where(SkillFrequency.role_filter == role).order_by(SkillFrequency.week_start.asc())
            )
        ).scalars().all()
    payload = [
        {
            "skill_name": row.skill_name,
            "category": row.category,
            "week_start": row.week_start.isoformat(),
            "frequency_pct": row.frequency_pct,
            "count": row.count,
            "total_postings": row.total_postings,
            "yoy_change_pct": row.yoy_change_pct,
        }
        for row in rows
    ]
    if fmt == "json":
        with open(output, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    else:
        with open(output, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(payload[0].keys()) if payload else [])
            if payload:
                writer.writeheader()
                writer.writerows(payload)
    print(f"Exported {len(payload)} rows to {output}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    parser.add_argument("--role", default="all")
    parser.add_argument("--output", default="report.csv")
    args = parser.parse_args()
    asyncio.run(export_data(args.format, args.role, args.output))


if __name__ == "__main__":
    main()
