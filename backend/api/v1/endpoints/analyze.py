"""Resume and manual skill analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.schemas.analyze import ManualSkillsAnalysisRequest, ResumeAnalysisResponse
from backend.config import Settings
from backend.core.analysis.gap_analyzer import GapAnalyzer
from backend.core.analysis.resume_parser import ResumeParser
from backend.db import crud
from backend.db.models import ResumeAnalysis, SkillFrequency
from backend.dependencies import get_app_settings, get_db

router = APIRouter()


def _serialize_analysis(analysis: ResumeAnalysis) -> ResumeAnalysisResponse:
    gap_payload = analysis.gap_analysis
    return ResumeAnalysisResponse(
        analysis_id=analysis.id,
        session_id=analysis.session_id,
        filename=analysis.filename,
        target_role=analysis.target_role,
        extracted_skills=analysis.extracted_skills,
        gap_score=gap_payload["gap_score"],
        fit_label=gap_payload["fit_label"],
        summary=gap_payload["summary"],
        strengths=gap_payload["strengths"],
        gaps=gap_payload["gaps"],
    )


async def _load_market_snapshot(db: AsyncSession, target_role: str) -> list[SkillFrequency]:
    """Load the latest role-specific benchmark, falling back to all roles when needed."""
    latest_week = await crud.get_latest_week(db)
    if latest_week is None:
        return []

    rows = await crud.get_top_skills(db, target_role, latest_week, limit=18)
    if rows:
        return rows
    return await crud.get_top_skills(db, "all", latest_week, limit=18)


@router.post("/resume", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    session_id: str = Form(...),
    target_role: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> ResumeAnalysisResponse:
    """Analyze an uploaded resume."""
    content = await file.read()
    parser = ResumeParser(settings)
    try:
        parsed = parser.parse_bytes(file.filename or "resume.pdf", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    rows = await _load_market_snapshot(db, target_role)
    gap_result = GapAnalyzer().analyze(parsed["skills"], list(rows), target_role=target_role)
    analysis = await crud.create_resume_analysis(
        db,
        {
            "session_id": session_id,
            "filename": file.filename or "resume.pdf",
            "extracted_skills": parsed["skills"],
            "target_role": target_role,
            "gap_analysis": gap_result,
            "roadmap": None,
        },
    )
    return _serialize_analysis(analysis)


@router.post("/skills", response_model=ResumeAnalysisResponse)
async def analyze_skills(
    payload: ManualSkillsAnalysisRequest,
    db: AsyncSession = Depends(get_db),
) -> ResumeAnalysisResponse:
    """Analyze manually provided skills."""
    rows = await _load_market_snapshot(db, payload.target_role)
    gap_result = GapAnalyzer().analyze(payload.skills, list(rows), target_role=payload.target_role)
    analysis = await crud.create_resume_analysis(
        db,
        {
            "session_id": payload.session_id,
            "filename": "manual_input.txt",
            "extracted_skills": payload.skills,
            "target_role": payload.target_role,
            "gap_analysis": gap_result,
            "roadmap": None,
        },
    )
    return _serialize_analysis(analysis)
