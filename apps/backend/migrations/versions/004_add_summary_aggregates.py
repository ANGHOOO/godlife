"""Add daily/weekly summary aggregate tables for GOD-42."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "004_add_summary_aggregates"
down_revision = "003_god38_schema_alignment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create summary snapshot tables and indexes."""
    op.create_table(
        "daily_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("summary_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column(
            "exercise_total_sets", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "exercise_done_sets", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "exercise_completion_rate",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "reading_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trend", sa.String(length=16), nullable=False, server_default="flat"),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint(
            "user_id", "summary_date", name="uq_daily_summaries_user_date"
        ),
    )
    op.create_index(
        "ix_daily_summaries_user_date",
        "daily_summaries",
        ["user_id", "summary_date"],
    )

    op.create_table(
        "weekly_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column(
            "daily_points", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "week_avg_completion_rate",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trend", sa.String(length=16), nullable=False, server_default="flat"),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint(
            "user_id", "start_date", name="uq_weekly_summaries_user_start"
        ),
    )
    op.create_index(
        "ix_weekly_summaries_user_start",
        "weekly_summaries",
        ["user_id", "start_date"],
    )


def downgrade() -> None:
    """Drop summary snapshot tables and indexes."""
    op.drop_index("ix_weekly_summaries_user_start", table_name="weekly_summaries")
    op.drop_table("weekly_summaries")

    op.drop_index("ix_daily_summaries_user_date", table_name="daily_summaries")
    op.drop_table("daily_summaries")
