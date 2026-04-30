"""Normalizer tests."""

from backend.core.extraction.normalizer import normalize_skill, normalize_skills


def test_normalizes_pytorch_variants():
    assert normalize_skill("pytorch") == "PyTorch"
    assert normalize_skill("PyTorch") == "PyTorch"
    assert normalize_skill("torch") == "PyTorch"


def test_normalizes_sklearn_variants():
    assert normalize_skill("sklearn") == "scikit-learn"


def test_removes_version_numbers_from_python():
    assert normalize_skill("Python 3.11") == "Python"


def test_preserves_gpt4_version():
    assert normalize_skill("gpt4") == "GPT-4"


def test_deduplicates_after_normalization():
    assert normalize_skills(["PyTorch", "torch", "pytorch"]) == ["PyTorch"]


def test_handles_empty_string():
    assert normalize_skill("") == ""


def test_handles_none_gracefully():
    assert normalize_skill(None) == ""


def test_batch_normalization_preserves_order():
    assert normalize_skills(["docker", "pytorch", "torch", "fastapi"]) == ["Docker", "PyTorch", "FastAPI"]
