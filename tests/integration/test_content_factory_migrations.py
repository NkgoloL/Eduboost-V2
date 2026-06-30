"""tests/integration/test_content_factory_migrations.py
─────────────────────────────────────────────────────────────────────────────
Verifies that after `alembic upgrade head` runs the Content Factory tables
and their key columns are present in the live database. Requires a real
database connection (uses the `db_session` fixture from the root conftest).
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import enum
import pytest
from sqlalchemy import inspect, text

pytestmark = pytest.mark.integration

# ── ORM-derived table list (single source of truth) ───────────────────────────
# Derived directly from app.models.content_factory so this list stays in sync
# with the ORM automatically – any new model added there will be caught here.
import app.models.content_factory as _cf_models  # noqa: E402
from app.core.database import Base  # noqa: E402

_CF_ORM_CLASSES = [
    cls for cls in _cf_models.__dict__.values()
    if isinstance(cls, type) and issubclass(cls, Base) and hasattr(cls, "__tablename__")
]

REQUIRED_TABLES: list[str] = sorted(
    {cls.__tablename__ for cls in _CF_ORM_CLASSES}
)

# Spot-check columns in the two tables that received the most schema expansion
REQUIRED_SOURCE_COLUMNS = [
    "source_document_id",
    "source_chunk_id",
    "license_status",
    "source_quality_score",
]

REQUIRED_TASK_COLUMNS = [
    "idempotency_key",
    "depends_on_task_ids",
    "validation_failures",
    "token_usage",
]

# ── Enum/status compatibility map: ORM Python enum → DB type name ─────────────
# Each entry: (Python enum class, expected postgres type name)
_ENUM_COMPAT_CHECKS: list[tuple[type[enum.Enum], str]] = [
    (_cf_models.ContentArtifactStatus, "content_artifact_status"),
    (_cf_models.ContentLayer, "content_layer"),
    (_cf_models.ContentArtifactType, "content_artifact_type"),
    (_cf_models.ContentReviewAction, "content_review_action"),
    (_cf_models.ContentScopeStatus, "content_scope_status"),
]


@pytest.mark.asyncio
async def test_content_factory_tables_exist(db_session):
    """All Content Factory tables must be present after migration."""

    def _check(conn):
        inspector = inspect(conn)
        existing = set(inspector.get_table_names())
        missing = [t for t in REQUIRED_TABLES if t not in existing]
        return missing

    async with db_session.bind.connect() as conn:
        missing = await conn.run_sync(_check)

    assert not missing, f"Missing Content Factory tables: {missing}"


@pytest.mark.asyncio
async def test_content_artifact_sources_columns(db_session):
    """content_artifact_sources must have provenance columns."""

    def _check(conn):
        inspector = inspect(conn)
        cols = {c["name"] for c in inspector.get_columns("content_artifact_sources")}
        return [c for c in REQUIRED_SOURCE_COLUMNS if c not in cols]

    async with db_session.bind.connect() as conn:
        missing = await conn.run_sync(_check)

    assert not missing, (
        f"content_artifact_sources missing columns: {missing}"
    )


@pytest.mark.asyncio
async def test_content_generation_tasks_columns(db_session):
    """content_generation_tasks must have ledger columns."""

    def _check(conn):
        inspector = inspect(conn)
        cols = {c["name"] for c in inspector.get_columns("content_generation_tasks")}
        return [c for c in REQUIRED_TASK_COLUMNS if c not in cols]

    async with db_session.bind.connect() as conn:
        missing = await conn.run_sync(_check)

    assert not missing, (
        f"content_generation_tasks missing columns: {missing}"
    )


@pytest.mark.asyncio
async def test_content_generation_artifacts_unique_hash(db_session):
    """artifact_hash column must have a unique index."""

    def _check(conn):
        inspector = inspect(conn)
        unique_constraints = inspector.get_unique_constraints(
            "content_generation_artifacts"
        )
        indexes = inspector.get_indexes("content_generation_artifacts")

        has_unique = any(
            "artifact_hash" in c.get("column_names", [])
            for c in unique_constraints
        ) or any(
            "artifact_hash" in idx.get("column_names", []) and idx.get("unique")
            for idx in indexes
        )
        return has_unique

    async with db_session.bind.connect() as conn:
        has_unique = await conn.run_sync(_check)

    assert has_unique, "content_generation_artifacts.artifact_hash must have a unique constraint"


# ── ORM ↔ migration table name reconciliation ─────────────────────────────────

@pytest.mark.asyncio
async def test_all_orm_tables_exist_in_db(db_session):
    """Every __tablename__ declared in app.models.content_factory must exist in the DB.

    This test is auto-derived from the ORM — if a new model is added but
    its migration is forgotten, this test will catch it.
    """
    def _check(conn):
        inspector = inspect(conn)
        existing = set(inspector.get_table_names())
        missing = [t for t in REQUIRED_TABLES if t not in existing]
        [t for t in REQUIRED_TABLES if t not in existing]
        return missing

    async with db_session.bind.connect() as conn:
        missing = await conn.run_sync(_check)

    assert not missing, (
        f"ORM-declared tables not found in DB after migration: {missing}. "
        "Add a migration for these tables."
    )


# ── Enum / status value compatibility ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_content_artifact_status_enum_matches_db(db_session):
    """Python ContentArtifactStatus values must exactly match the DB enum type."""
    py_values = {e.value for e in _cf_models.ContentArtifactStatus}
    query = text(
        "SELECT enumlabel FROM pg_enum "
        "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
        "WHERE pg_type.typname = 'content_artifact_status'"
    )
    result = await db_session.execute(query)
    db_values = {row[0] for row in result.fetchall()}

    missing_in_db = py_values - db_values
    missing_in_py = db_values - py_values
    assert not missing_in_db, f"Python enum values not in DB enum: {missing_in_db}"
    assert not missing_in_py, f"DB enum values not in Python enum: {missing_in_py}"


@pytest.mark.asyncio
async def test_content_layer_enum_matches_db(db_session):
    """Python ContentLayer values must exactly match the DB enum type."""
    py_values = {e.value for e in _cf_models.ContentLayer}
    query = text(
        "SELECT enumlabel FROM pg_enum "
        "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
        "WHERE pg_type.typname = 'content_layer'"
    )
    result = await db_session.execute(query)
    db_values = {row[0] for row in result.fetchall()}

    missing_in_db = py_values - db_values
    missing_in_py = db_values - py_values
    assert not missing_in_db, f"ContentLayer Python values not in DB: {missing_in_db}"
    assert not missing_in_py, f"ContentLayer DB values not in Python: {missing_in_py}"


@pytest.mark.asyncio
async def test_content_artifact_type_enum_matches_db(db_session):
    """Python ContentArtifactType values must exactly match the DB enum type."""
    py_values = {e.value for e in _cf_models.ContentArtifactType}
    query = text(
        "SELECT enumlabel FROM pg_enum "
        "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
        "WHERE pg_type.typname = 'content_artifact_type'"
    )
    result = await db_session.execute(query)
    db_values = {row[0] for row in result.fetchall()}

    missing_in_db = py_values - db_values
    missing_in_py = db_values - py_values
    assert not missing_in_db, f"ContentArtifactType Python values not in DB: {missing_in_db}"
    assert not missing_in_py, f"ContentArtifactType DB values not in Python: {missing_in_py}"


@pytest.mark.asyncio
async def test_content_review_action_enum_matches_db(db_session):
    """Python ContentReviewAction values must exactly match the DB enum type."""
    py_values = {e.value for e in _cf_models.ContentReviewAction}
    query = text(
        "SELECT enumlabel FROM pg_enum "
        "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
        "WHERE pg_type.typname = 'content_review_action'"
    )
    result = await db_session.execute(query)
    db_values = {row[0] for row in result.fetchall()}

    missing_in_db = py_values - db_values
    missing_in_py = db_values - py_values
    assert not missing_in_db, f"ContentReviewAction Python values not in DB: {missing_in_db}"
    assert not missing_in_py, f"ContentReviewAction DB values not in Python: {missing_in_py}"


@pytest.mark.asyncio
async def test_content_scope_status_enum_matches_db(db_session):
    """Python ContentScopeStatus values must exactly match the DB enum type."""
    py_values = {e.value for e in _cf_models.ContentScopeStatus}
    query = text(
        "SELECT enumlabel FROM pg_enum "
        "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
        "WHERE pg_type.typname = 'content_scope_status'"
    )
    result = await db_session.execute(query)
    db_values = {row[0] for row in result.fetchall()}

    missing_in_db = py_values - db_values
    missing_in_py = db_values - py_values
    assert not missing_in_db, f"ContentScopeStatus Python values not in DB: {missing_in_db}"
    assert not missing_in_py, f"ContentScopeStatus DB values not in Python: {missing_in_py}"
