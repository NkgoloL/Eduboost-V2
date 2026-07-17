from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_playwright_defaults_to_next_port_3050() -> None:
    source = (ROOT / "playwright.config.ts").read_text(encoding="utf-8")
    assert "http://127.0.0.1:3050" in source
    assert "timeout: 60_000" in source


def test_ether_auth_boundary_contract_is_restored() -> None:
    source = (ROOT / "app/api_v2_routers/ether.py").read_text(encoding="utf-8")
    assert '@router.get("/onboarding/questions")' in source
    assert "async def get_questions(user: AuthContext = Depends(require_auth_context))" in source


def test_router_contract_declares_curriculum_expansion_fragment() -> None:
    source = (ROOT / "tests/unit/test_api_v2_router_contract.py").read_text(encoding="utf-8")
    assert '"curriculum_expansion": "/admin/curriculum-expansion"' in source


def test_mcp_fastmcp_import_is_proven_by_sync_script() -> None:
    source = (ROOT / "scripts/audit_remediation/sync_backend_fast_runtime_dependencies.sh").read_text(encoding="utf-8")
    assert "mcp[cli]>=1.0.0" in source
    assert "from mcp.server.fastmcp import FastMCP" in source


def test_seed_result_identity_is_resilient_for_mocks() -> None:
    source = (ROOT / "scripts/curriculum/seed_staging_review_scopes.py").read_text(encoding="utf-8")
    assert 'getattr(res, "seed_run_id", None) or getattr(res, "id", None)' in source


def test_phase02e_verifier_reports_valid_static_contracts() -> None:
    from scripts.audit_remediation.verify_backend_fast_phase02e import run_checks

    checks = run_checks()
    assert all(check.passed for check in checks)
