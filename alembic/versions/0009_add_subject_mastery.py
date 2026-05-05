"""Add subject_mastery table

Revision ID: 0009_add_subject_mastery
Revises: 771fb3ac38b8
Create Date: 2026-05-05 17:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0009_add_subject_mastery'
down_revision = '771fb3ac38b8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'subject_mastery',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('learner_id', sa.String(length=36), nullable=False),
        sa.Column('subject', sa.String(length=60), nullable=False),
        sa.Column('topic', sa.String(length=120), nullable=False),
        sa.Column('theta', sa.Float(), nullable=False),
        sa.Column('standard_error', sa.Float(), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['learner_id'], ['learner_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subject_mastery_learner_subject', 'subject_mastery', ['learner_id', 'subject'], unique=False)


def downgrade():
    op.drop_index('ix_subject_mastery_learner_subject', table_name='subject_mastery')
    op.drop_table('subject_mastery')
