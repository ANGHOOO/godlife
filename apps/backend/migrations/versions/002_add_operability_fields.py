"""Add operator visibility fields for manual review and webhook compatibility."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

from sqlalchemy.dialects import postgresql


revision = "002_add_operability_fields"
down_revision = "001_initial_persistence_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add fields used by runbook and operations."""
    op.add_column(
        "notifications",
        sa.Column("reason_code", sa.String(length=128)),
    )
    op.add_column(
        "notifications",
        sa.Column("provider_response_code", sa.String(length=64)),
    )
    op.add_column("notifications", sa.Column("failure_reason", sa.Text()))
    op.add_column("notifications", sa.Column("last_error_at", sa.DateTime(timezone=True)))
    op.add_column("notifications", sa.Column("memo", sa.Text()))
    op.add_column("notifications", sa.Column("reviewed_by", sa.String(length=120)))
    op.add_column("notifications", sa.Column("reviewed_at", sa.DateTime(timezone=True)))

    op.add_column(
        "webhook_events",
        sa.Column("schema_version", sa.String(length=16), nullable=False, server_default="v1"),
    )
    op.add_column("webhook_events", sa.Column("request_id", sa.String(length=255)))
    op.add_column("webhook_events", sa.Column("signature_state", sa.String(length=120)))
    op.add_column("webhook_events", sa.Column("reason_code", sa.String(length=128)))
    op.add_column("webhook_events", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.create_index("ix_webhook_events_signature_state", "webhook_events", ["signature_state"])
    op.create_index("ix_webhook_events_provider_schema", "webhook_events", ["provider", "schema_version"])

    op.create_table(
        "notification_provider_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("provider_status_code", sa.String(length=80), nullable=False),
        sa.Column("provider_response", sa.Text()),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_notification_provider_codes_notification_id", "notification_provider_codes", ["notification_id"])


def downgrade() -> None:
    """Rollback operator visibility columns."""
    op.drop_table("notification_provider_codes")
    op.drop_index("ix_webhook_events_signature_state", table_name="webhook_events")
    op.drop_index("ix_webhook_events_provider_schema", table_name="webhook_events")
    op.drop_column("webhook_events", "retry_count")
    op.drop_column("webhook_events", "reason_code")
    op.drop_column("webhook_events", "signature_state")
    op.drop_column("webhook_events", "request_id")
    op.drop_column("webhook_events", "schema_version")

    op.drop_column("notifications", "reviewed_at")
    op.drop_column("notifications", "reviewed_by")
    op.drop_column("notifications", "memo")
    op.drop_column("notifications", "last_error_at")
    op.drop_column("notifications", "failure_reason")
    op.drop_column("notifications", "provider_response_code")
    op.drop_column("notifications", "reason_code")

