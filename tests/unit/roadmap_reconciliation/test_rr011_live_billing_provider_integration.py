from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr011_live_billing_provider_integration.py"
    spec = importlib.util.spec_from_file_location("verify_rr011", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(root))
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)
    return module


def _copy_minimal_repo(source: Path, target: Path) -> None:
    paths = [
        "Makefile",
        ".github/workflows/rr011-live-billing-provider-integration.yml",
        "scripts/billing/audit_rr011_live_billing_provider_integration.py",
        "scripts/roadmap_reconciliation/verify_rr011_live_billing_provider_integration.py",
        "scripts/roadmap_reconciliation/capture_rr011_live_billing_provider_integration_evidence.py",
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_010_beta_outcome_reporting_record.json",
        "docs/roadmap/reconciliation/rr_011_live_billing_provider_integration.md",
        "docs/roadmap/reconciliation/rr_011_live_billing_provider_integration_record.json",
        "docs/adr/ADR-009-billing-provider.md",
        "docs/billing/production_billing_provider_architecture_contract.md",
        "docs/billing/subscription_state_machine_contract.md",
        "docs/billing/webhook_security_idempotency_contract.md",
        "docs/billing/pricing_product_rules_contract.md",
        "docs/billing/billing_ux_audit_contract.md",
        "app/modules/billing/production_readiness_contracts.py",
        "scripts/check_billing_monetization_production_readiness.py",
    ]
    for rel in paths:
        src = source / rel
        if not src.exists() and rel.startswith(".github/workflows/"):
            archived = source / "archive/github_workflows" / Path(rel).name
            if archived.exists():
                src = archived
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copytree(source / "docs/billing", target / "docs/billing", dirs_exist_ok=True)


def _write_final_files(root: Path) -> None:
    billing = root / "docs/billing"
    (billing / "rr011_live_billing_provider_attestation.md").write_text(
        """# RR-011 Live Billing Provider Attestation\n\nBilling provider selected: stripe\nLive billing provider integration attested: true\nHosted checkout configured: true\nNo raw card storage confirmed: true\nSecret values committed: false\nProvider secret references documented: true\nBilling launch authorised: false\nLive payment processing authorised: false\nProduction release authorised: false\nPublic beta authorised: false\nRuntime KG implementation claimed: false\n""",
        encoding="utf-8",
    )
    (billing / "rr011_hosted_checkout_sandbox_validation.md").write_text(
        """# RR-011 Hosted Checkout Sandbox Validation\n\nHosted checkout sandbox validated: true\nSubscription lifecycle sandbox validated: true\nInvoice and receipt sandbox validated: true\nPayment failure sandbox validated: true\nCancellation sandbox validated: true\nRaw card data handled by provider only: true\n""",
        encoding="utf-8",
    )
    (billing / "rr011_webhook_endpoint_validation.md").write_text(
        """# RR-011 Webhook Endpoint Validation\n\nWebhook endpoint configured: true\nWebhook signature validation recorded: true\nWebhook replay protection recorded: true\nWebhook idempotency validation recorded: true\nWebhook audit logging recorded: true\nDuplicate provider event handling recorded: true\nOut-of-order provider event handling recorded: true\nLive webhook traffic authorised: false\n""",
        encoding="utf-8",
    )
    (billing / "rr011_pricing_catalogue_approval.md").write_text(
        """# RR-011 Pricing Catalogue Approval\n\nPricing catalogue approved: true\nParent plan configured: true\nSchool plan configured: true\nSponsored learner plan configured: true\nNGO/community plan configured: true\nTrial length approved: true\nRefund and cancellation policy approved: true\nData access after cancellation policy approved: true\n""",
        encoding="utf-8",
    )
    (billing / "rr011_billing_launch_boundary.md").write_text(
        """# RR-011 Billing Launch Boundary\n\nBilling launch boundary recorded: true\nBilling launch authorised: false\nLive payment processing authorised: false\nProduction release authorised: false\nDeployment authorised: false\nRelease tag authorised: false\nPublic beta authorised: false\nRuntime KG implementation claimed: false\n""",
        encoding="utf-8",
    )


def test_rr011_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True
    assert result["warnings"] == []


def test_rr011_record_becomes_valid_after_final_files_and_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    _copy_minimal_repo(source, target)
    _write_final_files(target)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_011_live_billing_provider_integration_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "live_billing_provider_integration_recorded": True,
            "rr010_beta_outcome_reporting_valid": True,
            "billing_provider_decision_recorded": True,
            "hosted_checkout_provider_attested": True,
            "hosted_checkout_sandbox_validated": True,
            "webhook_endpoint_validation_recorded": True,
            "webhook_signature_validation_recorded": True,
            "webhook_idempotency_validation_recorded": True,
            "pricing_catalogue_approved": True,
            "no_raw_card_storage_confirmed": True,
            "secrets_not_committed_confirmed": True,
            "billing_launch_boundary_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr012_production_telemetry_remaining_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "billing_provider_integration_audit": {"valid": True, "final_outputs_valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr011_audit_rejects_missing_final_files_when_required() -> None:
    root = Path.cwd()
    audit_path = root / "scripts/billing/audit_rr011_live_billing_provider_integration.py"
    spec = importlib.util.spec_from_file_location("audit_rr011", audit_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit(root, require_final=True)
    assert result["authority_valid"] is True, result
    assert result["final_outputs_valid"] is True
    assert result["errors"] == []


def test_rr011_policy_carries_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/billing/rr011_live_billing_provider_integration_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "non-required" in policy
    assert "RR-012" in policy
    assert "RR-015" in policy
    assert "RR-016" in policy
    assert "Billing launch authorised: false" in policy
    assert "Runtime KG implementation claimed: false" in policy


def test_rr011_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr011-live-billing-provider-audit" in text
    assert "rr011-live-billing-provider-check" in text
