"""Schemas for resume analysis endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ManualSkillsAnalysisRequest(BaseModel):
    """Request body for text-based skill analysis."""

    session_id: str
    target_role: str = "ml_engineer"
    skills: list[str] = Field(default_factory=list)


class SkillGapItem(BaseModel):
    """One skill in the gap analysis output."""

    skill_name: str
    category: str
    market_frequency_pct: float
    similarity_score: float
    status: str
    reason: str


class AnalysisSummary(BaseModel):
    """Small summary block for gap analysis quality."""

    resume_skill_count: int
    market_skill_count: int
    exact_matches: int
    adjacent_matches: int
    critical_gaps: int


class ResumeAnalysisResponse(BaseModel):
    """Stored resume analysis payload."""

    analysis_id: str
    session_id: str
    filename: str
    target_role: str
    extracted_skills: list[str]
    gap_score: float
    fit_label: str
    summary: AnalysisSummary
    strengths: list[SkillGapItem]
    gaps: list[SkillGapItem]
