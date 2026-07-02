from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_popia_service_uses_async_safe_db_add_helper() -> None:
    source = (ROOT / "app/services/popia_service.py").read_text()
    assert "async def _maybe_await(value: Any) -> Any:" in source
    assert "async def _add(self, *objects: Any) -> None:" in source
    assert "await _maybe_await(self.db.add(obj))" in source
    direct_adds = [line for line in source.splitlines() if "self.db.add(" in line and "await _maybe_await" not in line]
    assert direct_adds == []


def test_popia_mutations_go_through_async_safe_add() -> None:
    source = (ROOT / "app/services/popia_service.py").read_text()
    assert source.count("await self._add(erasure_request)") >= 3
    assert source.count("await self._add(learner)") >= 3


def test_learner_repository_soft_delete_tolerates_asyncmock_add() -> None:
    source = (ROOT / "app/repositories/learner_repository.py").read_text()
    assert "import inspect" in source
    assert "add_result = db.add(learner)" in source
    assert "if inspect.isawaitable(add_result):" in source
    assert "await add_result" in source


def test_phase02g_blocker_register_records_non_scope() -> None:
    source = (ROOT / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json").read_text()
    assert "phase_02g_slice" in source
    assert "popia_async_route_contract" in source
    assert "No runtime knowledge-graph implementation" in source
