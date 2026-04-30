"""JD extractor heuristic tests."""

from backend.config import get_settings
from backend.core.extraction.jd_extractor import JobDescriptionExtractor


def test_heuristic_extractor_flags_optional_vs_required_skills():
    text = (
        "We require strong experience in Python, PyTorch, and Docker. "
        "Experience with LangChain is a plus. Familiarity with Airflow is nice to have."
    )
    payload = JobDescriptionExtractor(get_settings())._extract_heuristically(text)
    skills = {item["name"]: item for item in payload["skills"]}

    assert skills["Python"]["is_required"] is True
    assert skills["PyTorch"]["is_required"] is True
    assert skills["LangChain"]["is_required"] is False
    assert skills["Airflow"]["is_required"] is False


def test_heuristic_extractor_infers_role_experience_and_domain():
    text = (
        "Hiring an LLM Engineer with 5+ years of experience to build RAG systems, "
        "prompt engineering workflows, and vector database integrations."
    )
    payload = JobDescriptionExtractor(get_settings())._extract_heuristically(text)

    assert payload["role_category"] == "llm_engineer"
    assert payload["experience_level"] == "mid"
    assert payload["domain"] == "generative_ai"


def test_heuristic_extractor_normalizes_richer_aliases():
    text = "Work with HuggingFace, pyspark, postgresql, and fine tuning large models."
    payload = JobDescriptionExtractor(get_settings())._extract_heuristically(text)
    names = [item["name"] for item in payload["skills"]]

    assert "Hugging Face" in names
    assert "PySpark" in names
    assert "PostgreSQL" in names
    assert "Fine-Tuning" in names
