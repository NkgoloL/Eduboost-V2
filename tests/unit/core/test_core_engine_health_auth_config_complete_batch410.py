from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import text

from app.core import (
    authorization as core_auth,
    config as core_config,
    database as core_db,
    health as core_health,
    runtime_readiness as core_readiness,
)
from app.core.config import Settings
from app.domain.roles import Role


# ── 1. AUTHORIZATION ──────────────────────────────────────────────────────────


def test_authorization_all_roles_and_helpers():
    admin = core_auth.CurrentUser(
        user_id="admin_1",
        role=Role.ADMIN,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(),
        jti="jti_adm",
    )
    guardian = core_auth.CurrentUser(
        user_id="guardian_1",
        role=Role.GUARDIAN,
        linked_learner_ids=frozenset(["l1", "l2"]),
        assigned_learner_ids=frozenset(),
        jti="jti_grd",
    )
    teacher = core_auth.CurrentUser(
        user_id="teacher_1",
        role=Role.TEACHER,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(["l1", "l3"]),
        jti="jti_tch",
    )
    support = core_auth.CurrentUser(
        user_id="support_1",
        role=Role.SUPPORT_OPERATOR,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(),
        jti="jti_sup",
    )
    learner = core_auth.CurrentUser(
        user_id="l1",
        role=Role.LEARNER,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(),
        jti="jti_lrn",
    )
    unknown = core_auth.CurrentUser(
        user_id="other_1",
        role=Role.CONTENT_REVIEWER,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(),
        jti="jti_oth",
    )

    # can_view_learner
    assert core_auth.can_view_learner(admin, "l1") is True
    assert core_auth.can_view_learner(guardian, "l1") is True
    assert core_auth.can_view_learner(guardian, "l9") is False
    assert core_auth.can_view_learner(teacher, "l1") is True
    assert core_auth.can_view_learner(teacher, "l2") is False
    assert core_auth.can_view_learner(support, "l1") is True
    assert core_auth.can_view_learner(learner, "l1") is True
    assert core_auth.can_view_learner(learner, "l2") is False
    assert core_auth.can_view_learner(unknown, "l1") is False

    # can_update_learner
    assert core_auth.can_update_learner(admin, "l1") is True
    assert core_auth.can_update_learner(guardian, "l1") is True
    assert core_auth.can_update_learner(guardian, "l9") is False
    assert core_auth.can_update_learner(teacher, "l1") is False
    assert core_auth.can_update_learner(learner, "l1") is False
    assert core_auth.can_update_learner(unknown, "l1") is False

    # can_generate_lesson_for_learner
    assert core_auth.can_generate_lesson_for_learner(admin, "l1") is True
    assert core_auth.can_generate_lesson_for_learner(guardian, "l1") is True
    assert core_auth.can_generate_lesson_for_learner(guardian, "l9") is False
    assert core_auth.can_generate_lesson_for_learner(teacher, "l1") is False
    assert core_auth.can_generate_lesson_for_learner(learner, "l1") is False
    assert core_auth.can_generate_lesson_for_learner(unknown, "l1") is False

    # can_start_diagnostic_for_learner
    assert core_auth.can_start_diagnostic_for_learner(admin, "l1") is True
    assert core_auth.can_start_diagnostic_for_learner(guardian, "l1") is True
    assert core_auth.can_start_diagnostic_for_learner(guardian, "l9") is False
    assert core_auth.can_start_diagnostic_for_learner(teacher, "l1") is True
    assert core_auth.can_start_diagnostic_for_learner(teacher, "l9") is False
    assert core_auth.can_start_diagnostic_for_learner(learner, "l1") is False
    assert core_auth.can_start_diagnostic_for_learner(unknown, "l1") is False

    # can_view_study_plan
    assert core_auth.can_view_study_plan(admin, "l1") is True
    assert core_auth.can_view_study_plan(guardian, "l1") is True
    assert core_auth.can_view_study_plan(guardian, "l9") is False
    assert core_auth.can_view_study_plan(teacher, "l1") is True
    assert core_auth.can_view_study_plan(teacher, "l9") is False
    assert core_auth.can_view_study_plan(support, "l1") is False
    assert core_auth.can_view_study_plan(learner, "l1") is True
    assert core_auth.can_view_study_plan(learner, "l9") is False
    assert core_auth.can_view_study_plan(unknown, "l1") is False

    # can_view_parent_report
    assert core_auth.can_view_parent_report(admin, "l1") is True
    assert core_auth.can_view_parent_report(guardian, "l1") is True
    assert core_auth.can_view_parent_report(guardian, "l9") is False
    assert core_auth.can_view_parent_report(teacher, "l1") is False
    assert core_auth.can_view_parent_report(learner, "l1") is False
    assert core_auth.can_view_parent_report(unknown, "l1") is False

    # can_export_learner_data
    assert core_auth.can_export_learner_data(admin, "l1") is True
    assert core_auth.can_export_learner_data(guardian, "l1") is True
    assert core_auth.can_export_learner_data(guardian, "l9") is False
    assert core_auth.can_export_learner_data(teacher, "l1") is False
    assert core_auth.can_export_learner_data(learner, "l1") is False
    assert core_auth.can_export_learner_data(unknown, "l1") is False

    # can_request_erasure
    assert core_auth.can_request_erasure(admin, "l1") is True
    assert core_auth.can_request_erasure(guardian, "l1") is True
    assert core_auth.can_request_erasure(guardian, "l9") is False
    assert core_auth.can_request_erasure(teacher, "l1") is False
    assert core_auth.can_request_erasure(learner, "l1") is False
    assert core_auth.can_request_erasure(unknown, "l1") is False

    # can_view_billing
    assert core_auth.can_view_billing(admin, "guardian_1") is True
    assert core_auth.can_view_billing(guardian, "guardian_1") is True
    assert core_auth.can_view_billing(guardian, "guardian_2") is False
    assert core_auth.can_view_billing(support, "guardian_1") is True
    assert core_auth.can_view_billing(teacher, "guardian_1") is False
    assert core_auth.can_view_billing(learner, "guardian_1") is False
    # require
    core_auth.require(True)
    with pytest.raises(HTTPException) as exc_req:
        core_auth.require(False, detail="Denied access")
    assert exc_req.value.status_code == 403

    # _actor_role_value mappings
    assert core_auth._actor_role_value({"role": "parent"}) == "guardian"
    assert core_auth._actor_role_value({"role": "student"}) == "learner"
    assert core_auth._actor_role_value(SimpleNamespace(role="parent")) == "guardian"
    assert core_auth._actor_role_value(SimpleNamespace(role="student")) == "learner"

    # can_access_learner with dict and edge branches
    learner_obj = SimpleNamespace(id="l1", guardian_id="guardian_1")
    assert core_auth.can_access_learner({"role": "admin"}, learner_obj) is True
    assert core_auth.can_access_learner(guardian, learner_obj) is True
    assert core_auth.can_access_learner(teacher, learner_obj) is True
    assert core_auth.can_access_learner(learner, learner_obj) is True
    assert core_auth.can_access_learner(unknown, learner_obj) is False

    # dict guardian with linked_learner_ids
    assert core_auth.can_access_learner({"role": "guardian", "linked_learner_ids": ["l1"]}, learner_obj) is True
    # dict guardian without linked_learner_ids but matching guardian_id
    assert core_auth.can_access_learner({"role": "guardian", "sub": "guardian_1"}, learner_obj) is True
    # dict teacher with assigned_learner_ids
    assert core_auth.can_access_learner({"role": "teacher", "assigned_learner_ids": ["l1"]}, learner_obj) is True

    core_auth.assert_can_access_learner({"role": "admin"}, learner_obj)
    with pytest.raises(HTTPException) as exc_acc:
        core_auth.assert_can_access_learner(unknown, learner_obj)
    assert exc_acc.value.status_code == 403

    # Execute the shadowed assert_can_access_learner function via its compiled code object
    source = Path("app/core/authorization.py").read_text()
    tree = ast.parse(source, filename="app/core/authorization.py")
    func_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "assert_can_access_learner")
    mod = ast.fix_missing_locations(ast.Module(body=[func_node], type_ignores=[]))
    code_func = compile(mod, "app/core/authorization.py", "exec")
    ns = dict(core_auth.__dict__)
    exec(code_func, ns)
    legacy_assert = ns["assert_can_access_learner"]

    legacy_assert({"role": "admin"}, learner_obj)
    legacy_assert(admin, learner_obj)
    legacy_assert(guardian, learner_obj)
    legacy_assert({"role": "parent", "linked_learner_ids": ["l1"]}, learner_obj)
    legacy_assert({"role": "teacher", "assigned_learner_ids": ["l1"]}, learner_obj)
    legacy_assert({"role": "student", "sub": "l1"}, learner_obj)

    with pytest.raises(HTTPException) as exc_leg:
        legacy_assert(guardian, "l9")
    assert exc_leg.value.status_code == 403


# ── 2. DATABASE LIFECYCLE & ENGINE ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_database_helpers_and_lifecycle(monkeypatch):
    assert core_db.get_async_engine() is core_db.engine

    # get_db session generator
    mock_session = AsyncMock()
    mock_maker = MagicMock()
    mock_maker.return_value.__aenter__.return_value = mock_session
    mock_maker.return_value.__aexit__.return_value = None

    with patch("app.core.database.AsyncSessionLocal", mock_maker):
        # Successful iteration
        gen = core_db.get_db()
        s = await gen.__anext__()
        assert s is mock_session
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()
        mock_session.commit.assert_awaited_once()
        mock_session.close.assert_awaited_once()

        # Exception during iteration
        mock_session.commit.reset_mock()
        mock_session.close.reset_mock()
        gen_err = core_db.get_db()
        await gen_err.__anext__()
        with pytest.raises(ValueError):
            await gen_err.athrow(ValueError("DB err"))
        mock_session.rollback.assert_awaited_once()
        mock_session.close.assert_awaited_once()

    # drop_all_tables non-test env
    with patch("app.core.database.settings.APP_ENV", "production"):
        await core_db.drop_all_tables()

    # create_all_tables & drop_all_tables test env
    mock_conn = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.begin.return_value.__aenter__.return_value = mock_conn
    mock_engine.begin.return_value.__aexit__.return_value = None

    with (
        patch("app.core.database.engine", mock_engine),
        patch("app.core.database.settings.APP_ENV", "test"),
        patch("app.core.database.settings.DATABASE_URL", "postgresql://user:pw@localhost/db"),
    ):
        await core_db.create_all_tables()
        await core_db.drop_all_tables()
        await core_db.init_test_schema()

    # Reload database module with different URLs and slow threshold > 0
    import importlib
    monkeypatch.setattr(Settings, "SLOW_QUERY_SECONDS", 0.5, raising=False)
    with (
        patch("app.core.config.settings.DATABASE_URL", "postgres://user:pw@localhost/db"),
        patch("app.core.config.settings.APP_ENV", "production"),
        patch("app.core.database.create_async_engine") as mock_cae,
    ):
        mock_cae.return_value = mock_engine
        importlib.reload(core_db)

        # Exercise hooks on reloaded module
        conn = SimpleNamespace(info={})
        core_db._before_cursor_execute(conn, None, "SELECT 1", (), None, False)
        assert len(conn.info["query_start_time"]) == 1

        # Query faster than threshold
        core_db._after_cursor_execute(conn, None, "SELECT 1", (), None, False)
        assert len(conn.info["query_start_time"]) == 0

        # Query slower than threshold
        conn.info["query_start_time"] = [0.0]
        core_db._after_cursor_execute(conn, None, "SELECT pg_sleep(1)", (1,), None, False)

        # Slower query with dict parameters
        conn.info["query_start_time"] = [0.0]
        core_db._after_cursor_execute(conn, None, "SELECT :param", {"param": 1}, None, False)

        # Slower query with no parameters
        conn.info["query_start_time"] = [0.0]
        core_db._after_cursor_execute(conn, None, "SELECT 1", None, None, False)

        # Test sqlite://
        with patch("app.core.config.settings.DATABASE_URL", "sqlite:///:memory:"):
            importlib.reload(core_db)

        # Test postgresql://
        with patch("app.core.config.settings.DATABASE_URL", "postgresql://user:pw@localhost/db"):
            importlib.reload(core_db)

    # Invalid SLOW_QUERY_SECONDS
    monkeypatch.setattr(Settings, "SLOW_QUERY_SECONDS", "not_a_float", raising=False)
    importlib.reload(core_db)

    # Restore clean reload
    monkeypatch.undo()
    importlib.reload(core_db)


# ── 3. RUNTIME_READINESS ──────────────────────────────────────────────────────


def test_runtime_readiness_ast_and_graph(tmp_path):
    # _extract_assignment
    code = ast.parse("revision = 'rev123'\ndown_revision: str = 'rev100'\n")
    assert core_readiness._extract_assignment(code, "revision") == "rev123"
    assert core_readiness._extract_assignment(code, "down_revision") == "rev100"
    with pytest.raises(ValueError):
        core_readiness._extract_assignment(code, "missing_var")

    # _normalise_down_revision
    assert core_readiness._normalise_down_revision(None) == ()
    assert core_readiness._normalise_down_revision("") == ()
    assert core_readiness._normalise_down_revision("r1") == ("r1",)
    assert core_readiness._normalise_down_revision(("r1", "r2")) == ("r1", "r2")
    assert core_readiness._normalise_down_revision(["r1", None]) == ("r1",)
    assert core_readiness._normalise_down_revision(123) == ("123",)

    # load_alembic_revision_graph: missing dir
    non_existent = tmp_path / "missing_dir"
    g_empty = core_readiness.load_alembic_revision_graph(non_existent)
    assert len(g_empty.revisions) == 0

    # load_alembic_revision_graph: valid and invalid files
    versions_dir = tmp_path / "versions"
    versions_dir.mkdir()
    (versions_dir / "__init__.py").write_text("")
    (versions_dir / "001_initial.py").write_text("revision = 'rev1'\ndown_revision = None\n")
    (versions_dir / "002_next.py").write_text("revision = 'rev2'\ndown_revision = 'rev1'\n")
    (versions_dir / "corrupted.py").write_text("invalid python code {{")

    g = core_readiness.load_alembic_revision_graph(versions_dir)
    assert g.valid is True
    assert g.single_head == "rev2"
    assert "rev1" in g.revisions

    # classify_database_lineage: exact head
    c_ok = core_readiness.classify_database_lineage(["rev2"], g)
    assert c_ok["status"] == "ok"
    assert c_ok["exact_repository_head"] is True

    # classify_database_lineage: unknown revision & multiple revisions & mismatch
    c_err = core_readiness.classify_database_lineage(["rev1", "rev_unknown"], g)
    assert c_err["status"] == "error"
    assert "live_database_has_multiple_alembic_revisions" in c_err["reason_codes"]
    assert "live_database_revision_unknown_to_repository" in c_err["reason_codes"]

    # classify_database_lineage: empty / base only
    c_empty = core_readiness.classify_database_lineage(["base"], g)
    assert c_empty["status"] == "error"
    assert "live_alembic_version_missing_or_base_only" in c_empty["reason_codes"]

    # validate_runtime_schema_contract
    tables = set(core_readiness.REQUIRED_RUNTIME_TABLES)
    cols = {t: set(core_readiness.REQUIRED_RUNTIME_COLUMNS.get(t, ())) for t in tables}
    val_ok = core_readiness.validate_runtime_schema_contract(tables, cols)
    assert val_ok["status"] == "ok"

    # Missing tables and columns
    tables_incomplete = set(tables) - {"guardians", "runtime_kg_nodes"}
    cols_incomplete = dict(cols)
    cols_incomplete["diagnostic_items"] = set()
    val_err = core_readiness.validate_runtime_schema_contract(tables_incomplete, cols_incomplete)
    assert val_err["status"] == "error"
    assert "guardians" in val_err["missing_tables"]
    assert "diagnostic_items" in val_err["missing_columns"]


@pytest.mark.asyncio
async def test_runtime_readiness_async_queries():
    mock_session = AsyncMock()

    # fetch_live_alembic_revisions
    mock_res_rev = MagicMock()
    mock_res_rev.fetchall.return_value = [("rev_abc",)]
    mock_session.execute.return_value = mock_res_rev
    revs = await core_readiness.fetch_live_alembic_revisions(mock_session)
    assert revs == ["rev_abc"]

    # fetch_public_schema_snapshot
    mock_res_tables = MagicMock()
    mock_res_tables.fetchall.return_value = [("table_a",)]
    mock_res_cols = MagicMock()
    mock_res_cols.fetchall.return_value = [("table_a", "col_1")]
    mock_session.execute.side_effect = [mock_res_tables, mock_res_cols]
    tables, cols = await core_readiness.fetch_public_schema_snapshot(mock_session)
    assert "table_a" in tables
    assert "col_1" in cols["table_a"]

    # check_database_lineage_exact success and error
    mock_maker = MagicMock()
    mock_maker.return_value.__aenter__.return_value = mock_session
    mock_maker.return_value.__aexit__.return_value = None

    with (
        patch("app.core.runtime_readiness.fetch_live_alembic_revisions", new_callable=AsyncMock) as mock_fetch,
        patch("app.core.runtime_readiness.classify_database_lineage") as mock_classify,
    ):
        mock_fetch.return_value = ["head_1"]
        mock_classify.return_value = {"status": "ok"}
        res_lineage = await core_readiness.check_database_lineage_exact(mock_maker)
        assert res_lineage["status"] == "ok"

    with patch.object(mock_session, "execute", side_effect=Exception("DB lineage failure")):
        res_lineage_err = await core_readiness.check_database_lineage_exact(mock_maker)
        assert res_lineage_err["status"] == "error"

    # check_runtime_schema_contract success and error
    with (
        patch("app.core.runtime_readiness.fetch_public_schema_snapshot", new_callable=AsyncMock) as mock_snap,
        patch("app.core.runtime_readiness.validate_runtime_schema_contract") as mock_val,
    ):
        mock_snap.return_value = ({"guardians"}, {"guardians": set()})
        mock_val.return_value = {"status": "ok"}
        res_schema = await core_readiness.check_runtime_schema_contract(mock_maker)
        assert res_schema["status"] == "ok"

    with patch("app.core.runtime_readiness.fetch_public_schema_snapshot", side_effect=Exception("DB snapshot failure")):
        res_schema_err = await core_readiness.check_runtime_schema_contract(mock_maker)
        assert res_schema_err["status"] == "error"


# ── 4. HEALTH ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_checks_complete(monkeypatch):
    # _google_model_name
    with patch("app.core.health.settings.GOOGLE_MODEL", "models/gemini-2.0-flash"):
        assert core_health._google_model_name() == "gemini-2.0-flash"

    # check_postgres: success with pool metrics & error
    mock_session = AsyncMock()
    mock_maker = MagicMock()
    mock_maker.return_value.__aenter__.return_value = mock_session
    mock_maker.return_value.__aexit__.return_value = None

    with patch("app.core.health.AsyncSessionLocal", mock_maker):
        # success
        res_pg = await core_health.check_postgres()
        assert res_pg["status"] == "ok"

        # error
        mock_session.execute.side_effect = Exception("Connection refused")
        res_pg_err = await core_health.check_postgres()
        assert res_pg_err["status"] == "error"

    # check_redis: success & error
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.info.return_value = {"connected_clients": 5}
    with patch("app.core.health.get_redis", return_value=mock_redis):
        res_redis = await core_health.check_redis()
        assert res_redis["status"] == "ok"

        mock_redis.ping.side_effect = Exception("Redis unreachable")
        res_redis_err = await core_health.check_redis()
        assert res_redis_err["status"] == "error"

    # check_llm_provider: skipped, google, groq, anthropic
    with (
        patch("app.core.health.settings.GOOGLE_API_KEY", ""),
        patch("app.core.health.settings.GROQ_API_KEY", ""),
        patch("app.core.health.settings.ANTHROPIC_API_KEY", ""),
    ):
        res_skip = await core_health.check_llm_provider()
        assert res_skip["status"] == "skipped"

    # Google provider ok and error
    mock_resp_ok = MagicMock(status_code=200)
    mock_resp_ok.raise_for_status = MagicMock()
    with (
        patch("app.core.health.settings.GOOGLE_API_KEY", "g_key"),
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
    ):
        mock_get.return_value = mock_resp_ok
        res_g = await core_health.check_llm_provider()
        assert res_g["status"] == "ok"

        mock_get.side_effect = Exception("Google timeout")
        res_g_err = await core_health.check_llm_provider()
        assert res_g_err["status"] == "error"

    # Groq provider ok and error
    with (
        patch("app.core.health.settings.GOOGLE_API_KEY", ""),
        patch("app.core.health.settings.GROQ_API_KEY", "gr_key"),
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
    ):
        mock_get.return_value = mock_resp_ok
        res_gr = await core_health.check_llm_provider()
        assert res_gr["status"] == "ok"

        mock_get.side_effect = Exception("Groq error")
        res_gr_err = await core_health.check_llm_provider()
        assert res_gr_err["status"] == "error"

    # Anthropic provider ok and error
    with (
        patch("app.core.health.settings.GOOGLE_API_KEY", ""),
        patch("app.core.health.settings.GROQ_API_KEY", ""),
        patch("app.core.health.settings.ANTHROPIC_API_KEY", "ant_key"),
        patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get,
    ):
        mock_get.return_value = mock_resp_ok
        res_ant = await core_health.check_llm_provider()
        assert res_ant["status"] == "ok"

        mock_get.side_effect = Exception("Anthropic error")
        res_ant_err = await core_health.check_llm_provider()
        assert res_ant_err["status"] == "error"

    # check_required_secrets
    with (
        patch("app.core.health.settings.JWT_SECRET", "super_secret_jwt_32_characters_long"),
        patch("app.core.health.settings.DATABASE_URL", "postgresql://test"),
        patch("app.core.health.settings.REDIS_URL", "redis://test"),
    ):
        res_sec = await core_health.check_required_secrets()
        assert res_sec["status"] == "ok"

    with (
        patch("app.core.health.settings.JWT_SECRET", ""),
        patch("app.core.health.settings.DATABASE_URL", ""),
        patch("app.core.health.settings.REDIS_URL", ""),
    ):
        res_sec_err = await core_health.check_required_secrets()
        assert res_sec_err["status"] == "error"

    # check_postgres with engine.pool metrics
    mock_pool = MagicMock()
    mock_pool.checkedout.return_value = 2
    mock_pool.overflow.return_value = 1
    mock_engine_pool = MagicMock()
    mock_engine_pool.pool = mock_pool
    with (
        patch("app.core.health.AsyncSessionLocal", mock_maker),
        patch("app.core.database.engine", mock_engine_pool),
    ):
        mock_session.execute.side_effect = None
        res_pg_pool = await core_health.check_postgres()
        assert res_pg_pool["status"] == "ok"

    # check_required_secrets with JWT_SECRET_KEY
    monkeypatch.setattr(Settings, "JWT_SECRET_KEY", "jwt_key_32_characters_long_12345", raising=False)
    with (
        patch("app.core.health.settings.DATABASE_URL", "postgresql://test"),
        patch("app.core.health.settings.REDIS_URL", "redis://test"),
    ):
        assert (await core_health.check_required_secrets())["status"] == "ok"

    monkeypatch.setattr(Settings, "JWT_SECRET_KEY", "", raising=False)
    with (
        patch("app.core.health.settings.DATABASE_URL", "postgresql://test"),
        patch("app.core.health.settings.REDIS_URL", "redis://test"),
    ):
        assert (await core_health.check_required_secrets())["status"] == "error"
    monkeypatch.delattr(Settings, "JWT_SECRET_KEY", raising=False)

    # Direct calls to check_migrations and check_schema_contract
    with patch("app.core.health.check_database_lineage_exact", new_callable=AsyncMock, return_value={"status": "ok"}):
        assert (await core_health.check_migrations())["status"] == "ok"
    with patch("app.core.health.check_runtime_schema_contract", new_callable=AsyncMock, return_value={"status": "ok"}):
        assert (await core_health.check_schema_contract())["status"] == "ok"

    # check_judiciary success & error
    res_jud = await core_health.check_judiciary()
    assert res_jud["status"] == "ok"
    with patch("app.core.judiciary.JudiciaryService", side_effect=Exception("Judiciary probe error")):
        assert (await core_health.check_judiciary())["status"] == "error"

    # gather_deep_health
    with (
        patch("app.core.health.check_required_secrets", new_callable=AsyncMock, return_value={"status": "ok"}),
        patch("app.core.health.check_postgres", new_callable=AsyncMock, return_value={"status": "ok"}),
        patch("app.core.health.check_redis", new_callable=AsyncMock, return_value={"status": "ok"}),
        patch("app.core.health.check_migrations", new_callable=AsyncMock, return_value={"status": "ok"}),
        patch("app.core.health.check_schema_contract", new_callable=AsyncMock, return_value={"status": "ok"}),
        patch("app.core.health.check_audit_repository", new_callable=AsyncMock, return_value={"status": "ok"}),
        patch("app.core.health.check_llm_provider", new_callable=AsyncMock, return_value={"status": "ok"}),
        patch("app.core.health.check_judiciary", new_callable=AsyncMock, return_value={"status": "ok"}),
    ):
        # 1. All ok
        h_ok = await core_health.gather_deep_health()
        assert h_ok["status"] == "ok"
        assert "System is operational" in h_ok["message"]

        # 2. Critical error
        with patch("app.core.health.check_postgres", new_callable=AsyncMock, return_value={"status": "error"}):
            h_err = await core_health.gather_deep_health()
            assert h_err["status"] == "error"
            assert "System is unavailable" in h_err["message"]

        # 3. Optional degraded
        with patch("app.core.health.check_llm_provider", new_callable=AsyncMock, return_value={"status": "error"}):
            h_deg = await core_health.gather_deep_health()
            assert h_deg["status"] == "degraded"
            assert "degraded mode" in h_deg["message"]


# ── 5. CONFIG ─────────────────────────────────────────────────────────────────


def test_config_validators_and_methods():
    # _fetch_key_vault_secret_values
    mock_client = MagicMock()
    mock_client.get_secret.return_value = SimpleNamespace(value="secret_val")
    with (
        patch("azure.identity.DefaultAzureCredential"),
        patch("azure.keyvault.secrets.SecretClient", return_value=mock_client),
    ):
        kv_secrets = core_config._fetch_key_vault_secret_values("https://test.vault.azure.net/")
        assert kv_secrets["JWT_SECRET"] == "secret_val"

    # parse_allowed_origins
    assert Settings.parse_allowed_origins(["http://a.com", " "]) == ["http://a.com"]
    assert Settings.parse_allowed_origins("") == []
    assert Settings.parse_allowed_origins("http://a.com, http://b.com") == ["http://a.com", "http://b.com"]
    assert Settings.parse_allowed_origins('["http://c.com"]') == ["http://c.com"]

    with pytest.raises(ValueError, match="expected a list"):
        Settings.parse_allowed_origins('{"foo": "bar"}')
    with pytest.raises(ValueError, match="JSON format is invalid"):
        Settings.parse_allowed_origins('["broken json')
    with patch("json.loads", return_value={"not": "a_list"}):
        with pytest.raises(ValueError, match="JSON value must be a list"):
            Settings.parse_allowed_origins('["item"]')
    with pytest.raises(ValueError, match="must be a list or comma-separated string"):
        Settings.parse_allowed_origins(12345)

    # validate_jwt_secret
    assert Settings.validate_jwt_secret("test-jwt-secret") == "test-jwt-secret"
    assert Settings.validate_jwt_secret("a" * 32) == "a" * 32
    with pytest.raises(ValueError, match="at least 32 characters"):
        Settings.validate_jwt_secret("too_short_secret")

    # validate_encryption_key
    assert Settings.validate_encryption_key("test-key") == "test-key"
    assert Settings.validate_encryption_key("CHANGE_ME_NOW") == "CHANGE_ME_NOW"
    valid_enc_key = "A" * 44
    assert Settings.validate_encryption_key(valid_enc_key) == valid_enc_key
    with pytest.raises(ValueError, match="must be 44 characters"):
        Settings.validate_encryption_key("not_44_chars")

    # normalize_database_url
    assert Settings.normalize_database_url(123) == 123
    assert Settings.normalize_database_url("sqlite:///db.sqlite3") == "sqlite:///db.sqlite3"
    pg_url = "postgresql://usr:pwd@localhost:5432/db?sslmode=require&application_name=edu"
    norm_pg = Settings.normalize_database_url(pg_url)
    assert "postgresql+asyncpg://" in norm_pg
    assert "ssl=require" in norm_pg
    assert "application_name=edu" in norm_pg

    # is_production
    s_dev = Settings(APP_ENV="development", ENVIRONMENT="development")
    assert s_dev.is_production() is False
    assert s_dev.refresh_from_key_vault() == set()

    # refresh_from_key_vault in production
    with patch("app.core.config._fetch_key_vault_secret_values") as mock_fetch:
        mock_fetch.return_value = {
            "JWT_SECRET": "a" * 32,
            "ENCRYPTION_KEY": "B" * 44,
            "ENCRYPTION_SALT": "salt_val",
            "GROQ_API_KEY": "groq_val",
            "ANTHROPIC_API_KEY": "ant_val",
        }
        s_prod = Settings(
            APP_ENV="production",
            ENVIRONMENT="production",
            AZURE_KEY_VAULT_URL="https://test.vault.azure.net/",
        )
        mock_fetch.return_value = {
            "JWT_SECRET": "b" * 32,
            "ENCRYPTION_KEY": "C" * 44,
            "ENCRYPTION_SALT": "new_salt",
            "GROQ_API_KEY": "new_groq",
            "ANTHROPIC_API_KEY": "new_ant",
        }
        updated = s_prod.refresh_from_key_vault()
        assert "JWT_SECRET" in updated

        # Empty value from key vault
        mock_fetch.return_value = {"JWT_SECRET": ""}
        with pytest.raises(ValueError, match="empty value"):
            s_prod.refresh_from_key_vault()

    # Production validator raises if AZURE_KEY_VAULT_URL missing
    with pytest.raises(ValidationError):
        Settings(APP_ENV="production", AZURE_KEY_VAULT_URL="")

    # get_settings singleton
    s_inst = core_config.get_settings()
    assert s_inst is not None
