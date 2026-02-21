"""persistence schema initial."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "001_initial_persistence_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create baseline domain tables for users, exercise,
    reading, messaging, webhook, outbox.
    """
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kakao_user_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "timezone",
            sa.String(length=80),
            nullable=False,
            server_default="Asia/Seoul",
        ),
        sa.Column(
            "status", sa.String(length=32), nullable=False, server_default="ACTIVE"
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
    )
    op.create_index("ix_users_kakao_user_id", "users", ["kakao_user_id"])

    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("age", sa.Integer()),
        sa.Column("height_cm", sa.Integer()),
        sa.Column("weight_kg", sa.Integer()),
        sa.Column("goal", sa.String(length=80)),
        sa.Column("experience_level", sa.String(length=80)),
        sa.Column("max_daily_minutes", sa.Integer()),
        sa.Column("available_equipment", sa.Text()),
        sa.Column("injury_notes", sa.Text()),
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
        sa.UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
    )

    op.create_table(
        "exercise_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column(
            "status", sa.String(length=32), nullable=False, server_default="DRAFT"
        ),
        sa.Column("summary", sa.Text()),
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
    )
    op.create_index(
        "ix_exercise_plans_target_date_status",
        "exercise_plans",
        ["target_date", "status"],
    )
    op.create_index(
        "ix_exercise_plans_user_id_target_date",
        "exercise_plans",
        ["user_id", "target_date"],
    )
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX uq_exercise_plans_user_target_date_active
            ON exercise_plans (user_id, target_date)
            WHERE status = 'ACTIVE'
            """
        )
    )

    op.create_table(
        "exercise_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_plans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.Column("exercise_name", sa.String(length=120), nullable=False),
        sa.Column("body_part", sa.String(length=120)),
        sa.Column("target_sets", sa.Integer(), nullable=False),
        sa.Column("target_reps", sa.Integer()),
        sa.Column("target_weight_kg", sa.Integer()),
        sa.Column("target_rest_sec", sa.Integer()),
        sa.Column("notes", sa.Text()),
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
    )

    op.create_table(
        "exercise_set_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("set_no", sa.Integer(), nullable=False),
        sa.Column(
            "status", sa.String(length=32), nullable=False, server_default="PENDING"
        ),
        sa.Column("performed_reps", sa.Integer()),
        sa.Column("performed_weight_kg", sa.Integer()),
        sa.Column("actual_rest_sec", sa.Integer()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("skipped_at", sa.DateTime(timezone=True)),
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
            "session_id", "set_no", name="uq_exercise_set_states_session_set_no"
        ),
    )
    op.create_index(
        "ix_exercise_set_states_session_id", "exercise_set_states", ["session_id"]
    )
    op.create_index("ix_exercise_set_states_status", "exercise_set_states", ["status"])

    op.create_table(
        "reading_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("remind_time", sa.Time(), nullable=False),
        sa.Column("goal_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column(
            "enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")
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
    )

    op.create_table(
        "reading_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "reading_plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reading_plans.id", ondelete="SET NULL"),
        ),
        sa.Column("book_title", sa.String(length=255)),
        sa.Column("start_at", sa.DateTime(timezone=True)),
        sa.Column("end_at", sa.DateTime(timezone=True)),
        sa.Column("pages_read", sa.Integer()),
        sa.Column("status", sa.String(length=32), nullable=False),
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
    )
    op.create_index(
        "ix_reading_logs_user_created_at", "reading_logs", ["user_id", "created_at"]
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=80), nullable=False),
        sa.Column("related_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "status", sa.String(length=32), nullable=False, server_default="SCHEDULED"
        ),
        sa.Column("schedule_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "idempotency_key", sa.String(length=255), nullable=False, unique=True
        ),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("provider_msg_id", sa.String(length=255)),
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
        sa.CheckConstraint(
            "retry_count >= 0", name="ck_notifications_retry_count_non_negative"
        ),
    )
    op.create_index(
        "ix_notifications_user_status_schedule",
        "notifications",
        ["user_id", "status", "schedule_at"],
    )

    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
        ),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("event_id", sa.String(length=255)),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
        sa.Column(
            "processed", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint(
            "provider", "idempotency_key", name="uq_webhook_events_provider_idempotency"
        ),
    )
    op.create_index(
        "ix_webhook_events_processed_created",
        "webhook_events",
        ["processed", "created_at"],
    )
    op.create_index(
        "ix_webhook_events_provider_event_id",
        "webhook_events",
        ["provider", "event_id"],
        unique=True,
    )

    op.create_table(
        "outbox_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column(
            "status", sa.String(length=32), nullable=False, server_default="PENDING"
        ),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
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
        sa.CheckConstraint(
            "retry_count >= 0", name="ck_outbox_retry_count_non_negative"
        ),
    )
    op.create_index(
        "ix_outbox_events_status_retry", "outbox_events", ["status", "retry_count"]
    )


def downgrade() -> None:
    """Rollback baseline schema."""
    op.drop_table("outbox_events")
    op.drop_table("webhook_events")
    op.drop_table("notifications")
    op.drop_table("reading_logs")
    op.drop_table("reading_plans")
    op.drop_table("exercise_set_states")
    op.drop_table("exercise_sessions")
    op.drop_table("exercise_plans")
    op.drop_table("user_profiles")
    op.drop_table("users")
