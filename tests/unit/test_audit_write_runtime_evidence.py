from __future__ import annotations

from scripts.audit_write_runtime_evidence import _trace_detected, has_placeholder, normalize_db_url, valid_db_url


def test_normalize_db_url_for_psycopg2():
    assert normalize_db_url("postgresql+asyncpg://u:p@h/db") == "postgresql://u:p@h/db"
    assert normalize_db_url("postgres://u:p@h/db") == "postgresql://u:p@h/db"
    assert normalize_db_url("postgresql://u:p@h/db") == "postgresql://u:p@h/db"


def test_db_url_validation_rejects_local_and_placeholder():
    assert valid_db_url("postgresql://u:p@db.example-host.supabase.co/postgres")
    assert not valid_db_url("postgresql://u:p@localhost/postgres")
    assert not valid_db_url("postgresql://u:p@example.com/postgres")
    assert not valid_db_url("<db-url>")


def test_placeholder_detection():
    assert has_placeholder("<value>")
    assert has_placeholder("https://example.com")
    assert has_placeholder("TODO")
    assert not has_placeholder("audit-write-flow")


def test_trace_detection_in_nested_row_payload():
    rows = [{"id": 1, "metadata": {"trace": "audit-write-123"}}, {"id": 2, "message": "other"}]
    assert _trace_detected(rows, "audit-write-123")
    assert not _trace_detected(rows, "missing")
