"""
Merge Alembic heads into a single linear graph.

This merge revision is a no-op migration whose purpose is to unify multiple
independent migration roots/heads found in the repository into a single
head so `alembic history` and CI pipelines see a linear upgrade path.

After applying this merge (and stamping databases as needed), future
revisions should be created from the single head produced by this merge.
"""
from alembic import op

revision = "merge_2026_05_01"
# List all current heads discovered in the repo; Alembic will treat this as a merge
down_revision = (
    "0001",
    "0001_initial",
    "0001_five_pillar_schema",
    "0004_add_rlhf_pipeline",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is intentionally a no-op merge revision. It unifies several
    # parallel migration branches into a single head for downstream CI and
    # deployment workflows. Database-specific stamping may be required for
    # already-deployed environments.
    pass


def downgrade() -> None:
    # Downgrade of a merge revision is a no-op and generally not supported
    # in the multi-head merge sense. Keep this as a no-op to avoid surprises.
    pass
