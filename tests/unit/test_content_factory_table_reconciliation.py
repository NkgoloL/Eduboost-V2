"""tests/unit/test_content_factory_table_reconciliation.py

Verifies that the ORM models in app.models.content_factory agree with the
centralized schema contract in scripts.ci.content_factory_schema_contract.

User rule: "Table reconciliation should compare against a single source of
truth" (centralized constants file).

These are static tests — no database connection is required.
"""
from __future__ import annotations

import importlib
import inspect

import pytest

from scripts.ci.content_factory_schema_contract import (
    ORM_TABLE_MAP,
    REQUIRED_COLUMNS,
    REQUIRED_TABLES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_orm_models() -> dict[str, type]:
    """Import and return {ClassName: class} for all models in content_factory."""
    module = importlib.import_module("app.models.content_factory")
    result: dict[str, type] = {}
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if hasattr(obj, "__tablename__"):
            result[name] = obj
    return result


def _orm_column_names(model_cls: type) -> set[str]:
    """Return the set of mapped column names for an ORM model."""
    try:
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(model_cls)
        return {col.key for col in mapper.column_attrs}
    except Exception:
        # Fallback: introspect __table__ if mapper is not available pre-mapping
        if hasattr(model_cls, "__table__"):
            return {col.name for col in model_cls.__table__.columns}
        return set()


# ---------------------------------------------------------------------------
# ORM → table name reconciliation
# ---------------------------------------------------------------------------

class TestOrmTableNameReconciliation:
    """ORM __tablename__ values must match the contract's ORM_TABLE_MAP."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.models = _load_orm_models()

    def test_all_contract_models_are_importable(self):
        """Every model named in ORM_TABLE_MAP must be importable."""
        missing: list[str] = []
        for model_name in ORM_TABLE_MAP:
            if model_name not in self.models:
                missing.append(model_name)

        assert not missing, (
            f"These models are declared in ORM_TABLE_MAP but not found in "
            f"app.models.content_factory: {missing!r}. "
            "Either add them to the model file or remove from the contract."
        )

    def test_orm_tablenames_match_contract(self):
        """Each ORM class's __tablename__ must match its contract entry."""
        mismatches: list[str] = []
        for model_name, expected_table in ORM_TABLE_MAP.items():
            if model_name not in self.models:
                continue  # caught by the previous test
            actual_table = self.models[model_name].__tablename__
            if actual_table != expected_table:
                mismatches.append(
                    f"{model_name}: ORM={actual_table!r}, contract={expected_table!r}"
                )

        assert not mismatches, (
            "ORM __tablename__ values do not match the schema contract:\n"
            + "\n".join(f"  {m}" for m in mismatches)
        )

    def test_no_undeclared_orm_models(self):
        """No ORM model may exist without a corresponding contract entry."""
        undeclared: list[str] = []
        for model_name in self.models:
            if model_name not in ORM_TABLE_MAP:
                undeclared.append(
                    f"{model_name} (__tablename__={self.models[model_name].__tablename__!r})"
                )

        assert not undeclared, (
            "The following ORM models are not declared in ORM_TABLE_MAP. "
            "Add them to the schema contract:\n"
            + "\n".join(f"  {m}" for m in undeclared)
        )


# ---------------------------------------------------------------------------
# Required tables
# ---------------------------------------------------------------------------

class TestRequiredTablesPresent:
    """All REQUIRED_TABLES must have a corresponding ORM model."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.models = _load_orm_models()
        self.orm_tables = {cls.__tablename__ for cls in self.models.values()}

    def test_all_required_tables_have_orm_model(self):
        missing: list[str] = []
        for table_name in REQUIRED_TABLES:
            if table_name not in self.orm_tables:
                missing.append(table_name)

        assert not missing, (
            f"These required tables have no corresponding ORM model: {missing!r}. "
            "Either add the ORM model or remove the table from REQUIRED_TABLES."
        )


# ---------------------------------------------------------------------------
# Required columns
# ---------------------------------------------------------------------------

class TestRequiredColumnsPresent:
    """All REQUIRED_COLUMNS per-table must be present on the ORM model."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.models = _load_orm_models()
        # Build table_name → model_class map
        self.table_to_model: dict[str, type] = {
            cls.__tablename__: cls for cls in self.models.values()
        }

    def test_required_columns_exist_on_orm_models(self):
        missing_per_table: dict[str, list[str]] = {}

        for table_name, required_cols in REQUIRED_COLUMNS.items():
            model_cls = self.table_to_model.get(table_name)
            if model_cls is None:
                missing_per_table[table_name] = [
                    f"(no ORM model for table '{table_name}')"
                ]
                continue

            orm_cols = _orm_column_names(model_cls)
            missing = [c for c in required_cols if c not in orm_cols]
            if missing:
                missing_per_table[table_name] = missing

        assert not missing_per_table, (
            "Some required columns are absent from ORM models:\n"
            + "\n".join(
                f"  {table}: {cols!r}"
                for table, cols in missing_per_table.items()
            )
        )

    def test_idempotency_key_is_unique_on_tasks(self):
        """content_generation_tasks.idempotency_key must have a unique constraint."""
        model_cls = self.table_to_model.get("content_generation_tasks")
        if model_cls is None:
            pytest.skip("content_generation_tasks ORM model not found")

        if not hasattr(model_cls, "__table__"):
            pytest.skip("__table__ not yet constructed")

        unique_cols: set[str] = set()
        for col in model_cls.__table__.columns:
            if col.unique:
                unique_cols.add(col.name)

        assert "idempotency_key" in unique_cols, (
            "content_generation_tasks.idempotency_key must have a UNIQUE constraint. "
            f"Unique columns found: {unique_cols!r}"
        )

    def test_artifact_hash_is_unique_on_artifacts(self):
        """content_generation_artifacts.artifact_hash must have a unique constraint."""
        model_cls = self.table_to_model.get("content_generation_artifacts")
        if model_cls is None:
            pytest.skip("content_generation_artifacts ORM model not found")

        if not hasattr(model_cls, "__table__"):
            pytest.skip("__table__ not yet constructed")

        unique_cols: set[str] = set()
        for col in model_cls.__table__.columns:
            if col.unique:
                unique_cols.add(col.name)

        assert "artifact_hash" in unique_cols, (
            "content_generation_artifacts.artifact_hash must have a UNIQUE constraint."
        )


# ---------------------------------------------------------------------------
# Contract self-consistency
# ---------------------------------------------------------------------------

class TestSchemaContractSelfConsistency:
    """REQUIRED_COLUMNS tables must all be present in REQUIRED_TABLES."""

    def test_required_columns_tables_are_in_required_tables(self):
        required_tables_set = set(REQUIRED_TABLES)
        extra: list[str] = [
            t for t in REQUIRED_COLUMNS if t not in required_tables_set
        ]
        assert not extra, (
            f"REQUIRED_COLUMNS references tables not in REQUIRED_TABLES: {extra!r}. "
            "Add them to REQUIRED_TABLES."
        )

    def test_orm_table_map_values_are_in_required_tables(self):
        required_tables_set = set(REQUIRED_TABLES)
        extra: list[str] = [
            f"{model} → {table}"
            for model, table in ORM_TABLE_MAP.items()
            if table not in required_tables_set
        ]
        assert not extra, (
            f"ORM_TABLE_MAP references tables not in REQUIRED_TABLES: {extra!r}. "
            "Add them to REQUIRED_TABLES."
        )
