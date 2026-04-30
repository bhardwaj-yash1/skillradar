"""Schemas for scrape endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScrapeTriggerRequest(BaseModel):
    """Payload for starting a scrape run."""

    role: str = "machine learning engineer"
    location: str = "india"
    max_results: int = Field(default=20, ge=1, le=100)
    sources: list[str] | None = None


class ScrapeTriggerResponse(BaseModel):
    """Accepted scrape job response."""

    status: str
    message: str
    scraped: int = 0
    new_postings: int = 0
    extracted_skills: int = 0


class SchedulerJobInfo(BaseModel):
    """One scheduler job description."""

    id: str
    next_run_time: str | None
    trigger: str


class ScrapeStatusResponse(BaseModel):
    """Current scrape and scheduler status."""

    posting_counts: dict[str, int]
    scheduler_jobs: list[SchedulerJobInfo]
