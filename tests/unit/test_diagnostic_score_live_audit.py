from __future__ import annotations

from scripts.diagnostic_score_live_audit import (
    _expr_for_diag_column,
    normalize_db_url,
    ColumnInfo,
)


def col(name: str, nullable: bool = False, default: bool = False, data_type: str = "text", udt_name: str = "text") -> ColumnInfo:
    return ColumnInfo(
        name=name,
        is_nullable=nullable,
        has_default=default,
        data_type=data_type,
        udt_name=udt_name,
    )


def test_normalize_db_url_to_asyncpg():
    assert normalize_db_url("postgresql://u:p@h/db").startswith("postgresql+asyncpg://")
    assert normalize_db_url("postgres://u:p@h/db").startswith("postgresql+asyncpg://")
    assert normalize_db_url("postgresql+asyncpg://u:p@h/db").startswith("postgresql+asyncpg://")


def test_bridge_expression_maps_item_id_from_irt_id():
    expr = _expr_for_diag_column(col("item_id"), {"id"})
    assert expr == 'gen_random_uuid()'


def test_bridge_expression_skips_nullable_unknown_columns():
    expr = _expr_for_diag_column(col("optional_note", nullable=True), {"id"})
    assert expr is None


def test_bridge_expression_rejects_required_unknown_columns():
    expr = _expr_for_diag_column(col("required_unknown"), {"id"})
    assert expr == "__UNSUPPORTED_REQUIRED__"
