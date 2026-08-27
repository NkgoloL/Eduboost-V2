from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_rr003_register_item_exists() -> None:
    text = (ROOT / "docs/roadmap/reconciliation/outstanding_work_register.md").read_text(encoding="utf-8")
    assert "RR-003" in text
    assert "Coverage / CI / route authority" in text


def test_rr003_release_policy_documents_route_and_ci_authority() -> None:
    text = (ROOT / "docs/release/coverage_ci_route_authority.md").read_text(encoding="utf-8")
    assert "Coverage baseline required" in text
    assert "Release-blocking checks visible in CI" in text
    assert "`/api/v2` is canonical" in text
    assert "`/v2` is compatibility-only" in text


def test_rr003_workflow_exposes_release_checks() -> None:
    wf = ROOT / ".github/workflows/rr003-release-authority.yml"
    if not wf.exists():
        wf = ROOT / "archive/github_workflows/rr003-release-authority.yml"
    text = wf.read_text(encoding="utf-8")
    assert "RR-003 Release Authority" in text
    assert "make test-fast" in text
    assert "make route-alias-policy-check" in text
    assert "make openapi-check" in text


def test_rr003_dormant_router_inventory_exists() -> None:
    text = (ROOT / "docs/release/dormant_router_inventory.md").read_text(encoding="utf-8")
    assert "Dormant Router Inventory" in text
    assert "app/modules/diagnostics/bias_review_router.py" in text
    assert "app/modules/lessons/lesson_coverage_router.py" in text
    assert "app/modules/lessons/lesson_review_router.py" in text
    assert "app/modules/practice/router.py" in text


def test_rr003_verifier_passes() -> None:
    from scripts.roadmap_reconciliation.verify_rr003_coverage_ci_route_authority import verify

    result = verify()
    assert result["valid"], result["errors"]
