"""Align exercise weight columns with runtime float contract for GOD-33."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005_god33_weight_columns_float"
down_revision = "004_add_summary_aggregates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Change exercise weight columns from Integer to Float."""
    op.alter_column(
        "exercise_sessions",
        "target_weight_kg",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=True,
    )
    op.alter_column(
        "exercise_set_states",
        "performed_weight_kg",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Rollback exercise weight columns to Integer."""
    op.alter_column(
        "exercise_set_states",
        "performed_weight_kg",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
    op.alter_column(
        "exercise_sessions",
        "target_weight_kg",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
