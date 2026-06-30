from __future__ import annotations

from scripts.db_live_only_table_ownership import (
    EXPECTED_LIVE_ONLY_TABLES,
    ALLOWED_OWNERSHIP,
    build_records,
    write_status,
)


def test_expected_live_only_tables_are_accounted_for():
    records = build_records()
    assert {record.table for record in records} == set(EXPECTED_LIVE_ONLY_TABLES)


def test_ownership_values_are_allowed():
    records = build_records()
    for record in records:
        assert record.ownership in ALLOWED_OWNERSHIP


def test_default_policy_marks_live_only_tables_sql_owned_non_blocking():
    records = build_records()
    for record in records:
        assert record.ownership == "sql-owned"
        assert record.orm_model_required is False
        assert record.beta_blocking is False
        assert record.accepted is True


def test_status_writes_ownership_artifacts():
    status = write_status()
    assert status.status == "db-live-only-table-ownership-accepted"
    assert status.accepted_count == status.required_count
