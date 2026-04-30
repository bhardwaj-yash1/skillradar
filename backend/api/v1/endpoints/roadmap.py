"""Learning roadmap endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.schemas.roadmap import RoadmapResponse
from backend.core.roadmap.roadmap_generator import RoadmapGenerator
from backend.db.models import ResumeAnalysis
from backend.dependencies import get_db

router = APIRouter()


@router.post("/{analysis_id}", response_model=RoadmapResponse)
async def generate_roadmap(
    analysis_id: str,
    total_weeks: int = Query(default=12, ge=4, le=26),
    db: AsyncSession = Depends(get_db),
) -> RoadmapResponse:
    """Generate a learning roadmap from a prior analysis."""
    analysis = await db.get(ResumeAnalysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    roadmap = RoadmapGenerator().generate(
        analysis_id=analysis.id,
        target_role=analysis.target_role,
        gaps=analysis.gap_analysis.get("gaps", []),
        strengths=analysis.gap_analysis.get("strengths", []),
        total_weeks=total_weeks,
    )
    analysis.roadmap = roadmap
    await db.commit()
    return RoadmapResponse(**roadmap)
