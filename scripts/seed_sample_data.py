"""Seed SkillRadar with a realistic curated market snapshot."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import crud
from backend.db.database import AsyncSessionLocal, init_db

ROLE_PROFILES = {
    "ai_engineer": {
        "postings_base": 160,
        "postings_growth": 7,
        "skills": [
            ("Python", "language", 72, 1.0),
            ("Large Language Models", "concept", 66, 1.4),
            ("Prompt Engineering", "concept", 58, 1.2),
            ("FastAPI", "framework", 49, 0.8),
            ("LangChain", "framework", 52, 1.1),
            ("Hugging Face", "tool", 47, 0.9),
            ("Vector Databases", "concept", 39, 1.2),
            ("Docker", "tool", 46, 0.6),
            ("AWS", "cloud", 41, 0.5),
            ("Retrieval-Augmented Generation", "concept", 36, 1.3),
            ("Kubernetes", "tool", 29, 0.4),
            ("Fine-Tuning", "concept", 31, 0.9),
        ],
    },
    "ml_engineer": {
        "postings_base": 182,
        "postings_growth": 5,
        "skills": [
            ("Python", "language", 74, 0.4),
            ("PyTorch", "framework", 59, 0.9),
            ("scikit-learn", "framework", 56, 0.3),
            ("Docker", "tool", 51, 0.5),
            ("SQL", "language", 46, 0.2),
            ("MLflow", "tool", 35, 1.0),
            ("AWS", "cloud", 42, 0.3),
            ("Kubernetes", "tool", 32, 0.4),
            ("Apache Spark", "framework", 28, 0.5),
            ("TensorFlow", "framework", 31, -0.3),
            ("Airflow", "tool", 24, 0.6),
            ("MLOps", "concept", 33, 0.8),
        ],
    },
    "llm_engineer": {
        "postings_base": 148,
        "postings_growth": 9,
        "skills": [
            ("Python", "language", 71, 0.7),
            ("Large Language Models", "concept", 68, 1.3),
            ("Prompt Engineering", "concept", 64, 1.2),
            ("LangChain", "framework", 56, 1.0),
            ("Vector Databases", "concept", 45, 1.2),
            ("Retrieval-Augmented Generation", "concept", 47, 1.4),
            ("Hugging Face", "tool", 49, 0.8),
            ("Fine-Tuning", "concept", 38, 1.0),
            ("LLaMA", "concept", 42, 1.1),
            ("FastAPI", "framework", 37, 0.7),
            ("Docker", "tool", 35, 0.4),
            ("AWS", "cloud", 31, 0.3),
        ],
    },
    "data_scientist": {
        "postings_base": 172,
        "postings_growth": 3,
        "skills": [
            ("Python", "language", 76, 0.2),
            ("SQL", "language", 69, 0.2),
            ("Pandas", "framework", 61, 0.3),
            ("scikit-learn", "framework", 58, 0.2),
            ("NumPy", "framework", 55, 0.1),
            ("Experimentation", "concept", 36, 0.8),
            ("XGBoost", "framework", 39, 0.4),
            ("LightGBM", "framework", 35, 0.3),
            ("PyTorch", "framework", 33, 0.5),
            ("AWS", "cloud", 30, 0.2),
            ("Tableau", "tool", 27, 0.3),
            ("Power BI", "tool", 24, 0.4),
        ],
    },
    "mlops_engineer": {
        "postings_base": 124,
        "postings_growth": 6,
        "skills": [
            ("Docker", "tool", 63, 0.5),
            ("Kubernetes", "tool", 57, 0.7),
            ("AWS", "cloud", 51, 0.4),
            ("MLflow", "tool", 46, 0.9),
            ("CI/CD", "tool", 44, 0.8),
            ("Python", "language", 43, 0.2),
            ("MLOps", "concept", 48, 0.8),
            ("Airflow", "tool", 29, 0.4),
            ("Databricks", "tool", 25, 0.5),
            ("GCP", "cloud", 27, 0.4),
            ("Azure", "cloud", 22, 0.4),
            ("FastAPI", "framework", 20, 0.3),
        ],
    },
    "data_engineer": {
        "postings_base": 166,
        "postings_growth": 4,
        "skills": [
            ("SQL", "language", 76, 0.3),
            ("Python", "language", 62, 0.2),
            ("Apache Spark", "framework", 54, 0.6),
            ("Airflow", "tool", 49, 0.6),
            ("dbt", "tool", 46, 0.9),
            ("Databricks", "tool", 39, 0.7),
            ("Snowflake", "tool", 37, 0.7),
            ("AWS", "cloud", 34, 0.3),
            ("GCP", "cloud", 28, 0.3),
            ("Docker", "tool", 24, 0.4),
            ("PySpark", "framework", 42, 0.7),
            ("Data Modeling", "concept", 31, 0.5),
        ],
    },
    "analytics_engineer": {
        "postings_base": 112,
        "postings_growth": 4,
        "skills": [
            ("SQL", "language", 78, 0.2),
            ("dbt", "tool", 62, 0.9),
            ("Data Modeling", "concept", 54, 0.5),
            ("Python", "language", 34, 0.2),
            ("Power BI", "tool", 41, 0.4),
            ("Tableau", "tool", 39, 0.4),
            ("BI Reporting", "tool", 48, 0.4),
            ("Snowflake", "tool", 35, 0.5),
            ("Databricks", "tool", 21, 0.4),
            ("Airflow", "tool", 19, 0.2),
            ("AWS", "cloud", 18, 0.2),
            ("Pandas", "framework", 20, 0.2),
        ],
    },
    "computer_vision_engineer": {
        "postings_base": 96,
        "postings_growth": 2,
        "skills": [
            ("Python", "language", 70, 0.2),
            ("PyTorch", "framework", 63, 0.7),
            ("Computer Vision", "domain", 66, 0.6),
            ("OpenCV", "framework", 48, 0.5),
            ("TensorFlow", "framework", 35, -0.2),
            ("NumPy", "framework", 42, 0.1),
            ("AWS", "cloud", 24, 0.2),
            ("Docker", "tool", 29, 0.3),
            ("MLOps", "concept", 27, 0.4),
            ("Kubernetes", "tool", 18, 0.2),
            ("Fine-Tuning", "concept", 17, 0.2),
            ("Hugging Face", "tool", 21, 0.3),
        ],
    },
    "nlp_engineer": {
        "postings_base": 106,
        "postings_growth": 5,
        "skills": [
            ("Python", "language", 72, 0.3),
            ("Natural Language Processing", "domain", 68, 0.5),
            ("Transformers", "framework", 57, 0.9),
            ("Large Language Models", "concept", 52, 1.0),
            ("Prompt Engineering", "concept", 43, 0.8),
            ("Hugging Face", "tool", 49, 0.7),
            ("PyTorch", "framework", 44, 0.4),
            ("Fine-Tuning", "concept", 36, 0.8),
            ("Vector Databases", "concept", 24, 0.7),
            ("Retrieval-Augmented Generation", "concept", 26, 0.8),
            ("AWS", "cloud", 20, 0.2),
            ("Docker", "tool", 24, 0.2),
        ],
    },
    "applied_scientist": {
        "postings_base": 92,
        "postings_growth": 3,
        "skills": [
            ("Python", "language", 73, 0.2),
            ("Experimentation", "concept", 52, 0.7),
            ("scikit-learn", "framework", 49, 0.3),
            ("PyTorch", "framework", 45, 0.4),
            ("SQL", "language", 38, 0.2),
            ("Pandas", "framework", 41, 0.2),
            ("NumPy", "framework", 39, 0.2),
            ("XGBoost", "framework", 33, 0.3),
            ("LightGBM", "framework", 29, 0.3),
            ("AWS", "cloud", 22, 0.2),
            ("MLOps", "concept", 21, 0.3),
            ("FastAPI", "framework", 16, 0.2),
        ],
    },
}

SEASONAL_BIAS = [0.0, 0.6, -0.3, 0.9, 0.1, -0.2, 0.7, -0.4, 0.5, 0.0, 0.8, 0.2]


def _clamp_frequency(value: float) -> float:
    return round(max(8.0, min(86.0, value)), 1)


def _total_postings(profile: dict, week_offset: int) -> int:
    seasonal = int((week_offset % 3) * 2)
    return profile["postings_base"] + (profile["postings_growth"] * week_offset) + seasonal


async def seed(synthetic_only: bool) -> None:
    """Insert 12 weeks of curated role-specific frequency snapshots."""
    await init_db()
    start = date.today() - timedelta(weeks=11)
    async with AsyncSessionLocal() as session:
        await crud.clear_skill_frequencies(session)
        count = 0

        for week_offset in range(12):
            week_start = start + timedelta(weeks=week_offset)
            aggregate_counts: dict[str, dict[str, float | str]] = defaultdict(
                lambda: {"category": "other", "count": 0.0, "total_postings": 0.0}
            )
            aggregate_total_postings = 0

            for role_filter, profile in ROLE_PROFILES.items():
                total_postings = _total_postings(profile, week_offset)
                aggregate_total_postings += total_postings
                for skill_name, category, baseline, slope in profile["skills"]:
                    frequency_pct = _clamp_frequency(baseline + (slope * week_offset) + SEASONAL_BIAS[week_offset])
                    count_value = int(round((frequency_pct / 100.0) * total_postings))
                    await crud.upsert_skill_frequency(
                        session,
                        {
                            "skill_name": skill_name,
                            "category": category,
                            "role_filter": role_filter,
                            "week_start": week_start,
                            "count": count_value,
                            "total_postings": total_postings,
                            "frequency_pct": frequency_pct,
                            "yoy_change_pct": None,
                        },
                    )
                    aggregate_counts[skill_name]["category"] = category
                    aggregate_counts[skill_name]["count"] = float(aggregate_counts[skill_name]["count"]) + count_value
                    aggregate_counts[skill_name]["total_postings"] = float(aggregate_counts[skill_name]["total_postings"]) + total_postings
                    count += 1

            for skill_name, payload in aggregate_counts.items():
                combined_count = int(payload["count"])
                frequency_pct = round((combined_count / max(aggregate_total_postings, 1)) * 100, 1)
                await crud.upsert_skill_frequency(
                    session,
                    {
                        "skill_name": skill_name,
                        "category": str(payload["category"]),
                        "role_filter": "all",
                        "week_start": week_start,
                        "count": combined_count,
                        "total_postings": aggregate_total_postings,
                        "frequency_pct": frequency_pct,
                        "yoy_change_pct": None,
                    },
                )
                count += 1

    print(f"Seeded {count} frequency records across 10 curated roles plus the overall market view.")
    if synthetic_only:
        return
    print("Curated market snapshot completed. Scrape pipeline can still be triggered separately for live source experiments.")


def main() -> None:
    """Parse CLI args and seed the database."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args()
    asyncio.run(seed(args.synthetic_only))


if __name__ == "__main__":
    main()
