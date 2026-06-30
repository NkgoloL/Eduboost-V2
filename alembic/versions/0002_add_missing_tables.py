"""Retire legacy missing-table migration in favour of canonical V2 schema.

Revision ID: 0002_add_missing_tables
Revises: merge_2026_05_01
Create Date: 2026-04-27 00:00:00

The original version of this migration attempted to create legacy tables that
conflicted with the current canonical V2 schema introduced by
0001_v2_consolidated_schema.py. It created a duplicate `lessons` table and
foreign keys to a legacy `learners` table that is no longer part of the active
model. Keeping this revision as an explicit no-op preserves the revision graph
while allowing fresh database bootstraps to proceed deterministically.
"""
from __future__ import annotations

revision = "0002_add_missing_tables"
down_revision = "merge_2026_05_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Superseded by the canonical V2 schema in 0001_v2_consolidated_schema.py.
    pass


def downgrade() -> None:
    # No-op by design. This revision no longer creates runtime tables.
    pass
