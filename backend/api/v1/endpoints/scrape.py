"""Scrape trigger and status endpoints."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.schemas.scrape import ScrapeStatusResponse, ScrapeTriggerRequest, ScrapeTriggerResponse
from backend.config import Settings
from backend.core.scheduler.job_scheduler import JobSchedulerService
from backend.core.scraper.scraper_manager import ScraperManager
from backend.db import crud
from backend.dependencies import get_app_settings, get_db

router = APIRouter()
SCRAPE_LOCK = asyncio.Lock()
_scheduler_service: JobSchedulerService | None = None


def set_scheduler_service(service: JobSchedulerService) -> None:
    """Attach the singleton scheduler service."""
    global _scheduler_service
    _scheduler_service = service


@router.post("/trigger", response_model=ScrapeTriggerResponse, status_code=202)
async def trigger_scrape(
    payload: ScrapeTriggerRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> ScrapeTriggerResponse:
    """Start a new scrape run if one is not already active."""
    try:
        await asyncio.wait_for(SCRAPE_LOCK.acquire(), timeout=1)
    except TimeoutError as exc:
        raise HTTPException(status_code=409, detail="already_running") from exc

    manager = ScraperManager(settings)
    try:
        result = await manager.run_scrape_pipeline(
            db,
            role=payload.role,
            location=payload.location,
            max_results=min(payload.max_results, settings.MAX_JDS_PER_SCRAPE_RUN),
            sources=payload.sources,
        )
        return ScrapeTriggerResponse(status="accepted", message="scrape completed", **result)
    finally:
        SCRAPE_LOCK.release()


@router.get("/status", response_model=ScrapeStatusResponse)
async def scrape_status(db: AsyncSession = Depends(get_db)) -> ScrapeStatusResponse:
    """Return posting counts and scheduler metadata."""
    counts = await crud.get_postings_count_by_source(db)
    jobs = _scheduler_service.get_job_statuses() if _scheduler_service else []
    return ScrapeStatusResponse(posting_counts=counts, scheduler_jobs=jobs)


@router.get("/jobs")
async def scheduler_jobs() -> list[dict]:
    """Return raw scheduler job status."""
    return _scheduler_service.get_job_statuses() if _scheduler_service else []
