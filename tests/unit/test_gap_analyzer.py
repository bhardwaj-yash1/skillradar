"""Gap analyzer tests."""

from backend.core.analysis.gap_analyzer import GapAnalyzer
from backend.db.models import SkillFrequency


def make_row(skill_name: str, frequency_pct: float, category: str = "framework") -> SkillFrequency:
    return SkillFrequency(
        skill_name=skill_name,
        category=category,
        role_filter="all",
        week_start=__import__("datetime").date.today(),
        count=int(frequency_pct),
        total_postings=100,
        frequency_pct=frequency_pct,
        yoy_change_pct=None,
    )


def test_perfect_match_gives_high_score():
    result = GapAnalyzer().analyze(["PyTorch", "Docker"], [make_row("PyTorch", 50), make_row("Docker", 45)])
    assert result["gap_score"] > 80


def test_empty_resume_gives_low_score():
    result = GapAnalyzer().analyze([], [make_row("PyTorch", 50), make_row("Docker", 45)])
    assert result["gap_score"] < 10


def test_semantic_matching_catches_synonyms():
    assert GapAnalyzer().similarity("NLP", "Natural Language Processing") >= 0.75


def test_critical_gap_threshold():
    result = GapAnalyzer().analyze([], [make_row("PyTorch", 45)])
    assert result["gaps"][0]["status"] == "CRITICAL_GAP"


def test_strong_skill_classification():
    result = GapAnalyzer().analyze(["PyTorch"], [make_row("PyTorch", 45)])
    assert result["strengths"][0]["status"] == "STRONG"


def test_gap_score_range():
    result = GapAnalyzer().analyze(["PyTorch"], [make_row("PyTorch", 45), make_row("Docker", 45)])
    assert 0 <= result["gap_score"] <= 100


def test_cosine_similarity_computation():
    assert GapAnalyzer().similarity("PyTorch", "PyTorch") == 1.0


def test_adjacent_skill_classification():
    result = GapAnalyzer().analyze(["Docker"], [make_row("Kubernetes", 45, category="tool")])
    assert result["strengths"][0]["status"] == "ADJACENT"


def test_summary_counts_are_present():
    result = GapAnalyzer().analyze(
        ["PyTorch", "Docker"],
        [make_row("PyTorch", 45), make_row("Kubernetes", 35, category="tool")],
        target_role="ml_engineer",
    )
    assert result["summary"]["exact_matches"] >= 1
    assert "critical_gaps" in result["summary"]
    assert "core_skill_coverage_pct" in result["summary"]
    assert "category_coverage_pct" in result["summary"]
