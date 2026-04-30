"""Schemas for market skills endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class SkillFrequencyOut(BaseModel):
    """Serialized weekly skill aggregate."""

    skill_name: str
    category: str
    role_filter: str
    week_start: str
    count: int
    total_postings: int
    frequency_pct: float
    yoy_change_pct: float | None = None


class SkillVelocityOut(BaseModel):
    """Velocity view for a skill."""

    skill_name: str
    category: str
    current_frequency_pct: float
    velocity: float
    latest_week: str


class SkillTrendPoint(BaseModel):
    """Single weekly trend point."""

    week_start: str
    frequency_pct: float
    count: int
    total_postings: int


class SkillTrendResponse(BaseModel):
    """Trend details for one skill."""

    skill_name: str
    role_filter: str
    points: list[SkillTrendPoint]


class HeatmapResponse(BaseModel):
    """Heatmap matrix for skills by week."""

    skills: list[str]
    weeks: list[str]
    matrix: list[list[float]]


class MarketSummaryResponse(BaseModel):
    """High-level dashboard summary."""

    total_postings: int
    unique_skills: int
    top_skill: str | None
    fastest_rising: str | None
    data_freshness_week: str | None


class TrendingSkillsResponse(BaseModel):
    """Rising and declining skill sets."""

    rising: list[SkillVelocityOut]
    falling: list[SkillVelocityOut]
