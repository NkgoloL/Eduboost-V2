"""Merge remaining heads 0004 and 0005

Revision ID: 94b628483fa7
Revises: 0004_add_rlhf_pipeline, 0005_seed_irt_items
Create Date: 2026-05-03 15:03:30.449260
"""
from alembic import op
import sqlalchemy as sa


revision = '94b628483fa7'
down_revision = ('0004_add_rlhf_pipeline', '0005_seed_irt_items')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
