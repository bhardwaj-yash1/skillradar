"""SQLAlchemy ORM models for SkillRadar."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base declarative model."""


class JobSource(str, enum.Enum):
    """Supported job data sources."""

    NAUKRI = "naukri"
    INDEED = "indeed"
    LINKEDIN = "linkedin"


class CompanyTier(str, enum.Enum):
    """Coarse company segmentation labels."""

    TIER1_MNC = "tier1_mnc"
    TIER2_MNC = "tier2_mnc"
    STARTUP_FUNDED = "startup_funded"
    STARTUP_EARLY = "startup_early"
    UNKNOWN = "unknown"


class SkillCategory(str, enum.Enum):
    """Skill taxonomy used throughout the app."""

    FRAMEWORK = "framework"
    LANGUAGE = "language"
    DOMAIN = "domain"
    TOOL = "tool"
    CONCEPT = "concept"
    CLOUD = "cloud"
    OTHER = "other"


class JobPosting(Base):
    """Raw job posting scraped from a source."""

    __tablename__ = "job_postings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source: Mapped[JobSource] = mapped_column(Enum(JobSource, native_enum=False), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    company_tier: Mapped[CompanyTier] = mapped_column(
        Enum(CompanyTier, native_enum=False),
        nullable=False,
        default=CompanyTier.UNKNOWN,
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    extracted_skills: Mapped[list["ExtractedSkill"]] = relationship(
        back_populates="job_posting",
        cascade="all, delete-orphan",
    )


class ExtractedSkill(Base):
    """Structured skill extracted from a job posting."""

    __tablename__ = "extracted_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_posting_id: Mapped[str] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    skill_raw: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory, native_enum=False), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extraction_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    job_posting: Mapped[JobPosting] = relationship(back_populates="extracted_skills")


class SkillFrequency(Base):
    """Weekly aggregated skill frequency data."""

    __tablename__ = "skill_frequencies"
    __table_args__ = (UniqueConstraint("skill_name", "role_filter", "week_start", name="uq_skill_role_week"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    role_filter: Mapped[str] = mapped_column(String(100), nullable=False, default="all")
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_postings: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency_pct: Mapped[float] = mapped_column(Float, nullable=False)
    yoy_change_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class UserSubscription(Base):
    """Email subscription record for weekly digests."""

    __tablename__ = "user_subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role_filter: Mapped[str] = mapped_column(String(100), nullable=False, default="all")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    subscribed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_digest_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    unsubscribe_token: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        default=lambda: str(uuid.uuid4()),
    )


class ResumeAnalysis(Base):
    """Persisted resume analysis and roadmap output."""

    __tablename__ = "resume_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    target_role: Mapped[str] = mapped_column(String(100), nullable=False)
    gap_analysis: Mapped[dict] = mapped_column(JSON, nullable=False)
    roadmap: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
