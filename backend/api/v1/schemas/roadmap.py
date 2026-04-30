"""Schemas for roadmap endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class LearningResource(BaseModel):
    """One suggested resource."""

    title: str
    url: str
    provider: str


class RoadmapSkillStep(BaseModel):
    """One skill recommendation inside a roadmap phase."""

    skill_name: str
    category: str
    market_frequency_pct: float
    estimated_weeks: int
    free_resource: LearningResource
    paid_resource: LearningResource
    project_idea: str
    why_important: str


class RoadmapPhase(BaseModel):
    """A grouped phase of learning tasks."""

    phase_title: str
    week_range: str
    skills: list[RoadmapSkillStep]


class RoadmapResponse(BaseModel):
    """Roadmap generation response."""

    analysis_id: str
    target_role: str
    total_weeks: int
    phases: list[RoadmapPhase]
