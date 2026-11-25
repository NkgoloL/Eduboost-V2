"""Quarantine generated content carrying unsupported approval labels.

Revision ID: 20261123_1200
Revises: 20260922_1600_educational_validation_traceability
Create Date: 2026-11-23
"""
from alembic import op

revision = "20261123_1200"
down_revision = "20260922_1600_educational_validation_traceability"
branch_labels = None
depends_on = None
SYNTHETIC_REVIEWERS = ("00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000002")


def upgrade() -> None:
    op.execute("""
        CREATE TABLE content_quarantine_20261123 (
            entity_type text NOT NULL,
            entity_id text NOT NULL,
            previous_review_status text NOT NULL,
            previous_reviewer_id uuid NULL,
            previous_reviewed_at timestamptz NULL,
            PRIMARY KEY (entity_type, entity_id)
        )
    """)
    op.execute(f"""
        INSERT INTO content_quarantine_20261123
            (entity_type, entity_id, previous_review_status, previous_reviewer_id, previous_reviewed_at)
        SELECT 'diagnostic_item', item_id::text, review_status::text, reviewer_id, reviewed_at
        FROM diagnostic_items
        WHERE review_status::text IN ('approved', 'human_reviewed')
          AND (reviewer_id IN ('{SYNTHETIC_REVIEWERS[0]}'::uuid, '{SYNTHETIC_REVIEWERS[1]}'::uuid)
               OR (review_status::text = 'approved' AND source::text = 'llm_generated')
               OR (review_status::text = 'human_reviewed' AND reviewer_id IS NULL))
    """)
    op.execute("""
        UPDATE diagnostic_items
        SET review_status = 'ai_generated', reviewer_id = NULL, reviewed_at = NULL
        WHERE item_id::text IN (
            SELECT entity_id FROM content_quarantine_20261123 WHERE entity_type = 'diagnostic_item'
        )
    """)
    op.execute(f"""
        INSERT INTO content_quarantine_20261123
            (entity_type, entity_id, previous_review_status, previous_reviewer_id, previous_reviewed_at)
        SELECT 'lesson', id::text, review_status, reviewer_id, reviewed_at
        FROM lessons
        WHERE review_status IN ('approved', 'human_reviewed')
          AND (
              reviewer_id IN ('{SYNTHETIC_REVIEWERS[0]}'::uuid, '{SYNTHETIC_REVIEWERS[1]}'::uuid)
              OR (reviewer_id IS NULL AND (prompt_template_version IS NOT NULL OR review_status = 'human_reviewed'))
          )
    """)
    op.execute("""
        UPDATE lessons
        SET review_status = 'ai_generated', reviewer_id = NULL, reviewed_at = NULL
        WHERE id IN (
            SELECT entity_id FROM content_quarantine_20261123 WHERE entity_type = 'lesson'
        )
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE diagnostic_items AS item
        SET review_status = quarantine.previous_review_status,
            reviewer_id = quarantine.previous_reviewer_id,
            reviewed_at = quarantine.previous_reviewed_at
        FROM content_quarantine_20261123 AS quarantine
        WHERE quarantine.entity_type = 'diagnostic_item'
          AND item.item_id::text = quarantine.entity_id
    """)
    op.execute("""
        UPDATE lessons AS lesson
        SET review_status = quarantine.previous_review_status,
            reviewer_id = quarantine.previous_reviewer_id,
            reviewed_at = quarantine.previous_reviewed_at
        FROM content_quarantine_20261123 AS quarantine
        WHERE quarantine.entity_type = 'lesson'
          AND lesson.id::text = quarantine.entity_id
    """)
    op.execute("DROP TABLE content_quarantine_20261123")
