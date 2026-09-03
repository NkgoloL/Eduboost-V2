from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.deep_readiness_readonly import (
    DEFAULT_READINESS_SPECS,
    ReadinessCheckResult,
    ReadinessCheckSpec,
    ReadinessSeverity,
    assert_read_only_operation,
    run_read_only_probe,
    summarize_specs,
)
from app.services.deep_readiness_route_contracts import (
    public_deep_readiness_checks,
    release_required_checks,
    unsafe_public_checks,
)
from app.services.deep_readiness_runtime import (
    DeepReadinessCheckResult,
    DeepReadinessRuntimeResult,
    _execute,
    run_deep_readiness_runtime_checks,
)


def test_deep_readiness_readonly_complete():
    # 1. assert_read_only_operation
    assert_read_only_operation("SELECT * FROM users")  # Passes

    with pytest.raises(ValueError, match="not read-only"):
        assert_read_only_operation("session.commit()")

    with pytest.raises(ValueError, match="not read-only"):
        assert_read_only_operation("INSERT INTO users VALUES (1)")

    # 2. summarize_specs
    summary = summarize_specs()
    assert summary["total"] == len(DEFAULT_READINESS_SPECS)
    assert summary["required"] > 0
    assert summary["read_only"] is True
    assert "database_connectivity" in summary["names"]

    # 3. run_read_only_probe
    def good_probe():
        return {"ping": "pong"}

    res_good = run_read_only_probe("ping_probe", good_probe)
    assert res_good.passed is True
    assert res_good.read_only is True
    assert res_good.details["value"] == {"ping": "pong"}

    def empty_probe():
        return None

    res_none = run_read_only_probe("none_probe", empty_probe)
    assert res_none.passed is True


def test_deep_readiness_route_contracts_complete():
    # 1. public_deep_readiness_checks (line 76)
    public_checks = public_deep_readiness_checks()
    assert isinstance(public_checks, tuple)
    assert all(c.public_safe and not c.mutates_state for c in public_checks)

    # 2. unsafe_public_checks (line 84)
    unsafe_checks = unsafe_public_checks()
    assert isinstance(unsafe_checks, tuple)
    assert all(c.public_safe and c.mutates_state for c in unsafe_checks)

    # 3. release_required_checks (line 92)
    release_checks = release_required_checks()
    assert isinstance(release_checks, tuple)
    assert all(c.required_for_release for c in release_checks)


@pytest.mark.asyncio
async def test_deep_readiness_runtime_complete():
    # 1. _execute with None session (lines 25-26)
    assert await _execute(None, "SELECT 1") is None

    # 2. to_dict on DeepReadinessRuntimeResult (lines 20-21)
    res = DeepReadinessRuntimeResult("pass", (DeepReadinessCheckResult("chk", "pass", "ok"),))
    d = res.to_dict()
    assert d["status"] == "pass"
    assert len(d["checks"]) == 1

    # 3. run_deep_readiness_runtime_checks with failing database connectivity (lines 42-43)
    mock_failing_db = AsyncMock()
    mock_failing_db.execute.side_effect = RuntimeError("DB connection refused")

    res_failing = await run_deep_readiness_runtime_checks(
        db_session=mock_failing_db,
        required_tables=("users",),
    )
    assert res_failing.status == "fail"
    db_check = next(c for c in res_failing.checks if c.name == "database_connectivity")
    assert db_check.status == "fail"

    # 4. run_deep_readiness_runtime_checks with alembic and table warnings (lines 47-48, 53-54)
    # First call (SELECT 1) succeeds, subsequent fail
    call_count = 0
    async def mock_selective_execute(sql):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            mock_res = MagicMock()
            mock_res.scalar.return_value = 1
            return mock_res
        raise RuntimeError("Table missing")

    mock_partial_db = MagicMock()
    mock_partial_db.execute = mock_selective_execute

    # Cache client with async ping (lines 56-61)
    mock_cache = MagicMock()
    mock_cache.ping = AsyncMock(return_value="PONG")

    res_partial = await run_deep_readiness_runtime_checks(
        db_session=mock_partial_db,
        cache_client=mock_cache,
        required_tables=("users",),
    )
    # database_connectivity passed, alembic and table warned, cache passed
    assert res_partial.status == "pass"
    names = {c.name for c in res_partial.checks}
    assert "cache_ping" in names
    assert "table:users" in names
