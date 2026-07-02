from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_seed_executor_uses_safe_session_helpers_and_returns_result() -> None:
    source = read("app/services/content_staging_seed_executor.py")
    assert "async def _session_commit" in source
    assert "async def _session_rollback" in source
    assert "await _session_commit(session)" in source
    assert "return StagingSeedRunResult(" in source
    assert "seeded_count=seeded_count" in source


def test_diagnostic_item_selection_defaults_missing_irt_state() -> None:
    model = read("app/models/diagnostic_item.py")
    service = read("app/modules/diagnostics/item_bank_service.py")
    assert 'quality_state = self.irt_quality_state or "uncalibrated"' in model
    assert "if not isinstance(state, str) or not state:" in service
    assert 'state = "uncalibrated"' in service


def test_router_contract_declares_tutor_fragment() -> None:
    source = read("tests/unit/test_api_v2_router_contract.py")
    assert '"tutor": "/tutor"' in source


def test_study_plan_db_import_contract_is_preserved() -> None:
    source = read("app/api_v2_routers/study_plans.py")
    assert "from app.core.database import AsyncSessionLocal, get_db" in source
    assert "db: AsyncSession = Depends(get_db)" in source


def test_phase02f_doc_preserves_backend_fast_and_kg_boundaries() -> None:
    source = read("docs/roadmap/execution/technical_audit_remediation/02f_backend_fast_item_seed_router.md")
    assert "No passing backend-fast evidence" in source
    assert "No runtime knowledge-graph implementation" in source
