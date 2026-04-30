"""Async scheduler bootstrap and jobs."""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from backend.config import Settings
from backend.core.analysis.trend_analyzer import TrendAnalyzer
from backend.core.notifications.digest_builder import DigestBuilder
from backend.core.notifications.email_service import EmailService
from backend.core.scraper.scraper_manager import ScraperManager
from backend.db import crud
from backend.db.database import AsyncSessionLocal
from backend.db.models import ExtractedSkill, JobPosting, SkillFrequency
from backend.utils.logging_config import get_logger

WEEKDAY_TO_CRON = {
    "monday": "mon",
    "tuesday": "tue",
    "wednesday": "wed",
    "thursday": "thu",
    "friday": "fri",
    "saturday": "sat",
    "sunday": "sun",
}


class JobSchedulerService:
    """Manage recurring scrape, aggregation, and digest jobs."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.scraper_manager = ScraperManager(settings)
        self.trend_analyzer = TrendAnalyzer()
        self.email_service = EmailService(settings)
        self.digest_builder = DigestBuilder()

    def start(self) -> None:
        """Register jobs and start the scheduler."""
        if self.scheduler.running:
            return
        scrape_day = WEEKDAY_TO_CRON.get(self.settings.WEEKLY_SCRAPE_DAY, self.settings.WEEKLY_SCRAPE_DAY)
        digest_day = WEEKDAY_TO_CRON.get(self.settings.WEEKLY_DIGEST_DAY, self.settings.WEEKLY_DIGEST_DAY)
        self.scheduler.add_job(
            self.run_weekly_scrape,
            "cron",
            day_of_week=scrape_day,
            hour=self.settings.WEEKLY_SCRAPE_HOUR,
            id="weekly_scrape",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.refresh_weekly_skill_frequencies,
            "cron",
            day_of_week=scrape_day,
            hour=max(0, self.settings.WEEKLY_SCRAPE_HOUR + 1),
            id="weekly_aggregation",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.send_weekly_digests,
            "cron",
            day_of_week=digest_day,
            hour=self.settings.WEEKLY_DIGEST_HOUR,
            id="weekly_digest",
            replace_existing=True,
        )
        self.scheduler.start()
        self.logger.info("scheduler_started", jobs=len(self.scheduler.get_jobs()))

    async def shutdown(self) -> None:
        """Stop the scheduler cleanly."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.logger.info("scheduler_stopped")

    async def run_weekly_scrape(self) -> None:
        """Run the default weekly scrape."""
        async with AsyncSessionLocal() as session:
            await self.scraper_manager.run_scrape_pipeline(
                session,
                role="machine learning engineer",
                location="india",
                max_results=self.settings.MAX_JDS_PER_SCRAPE_RUN,
            )

    async def refresh_weekly_skill_frequencies(self) -> None:
        """Aggregate extracted skills into weekly frequency snapshots."""
        async with AsyncSessionLocal() as session:
            postings = (await session.execute(select(JobPosting))).scalars().all()
            skills = (await session.execute(select(ExtractedSkill))).scalars().all()
            if not postings or not skills:
                return
            total_postings = len(postings)
            latest_week = max(posting.scraped_at.date() for posting in postings)
            monday = latest_week.fromordinal(latest_week.toordinal() - latest_week.weekday())
            grouped: dict[tuple[str, str], int] = {}
            for skill in skills:
                key = (skill.skill_name, skill.category.value if hasattr(skill.category, "value") else str(skill.category))
                grouped[key] = grouped.get(key, 0) + 1
            for (skill_name, category), count in grouped.items():
                await crud.upsert_skill_frequency(
                    session,
                    {
                        "skill_name": skill_name,
                        "category": category,
                        "role_filter": "all",
                        "week_start": monday,
                        "count": count,
                        "total_postings": total_postings,
                        "frequency_pct": round((count / total_postings) * 100, 2),
                        "yoy_change_pct": None,
                    },
                )

    async def send_weekly_digests(self) -> None:
        """Send digest emails to active subscribers."""
        async with AsyncSessionLocal() as session:
            subscriptions = await crud.get_active_subscriptions(session)
            rows = (await session.execute(select(SkillFrequency))).scalars().all()
            summary = self.trend_analyzer.market_summary(list(rows))
            rising = await crud.get_trending_skills(session, "all", limit=5)
            falling = await crud.get_declining_skills(session, "all", limit=5)
            for subscription in subscriptions:
                html = self.digest_builder.build(subscription.role_filter, summary, rising, falling)
                await self.email_service.send_email(
                    subscription.email,
                    self.settings.EMAIL_DIGEST_SUBJECT,
                    html,
                )

    def get_job_statuses(self) -> list[dict]:
        """Return scheduler status for API consumers."""
        return [
            {
                "id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in self.scheduler.get_jobs()
        ]
