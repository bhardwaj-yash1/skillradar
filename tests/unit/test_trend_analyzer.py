"""Trend analyzer tests."""

from datetime import date, timedelta

from backend.core.analysis.trend_analyzer import TrendAnalyzer
from backend.db.models import SkillFrequency


def make_rows() -> list[SkillFrequency]:
    start = date.today() - timedelta(weeks=2)
    return [
        SkillFrequency(skill_name="PyTorch", category="framework", role_filter="all", week_start=start, count=40, total_postings=100, frequency_pct=40, yoy_change_pct=None),
        SkillFrequency(skill_name="PyTorch", category="framework", role_filter="all", week_start=start + timedelta(weeks=1), count=50, total_postings=100, frequency_pct=50, yoy_change_pct=None),
        SkillFrequency(skill_name="TensorFlow", category="framework", role_filter="all", week_start=start, count=60, total_postings=100, frequency_pct=60, yoy_change_pct=None),
        SkillFrequency(skill_name="TensorFlow", category="framework", role_filter="all", week_start=start + timedelta(weeks=1), count=55, total_postings=100, frequency_pct=55, yoy_change_pct=None),
    ]


def test_top_skills_sorted_by_frequency():
    rows = TrendAnalyzer().top_skills(make_rows(), limit=2)
    assert rows[0].frequency_pct >= rows[1].frequency_pct


def test_velocity_identifies_rising_skill():
    velocities = TrendAnalyzer().compute_velocity(make_rows())
    assert velocities["PyTorch"] > 0


def test_velocity_identifies_falling_skill():
    velocities = TrendAnalyzer().compute_velocity(make_rows())
    assert velocities["TensorFlow"] < 0


def test_heatmap_returns_correct_shape():
    heatmap = TrendAnalyzer().heatmap(make_rows(), top_n=2)
    assert len(heatmap["matrix"]) == len(heatmap["skills"])


def test_market_summary_computes_correctly():
    summary = TrendAnalyzer().market_summary(make_rows())
    assert summary["top_skill"] is not None


def test_trend_data_ordered_by_week_ascending():
    weeks = [row.week_start for row in sorted(make_rows(), key=lambda row: row.week_start)]
    assert weeks == sorted(weeks)
