from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_rr002_register_item_exists() -> None:
    text = (ROOT / "docs/roadmap/reconciliation/outstanding_work_register.md").read_text(encoding="utf-8")
    assert "RR-002" in text
    assert "Privacy / POPIA" in text


def test_erasure_safety_helper_contains_required_controls() -> None:
    text = (ROOT / "app/services/popia_erasure_safety.py").read_text(encoding="utf-8")
    assert "build_erasure_preflight_decision" in text
    assert "legal_hold_checked=True" in text
    assert "export_requirement_satisfied" in text
    assert "preserve_audit_records=True" in text


def test_popia_service_persists_export_and_legal_hold_preflight() -> None:
    text = (ROOT / "app/services/popia_service.py").read_text(encoding="utf-8")
    assert 'export_offered=preflight_result.get("export_offered", False)' in text
    assert '"export_offered": preflight_result.get("export_offered", False)' in text
    assert '"preserve_audit_records": True' in text


def test_legacy_delete_routes_use_canonical_popia_state_machine() -> None:
    for rel in ("app/api_v2_routers/learners.py", "app/api_v2_routers/parents.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "POPIADataRightsService" in text
        assert "status.HTTP_202_ACCEPTED" in text
        assert "request_erasure(learner_id=learner_id" in text


def test_rr002_verifier_passes() -> None:
    from scripts.roadmap_reconciliation.verify_rr002_privacy_popia_completion import verify

    result = verify()
    assert result["valid"], result["errors"]
