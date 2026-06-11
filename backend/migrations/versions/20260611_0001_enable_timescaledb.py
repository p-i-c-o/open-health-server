"""Enable TimescaleDB extension.

Revision ID: 20260611_0001
Revises:
Create Date: 2026-06-11
"""

from alembic import op

revision = "20260611_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS timescaledb")
