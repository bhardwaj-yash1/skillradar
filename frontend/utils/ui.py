"""Small UI helpers for Streamlit pages."""

from __future__ import annotations


ROLE_LABELS = {
    "all": "All Roles",
    "applied_scientist": "Applied Scientist",
    "ml_engineer": "ML Engineer",
    "llm_engineer": "LLM Engineer",
    "data_scientist": "Data Scientist",
    "ai_engineer": "AI Engineer",
    "mlops_engineer": "MLOps Engineer",
    "data_engineer": "Data Engineer",
    "analytics_engineer": "Analytics Engineer",
    "computer_vision_engineer": "Computer Vision Engineer",
    "nlp_engineer": "NLP Engineer",
}

ROLE_DESCRIPTIONS = {
    "ai_engineer": "Builds user-facing AI products with LLMs, APIs, and retrieval systems.",
    "ml_engineer": "Ships classical and deep learning systems into production.",
    "llm_engineer": "Focuses on prompt design, RAG pipelines, evaluation, and model integration.",
    "data_scientist": "Drives experimentation, modeling, and decision support from data.",
    "mlops_engineer": "Owns deployment, orchestration, monitoring, and reliability for ML systems.",
    "data_engineer": "Builds data pipelines, transformations, and platform foundations.",
    "analytics_engineer": "Turns raw warehouse data into trusted business-ready models and reporting layers.",
    "computer_vision_engineer": "Develops perception systems for image and video workloads.",
    "nlp_engineer": "Builds language understanding and text generation systems.",
    "applied_scientist": "Combines experimentation, research, and product modeling on high-value problems.",
}


def humanize_role(role: str) -> str:
    """Convert a role key into a user-facing label."""
    return ROLE_LABELS.get(role, role.replace("_", " ").title())


def describe_role(role: str) -> str:
    """Return a short user-facing description for a role."""
    return ROLE_DESCRIPTIONS.get(role, "Tracked role in the current AI and data hiring snapshot.")


def infer_data_mode(posting_counts: dict[str, int]) -> tuple[str, str]:
    """Infer whether the UI is showing demo-only or scraped-backed data."""
    total_postings = sum(posting_counts.values())
    if total_postings <= 0:
        return (
            "Curated Snapshot",
            "Using a curated 12-week AI hiring snapshot built to simulate realistic market demand across 10 roles.",
        )
    return "Scraped Data", f"Backed by {total_postings} scraped postings currently stored in the database."
