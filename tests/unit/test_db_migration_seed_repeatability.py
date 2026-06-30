from __future__ import annotations

from pathlib import Path

from scripts.db_migration_seed_repeatability import (
    EXPECTED_IRT_ROWS,
    BROKEN_NULL_IRT_SEED_RE,
    clean_supabase_sql,
    generate_irt_seed_sql,
    write_status,
)


def test_clean_supabase_sql_removes_debug_chatter_null_seed_and_role_lines():
    raw = """INFO [alembic.runtime.migration] Running upgrade
DEBUG: Creating enum itemtype
CREATE TABLE public.irt_items (id text);
INSERT INTO irt_items (
 id, grade, subject, topic, language, question_text, options,
 correct_option, a_param, b_param
 )
 VALUES (
 NULL, NULL, NULL, NULL, NULL, NULL,
 CAST(NULL AS JSONB), NULL, NULL, NULL
 )
 ON CONFLICT (id) DO NOTHING;

REVOKE ALL ON SCHEMA public FROM eduboost_app;
INSERT INTO alembic_version (version_num) VALUES ('20260516_0100');
"""
    assert BROKEN_NULL_IRT_SEED_RE.search(raw)
    cleaned, chatter, null_blocks, role_lines = clean_supabase_sql(raw)
    assert "INFO [" not in cleaned
    assert "DEBUG:" not in cleaned
    assert "CAST(NULL AS JSONB)" not in cleaned
    assert "eduboost_app" not in cleaned
    assert chatter == 2
    assert null_blocks == 1
    assert role_lines == 1


def test_generate_irt_seed_sql_is_idempotent_and_expected_size():
    generated, unique = generate_irt_seed_sql()
    assert unique == EXPECTED_IRT_ROWS
    assert generated >= unique
    text = Path("temp/db_repeatability/seed_irt_items.sql").read_text(encoding="utf-8")
    assert text.count("INSERT INTO public.irt_items") == EXPECTED_IRT_ROWS
    assert "ON CONFLICT (id) DO NOTHING" in text


def test_write_status_generates_repeatability_artifacts():
    status = write_status()
    assert status.status in {
        "db-migration-seed-repeatability-passing",
        "db-migration-seed-repeatability-not-proven",
    }
    assert Path("docs/release/db_migration_seed_repeatability_status.json").exists()
    assert Path("docs/release/db_migration_seed_repeatability_status.md").exists()
    assert Path("temp/db_repeatability/alembic_upgrade_head.supabase.sql").exists()
    assert Path("temp/db_repeatability/seed_irt_items.sql").exists()

def test_clean_supabase_sql_removes_schema_qualified_quoted_null_seed():
    from scripts.db_migration_seed_repeatability import clean_supabase_sql

    raw = "\n".join([
        'CREATE TABLE public."irt_items" (id text);',
        'INSERT INTO public."irt_items" (',
        '  id, grade, subject, topic, language, question_text, options,',
        '  correct_option, a_param, b_param',
        ')',
        'VALUES (',
        '  NULL, NULL, NULL, NULL, NULL, NULL,',
        '  CAST(NULL AS JSONB), NULL, NULL, NULL',
        ')',
        'ON CONFLICT (id) DO NOTHING;',
        "INSERT INTO alembic_version (version_num) VALUES ('20260516_0100');",
    ])

    cleaned, _chatter, null_blocks, _role_lines = clean_supabase_sql(raw)
    assert null_blocks == 1
    assert 'CAST(NULL AS JSONB)' not in cleaned
    assert 'ON CONFLICT (id) DO NOTHING' not in cleaned
    assert '20260516_0100' in cleaned


def test_required_table_presence_handles_quoted_schema_qualified_ddl():
    from scripts.db_migration_seed_repeatability import _required_table_presence

    sql = "\n".join([
        'CREATE TABLE public."audit_events" (',
        '    id UUID PRIMARY KEY',
        ');',
        'CREATE TABLE IF NOT EXISTS "diagnostic_sessions" (',
        '    id UUID PRIMARY KEY',
        ');',
        'CREATE TABLE "irt_items" (',
        '    id TEXT PRIMARY KEY',
        ');',
    ])

    presence = _required_table_presence(sql)
    assert presence['audit_events'] is True
    assert presence['diagnostic_sessions'] is True
    assert presence['irt_items'] is True
