"""Initial schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all primary application tables."""
    op.create_table(
        "job_postings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=9), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("company_tier", sa.String(length=20), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("experience_min", sa.Integer(), nullable=True),
        sa.Column("experience_max", sa.Integer(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("is_processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_job_postings_source_processed", "job_postings", ["source", "is_processed"])

    op.create_table(
        "extracted_skills",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("job_posting_id", sa.String(length=36), sa.ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_name", sa.String(length=255), nullable=False),
        sa.Column("skill_raw", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_extracted_skills_posting", "extracted_skills", ["job_posting_id"])

    op.create_table(
        "skill_frequencies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("skill_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("role_filter", sa.String(length=100), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("total_postings", sa.Integer(), nullable=False),
        sa.Column("frequency_pct", sa.Float(), nullable=False),
        sa.Column("yoy_change_pct", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("skill_name", "role_filter", "week_start", name="uq_skill_role_week"),
    )
    op.create_index("ix_skill_frequencies_skill_week", "skill_frequencies", ["skill_name", "week_start"])

    op.create_table(
        "user_subscriptions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("role_filter", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("subscribed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_digest_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsubscribe_token", sa.String(length=36), nullable=False),
    )
    op.create_index("ix_user_subscriptions_email", "user_subscriptions", ["email"], unique=True)

    op.create_table(
        "resume_analyses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("extracted_skills", sa.JSON(), nullable=False),
        sa.Column("target_role", sa.String(length=100), nullable=False),
        sa.Column("gap_analysis", sa.JSON(), nullable=False),
        sa.Column("roadmap", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Drop all application tables."""
    op.drop_table("resume_analyses")
    op.drop_index("ix_user_subscriptions_email", table_name="user_subscriptions")
    op.drop_table("user_subscriptions")
    op.drop_index("ix_skill_frequencies_skill_week", table_name="skill_frequencies")
    op.drop_table("skill_frequencies")
    op.drop_index("ix_extracted_skills_posting", table_name="extracted_skills")
    op.drop_table("extracted_skills")
    op.drop_index("ix_job_postings_source_processed", table_name="job_postings")
    op.drop_table("job_postings")
