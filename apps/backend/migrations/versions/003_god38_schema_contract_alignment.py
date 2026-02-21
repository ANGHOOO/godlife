"""Align active persistence schema with runtime model contract for GOD-38."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "003_god38_schema_contract_alignment"
down_revision = "002_add_operability_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Align legacy integer profile metrics to numeric profile metrics."""
    op.alter_column(
        "user_profiles",
        "height_cm",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=True,
    )
    op.alter_column(
        "user_profiles",
        "weight_kg",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Rollback to legacy integer profile metrics."""
    op.alter_column(
        "user_profiles",
        "height_cm",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
    op.alter_column(
        "user_profiles",
        "weight_kg",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
