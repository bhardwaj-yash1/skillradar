"""Small UI helpers for Streamlit pages."""

from __future__ import annotations


ROLE_LABELS = {
    "all": "All Roles",
    "ml_engineer": "ML Engineer",
    "llm_engineer": "LLM Engineer",
    "data_scientist": "Data Scientist",
    "ai_engineer": "AI Engineer",
}


def humanize_role(role: str) -> str:
    """Convert a role key into a user-facing label."""
    return ROLE_LABELS.get(role, role.replace("_", " ").title())


def infer_data_mode(posting_counts: dict[str, int]) -> tuple[str, str]:
    """Infer whether the UI is showing demo-only or scraped-backed data."""
    total_postings = sum(posting_counts.values())
    if total_postings <= 0:
        return "Demo Data", "Using seeded market data for local exploration."
    return "Scraped Data", f"Backed by {total_postings} scraped postings currently stored in the database."
