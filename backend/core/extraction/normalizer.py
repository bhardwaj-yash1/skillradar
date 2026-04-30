"""Skill normalization helpers."""

from __future__ import annotations

import re

from backend.utils.text_utils import normalize_whitespace

VERSION_TRAIL_RE = re.compile(r"\b(?:v)?\d+(?:\.\d+)+\b")

CANONICAL_SKILLS: dict[str, tuple[str, str]] = {
    "python": ("Python", "language"),
    "python 3": ("Python", "language"),
    "fastapi": ("FastAPI", "framework"),
    "pytorch": ("PyTorch", "framework"),
    "torch": ("PyTorch", "framework"),
    "tensorflow": ("TensorFlow", "framework"),
    "tf": ("TensorFlow", "framework"),
    "langchain": ("LangChain", "framework"),
    "scikit learn": ("scikit-learn", "framework"),
    "sklearn": ("scikit-learn", "framework"),
    "docker": ("Docker", "tool"),
    "kubernetes": ("Kubernetes", "tool"),
    "aws": ("AWS", "cloud"),
    "azure": ("Azure", "cloud"),
    "gcp": ("GCP", "cloud"),
    "sql": ("SQL", "language"),
    "nlp": ("Natural Language Processing", "domain"),
    "natural language processing": ("Natural Language Processing", "domain"),
    "llm": ("Large Language Models", "concept"),
    "large language models": ("Large Language Models", "concept"),
    "transformers": ("Transformers", "framework"),
    "huggingface": ("Hugging Face", "tool"),
    "hugging face": ("Hugging Face", "tool"),
    "hf transformers": ("Hugging Face", "tool"),
    "mlops": ("MLOps", "concept"),
    "computer vision": ("Computer Vision", "domain"),
    "cv": ("Computer Vision", "domain"),
    "pandas": ("Pandas", "framework"),
    "numpy": ("NumPy", "framework"),
    "spark": ("Apache Spark", "framework"),
    "apache spark": ("Apache Spark", "framework"),
    "pyspark": ("PySpark", "framework"),
    "xgboost": ("XGBoost", "framework"),
    "lightgbm": ("LightGBM", "framework"),
    "postgres": ("PostgreSQL", "tool"),
    "postgresql": ("PostgreSQL", "tool"),
    "airflow": ("Airflow", "tool"),
    "llama": ("LLaMA", "concept"),
    "llama 2": ("LLaMA", "concept"),
    "llama2": ("LLaMA", "concept"),
    "vector database": ("Vector Databases", "concept"),
    "vector databases": ("Vector Databases", "concept"),
    "vectordb": ("Vector Databases", "concept"),
    "prompt engineering": ("Prompt Engineering", "concept"),
    "fine tuning": ("Fine-Tuning", "concept"),
    "finetuning": ("Fine-Tuning", "concept"),
    "gpt-4": ("GPT-4", "concept"),
    "gpt4": ("GPT-4", "concept"),
    "gpt-4o": ("GPT-4o", "concept"),
    "rag": ("Retrieval-Augmented Generation", "concept"),
    "retrieval augmented generation": ("Retrieval-Augmented Generation", "concept"),
}


def _normalize_key(skill: str) -> str:
    text = normalize_whitespace(skill).lower().replace("/", " ")
    if text not in {"gpt-4", "gpt4", "gpt-4o"}:
        text = VERSION_TRAIL_RE.sub("", text)
    text = normalize_whitespace(text.replace("-", " "))
    return text


def normalize_skill(skill: str | None) -> str:
    """Normalize one skill name to its canonical display form."""
    if not skill:
        return ""
    key = _normalize_key(skill)
    if not key:
        return ""
    if key in CANONICAL_SKILLS:
        return CANONICAL_SKILLS[key][0]
    return " ".join(part.capitalize() for part in key.split())


def infer_category(skill: str | None) -> str:
    """Infer category from a normalized or raw skill."""
    normalized = normalize_skill(skill)
    for _, (display, category) in CANONICAL_SKILLS.items():
        if display == normalized:
            return category
    return "other"


def normalize_skills(skills: list[str | None]) -> list[str]:
    """Normalize a list while preserving order and removing duplicates."""
    seen: set[str] = set()
    normalized: list[str] = []
    for skill in skills:
        value = normalize_skill(skill)
        if value and value not in seen:
            normalized.append(value)
            seen.add(value)
    return normalized
