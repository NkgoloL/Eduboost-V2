"""Merge migration branches

Revision ID: f2faf5aa12fd
Revises: 20260528_1700, 3f8a2c1d9e04
Create Date: 2026-06-05 20:18:52.618812
"""
from alembic import op
import sqlalchemy as sa


revision = 'f2faf5aa12fd'
down_revision = ('20260528_1700', '3f8a2c1d9e04')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
