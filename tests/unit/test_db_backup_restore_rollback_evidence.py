from __future__ import annotations

from scripts.db_backup_restore_rollback_evidence import (
    compare_counts,
    has_placeholder,
    normalize_db_url,
    valid_db_url,
)


def test_normalize_db_url_for_postgres_clients():
    assert normalize_db_url("postgresql+asyncpg://u:p@h/db") == "postgresql://u:p@h/db"
    assert normalize_db_url("postgres://u:p@h/db") == "postgresql://u:p@h/db"
    assert normalize_db_url("postgresql://u:p@h/db") == "postgresql://u:p@h/db"


def test_db_url_validation_rejects_local_and_placeholder():
    assert valid_db_url("postgresql://u:p@aws-0-eu-west-1.pooler.supabase.com:6543/postgres")
    assert not valid_db_url("postgresql://u:p@localhost/postgres")
    assert not valid_db_url("postgresql://u:p@example.com/postgres")
    assert not valid_db_url("<db-url>")


def test_placeholder_detection():
    assert has_placeholder("<value>")
    assert has_placeholder("https://example.com")
    assert has_placeholder("TODO")
    assert not has_placeholder("aws-0-eu-west-1.pooler.supabase.com")


def test_key_mismatch_detection():
    source = {"key_table_counts": {"audit_events": 6, "irt_items": 1600}}
    restore = {"key_table_counts": {"audit_events": 6, "irt_items": 1599}}
    mismatches = compare_counts(source, restore)
    assert "irt_items" in mismatches
    assert "audit_events" not in mismatches
