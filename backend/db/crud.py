"""Async CRUD helpers."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import ExtractedSkill, JobPosting, ResumeAnalysis, SkillFrequency, UserSubscription


async def create_job_posting(db: AsyncSession, data: dict) -> JobPosting:
    """Persist a raw job posting."""
    posting = JobPosting(**data)
    db.add(posting)
    await db.commit()
    await db.refresh(posting)
    return posting


async def get_job_posting_by_external_id(
    db: AsyncSession,
    external_id: str,
    source: str,
) -> JobPosting | None:
    """Look up a posting by source-specific identifier."""
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.external_id == external_id,
            JobPosting.source == source,
        )
    )
    return result.scalar_one_or_none()


async def get_unprocessed_postings(db: AsyncSession, limit: int = 50) -> list[JobPosting]:
    """Return job postings pending extraction."""
    result = await db.execute(
        select(JobPosting)
        .where(JobPosting.is_processed.is_(False))
        .order_by(JobPosting.scraped_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def mark_posting_processed(db: AsyncSession, posting_id: str, processed_at: datetime) -> None:
    """Mark a posting as extracted."""
    posting = await db.get(JobPosting, posting_id)
    if posting is None:
        return
    posting.is_processed = True
    posting.processed_at = processed_at
    await db.commit()


async def get_postings_count_by_source(db: AsyncSession) -> dict[str, int]:
    """Count postings grouped by source."""
    result = await db.execute(select(JobPosting.source, func.count(JobPosting.id)).group_by(JobPosting.source))
    return {str(source.value if hasattr(source, "value") else source): count for source, count in result.all()}


async def bulk_create_skills(db: AsyncSession, skills: list[dict]) -> int:
    """Insert extracted skills in bulk."""
    objects = [ExtractedSkill(**skill) for skill in skills]
    db.add_all(objects)
    await db.commit()
    return len(objects)


async def get_skills_by_posting(db: AsyncSession, posting_id: str) -> list[ExtractedSkill]:
    """Return skills attached to one job posting."""
    result = await db.execute(
        select(ExtractedSkill)
        .where(ExtractedSkill.job_posting_id == posting_id)
        .order_by(ExtractedSkill.skill_name.asc())
    )
    return list(result.scalars().all())


async def upsert_skill_frequency(db: AsyncSession, data: dict) -> SkillFrequency:
    """Upsert a weekly skill frequency record."""
    dialect_name = db.bind.dialect.name if db.bind else ""
    if dialect_name == "postgresql":
        stmt = pg_insert(SkillFrequency).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["skill_name", "role_filter", "week_start"],
            set_={
                "category": data["category"],
                "count": data["count"],
                "total_postings": data["total_postings"],
                "frequency_pct": data["frequency_pct"],
                "yoy_change_pct": data.get("yoy_change_pct"),
            },
        )
        await db.execute(stmt)
        await db.commit()
    else:
        existing = await db.execute(
            select(SkillFrequency).where(
                SkillFrequency.skill_name == data["skill_name"],
                SkillFrequency.role_filter == data["role_filter"],
                SkillFrequency.week_start == data["week_start"],
            )
        )
        record = existing.scalar_one_or_none()
        if record:
            for key, value in data.items():
                setattr(record, key, value)
        else:
            record = SkillFrequency(**data)
            db.add(record)
        await db.commit()

    refreshed = await db.execute(
        select(SkillFrequency).where(
            SkillFrequency.skill_name == data["skill_name"],
            SkillFrequency.role_filter == data["role_filter"],
            SkillFrequency.week_start == data["week_start"],
        )
    )
    return refreshed.scalar_one()


async def get_top_skills(
    db: AsyncSession,
    role_filter: str,
    week_start: date,
    limit: int = 50,
) -> list[SkillFrequency]:
    """Return the top skills for a role and week."""
    result = await db.execute(
        select(SkillFrequency)
        .where(SkillFrequency.role_filter == role_filter, SkillFrequency.week_start == week_start)
        .order_by(SkillFrequency.frequency_pct.desc(), SkillFrequency.count.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_skill_trend(
    db: AsyncSession,
    skill_name: str,
    role_filter: str,
    weeks: int = 12,
) -> list[SkillFrequency]:
    """Return recent weekly trend data for a skill."""
    result = await db.execute(
        select(SkillFrequency)
        .where(SkillFrequency.skill_name == skill_name, SkillFrequency.role_filter == role_filter)
        .order_by(SkillFrequency.week_start.asc())
        .limit(weeks)
    )
    return list(result.scalars().all())


async def _compute_velocity_rows(db: AsyncSession, role_filter: str) -> list[dict]:
    result = await db.execute(
        select(
            SkillFrequency.skill_name,
            SkillFrequency.category,
            SkillFrequency.week_start,
            SkillFrequency.frequency_pct,
        )
        .where(SkillFrequency.role_filter == role_filter)
        .order_by(SkillFrequency.skill_name.asc(), SkillFrequency.week_start.asc())
    )
    grouped: dict[str, list[tuple[str, date, float]]] = defaultdict(list)
    for skill_name, category, week_start, frequency_pct in result.all():
        grouped[skill_name].append((category, week_start, frequency_pct))

    rows: list[dict] = []
    for skill_name, points in grouped.items():
        if len(points) < 2:
            continue
        first = points[0][2]
        last = points[-1][2]
        rows.append(
            {
                "skill_name": skill_name,
                "category": points[-1][0],
                "current_frequency_pct": last,
                "velocity": round(last - first, 2),
                "latest_week": points[-1][1].isoformat(),
            }
        )
    return rows


async def get_trending_skills(db: AsyncSession, role_filter: str, limit: int = 20) -> list[dict]:
    """Return the fastest rising skills."""
    rows = await _compute_velocity_rows(db, role_filter)
    return sorted(rows, key=lambda row: row["velocity"], reverse=True)[:limit]


async def get_declining_skills(db: AsyncSession, role_filter: str, limit: int = 10) -> list[dict]:
    """Return the fastest falling skills."""
    rows = await _compute_velocity_rows(db, role_filter)
    return sorted(rows, key=lambda row: row["velocity"])[:limit]


async def create_subscription(
    db: AsyncSession,
    email: str,
    name: str | None,
    role_filter: str,
) -> UserSubscription:
    """Create a subscription or reactivate an existing one."""
    existing = await get_subscription_by_email(db, email)
    if existing:
        existing.is_active = True
        existing.name = name
        existing.role_filter = role_filter
        await db.commit()
        await db.refresh(existing)
        return existing

    subscription = UserSubscription(email=email, name=name, role_filter=role_filter)
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return subscription


async def get_subscription_by_email(db: AsyncSession, email: str) -> UserSubscription | None:
    """Look up a subscription by email."""
    result = await db.execute(select(UserSubscription).where(UserSubscription.email == email))
    return result.scalar_one_or_none()


async def get_active_subscriptions(db: AsyncSession) -> list[UserSubscription]:
    """Return all active subscriptions."""
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.is_active.is_(True))
        .order_by(UserSubscription.subscribed_at.asc())
    )
    return list(result.scalars().all())


async def deactivate_subscription(db: AsyncSession, unsubscribe_token: str) -> bool:
    """Deactivate a subscription using its one-click unsubscribe token."""
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.unsubscribe_token == unsubscribe_token)
    )
    subscription = result.scalar_one_or_none()
    if subscription is None or not subscription.is_active:
        return False
    subscription.is_active = False
    await db.commit()
    return True


async def create_resume_analysis(db: AsyncSession, data: dict) -> ResumeAnalysis:
    """Persist a resume analysis result."""
    analysis = ResumeAnalysis(**data)
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis


async def get_analysis_by_session(db: AsyncSession, session_id: str) -> list[ResumeAnalysis]:
    """Return all resume analyses for a browser session."""
    result = await db.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.session_id == session_id)
        .order_by(ResumeAnalysis.created_at.desc())
    )
    return list(result.scalars().all())
