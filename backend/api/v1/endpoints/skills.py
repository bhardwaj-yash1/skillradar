"""Skills analytics endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.schemas.skills import (
    HeatmapResponse,
    MarketSummaryResponse,
    SkillFrequencyOut,
    SkillTrendPoint,
    SkillTrendResponse,
    SkillVelocityOut,
    TrendingSkillsResponse,
)
from backend.core.analysis.trend_analyzer import TrendAnalyzer
from backend.db import crud
from backend.db.models import SkillFrequency
from backend.dependencies import get_db

router = APIRouter()


def _serialize_frequency(row: SkillFrequency) -> SkillFrequencyOut:
    return SkillFrequencyOut(
        skill_name=row.skill_name,
        category=row.category,
        role_filter=row.role_filter,
        week_start=row.week_start.isoformat(),
        count=row.count,
        total_postings=row.total_postings,
        frequency_pct=row.frequency_pct,
        yoy_change_pct=row.yoy_change_pct,
    )


@router.get("/top", response_model=list[SkillFrequencyOut])
async def top_skills(
    role_filter: str = Query(default="all"),
    week_start: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[SkillFrequencyOut]:
    """Return top skills for a role and week."""
    if week_start is None:
        weeks = await db.execute(select(SkillFrequency.week_start).order_by(SkillFrequency.week_start.desc()))
        latest = weeks.scalars().first()
        if latest is None:
            return []
        parsed_week = latest
    else:
        parsed_week = date.fromisoformat(week_start)
    rows = await crud.get_top_skills(db, role_filter, parsed_week, limit)
    return [_serialize_frequency(row) for row in rows]


@router.get("/trend/{skill_name}", response_model=SkillTrendResponse)
async def skill_trend(
    skill_name: str,
    role_filter: str = Query(default="all"),
    weeks: int = Query(default=12, ge=1, le=52),
    db: AsyncSession = Depends(get_db),
) -> SkillTrendResponse:
    """Return trend details for one skill."""
    rows = await crud.get_skill_trend(db, skill_name, role_filter, weeks)
    return SkillTrendResponse(
        skill_name=skill_name,
        role_filter=role_filter,
        points=[
            SkillTrendPoint(
                week_start=row.week_start.isoformat(),
                frequency_pct=row.frequency_pct,
                count=row.count,
                total_postings=row.total_postings,
            )
            for row in rows
        ],
    )


@router.get("/heatmap", response_model=HeatmapResponse)
async def heatmap(
    role_filter: str = Query(default="all"),
    db: AsyncSession = Depends(get_db),
) -> HeatmapResponse:
    """Return heatmap data for the dashboard."""
    rows = (
        await db.execute(
            select(SkillFrequency).where(SkillFrequency.role_filter == role_filter).order_by(SkillFrequency.week_start.asc())
        )
    ).scalars().all()
    payload = TrendAnalyzer().heatmap(list(rows))
    return HeatmapResponse(**payload)


@router.get("/summary", response_model=MarketSummaryResponse)
async def market_summary(
    role_filter: str = Query(default="all"),
    db: AsyncSession = Depends(get_db),
) -> MarketSummaryResponse:
    """Return top-level market summary cards."""
    rows = (
        await db.execute(
            select(SkillFrequency).where(SkillFrequency.role_filter == role_filter).order_by(SkillFrequency.week_start.asc())
        )
    ).scalars().all()
    return MarketSummaryResponse(**TrendAnalyzer().market_summary(list(rows)))


@router.get("/trending", response_model=TrendingSkillsResponse)
async def trending(
    role_filter: str = Query(default="all"),
    db: AsyncSession = Depends(get_db),
) -> TrendingSkillsResponse:
    """Return rising and falling skills."""
    rising = [SkillVelocityOut(**item) for item in await crud.get_trending_skills(db, role_filter)]
    falling = [SkillVelocityOut(**item) for item in await crud.get_declining_skills(db, role_filter)]
    return TrendingSkillsResponse(rising=rising, falling=falling)
