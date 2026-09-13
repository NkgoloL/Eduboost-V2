from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr014_public_beta_expansion.py"
    spec = importlib.util.spec_from_file_location("verify_rr014", module_path)
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
        ".github/workflows/rr014-public-beta-expansion.yml",
        "scripts/public_beta/audit_rr014_public_beta_expansion.py",
        "scripts/roadmap_reconciliation/verify_rr014_public_beta_expansion.py",
        "scripts/roadmap_reconciliation/capture_rr014_public_beta_expansion_evidence.py",
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research_record.json",
        "docs/roadmap/reconciliation/rr_014_public_beta_expansion.md",
        "docs/roadmap/reconciliation/rr_014_public_beta_expansion_record.json",
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
    shutil.copytree(source / "docs/public_beta", target / "docs/public_beta", dirs_exist_ok=True)


def _write_final_files(root: Path) -> None:
    base = root / "docs/public_beta"
    base.mkdir(parents=True, exist_ok=True)
    (base / "rr014_public_beta_expansion_readiness_plan.md").write_text(
        """# RR-014 Public Beta Expansion Readiness Plan

Public beta expansion readiness recorded: true
Controlled beta outcome reviewed: true
Public beta scope bounded: true
Public beta success metrics defined: true
Public beta rollback criteria defined: true
""",
        encoding="utf-8",
    )
    (base / "rr014_public_beta_cohort_plan.json").write_text(
        json.dumps(
            {
                "public_beta_cohort_plan_recorded": True,
                "initial_public_beta_cohort_bounded": True,
                "initial_public_beta_cohort_size": 50,
                "phased_rollout_required": True,
                "guardian_consent_required": True,
                "educator_or_support_monitoring_required": True,
                "public_beta_expansion_authorised": False,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (base / "rr014_public_beta_consent_and_privacy_attestation.md").write_text(
        """# RR-014 Consent and Privacy Attestation

Consent and privacy attestation recorded: true
POPIA/privacy review required before public beta activation: true
No learner PII exposed in public beta evidence: true
Guardian consent update path defined: true
Data subject rights path confirmed: true
""",
        encoding="utf-8",
    )
    (base / "rr014_public_beta_support_and_incident_plan.md").write_text(
        """# RR-014 Support and Incident Plan

Support and incident plan recorded: true
Support escalation path defined: true
Incident response path linked: true
Public beta support owner assigned: true
Critical incident rollback trigger defined: true
""",
        encoding="utf-8",
    )
    (base / "rr014_public_beta_launch_boundary.md").write_text(
        """# RR-014 Public Beta Launch Boundary

Public beta launch boundary recorded: true
Public beta expansion authorised: false
Public beta live traffic authorised: false
Expanded learner data migration authorised: false
Production release authorised: false
Runtime KG implementation claimed: false
""",
        encoding="utf-8",
    )


def test_rr014_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True, result


def test_rr014_record_becomes_valid_after_final_files_and_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    _copy_minimal_repo(source, target)
    _write_final_files(target)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_014_public_beta_expansion_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "public_beta_expansion_readiness_recorded": True,
            "rr013_advanced_mastery_model_research_valid": True,
            "expansion_planning_boundary_recorded": True,
            "controlled_beta_outcome_reviewed": True,
            "public_beta_scope_bounded": True,
            "public_beta_success_metrics_defined": True,
            "public_beta_rollback_criteria_defined": True,
            "public_beta_cohort_plan_recorded": True,
            "consent_privacy_attestation_recorded": True,
            "support_incident_plan_recorded": True,
            "public_beta_launch_boundary_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "rr017_release_safety_controls_remaining_visible": True,
            "rr018_trustworthy_beta_quality_remaining_visible": True,
            "public_beta_expansion_audit": {"valid": True, "final_outputs_valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr014_audit_rejects_missing_final_files_when_required(tmp_path: Path) -> None:
    source = Path.cwd()
    root = tmp_path / "repo"
    _copy_minimal_repo(source, root)
    for path in (
        "rr014_public_beta_expansion_readiness_plan.md",
        "rr014_public_beta_cohort_plan.json",
        "rr014_public_beta_consent_and_privacy_attestation.md",
        "rr014_public_beta_support_and_incident_plan.md",
        "rr014_public_beta_launch_boundary.md",
    ):
        (root / "docs/public_beta" / path).unlink()
    audit_path = root / "scripts/public_beta/audit_rr014_public_beta_expansion.py"
    spec = importlib.util.spec_from_file_location("audit_rr014", audit_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit(root, require_final=True)
    assert result["authority_valid"] is True, result
    assert result["final_outputs_valid"] is False
    assert any("missing final RR-014 evidence file" in error or "missing or invalid final RR-014 evidence file" in error for error in result["errors"])


def test_rr014_policy_carries_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/public_beta/rr014_public_beta_expansion_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "non-required" in policy
    assert "RR-015" in policy
    assert "RR-016" in policy
    assert "RR-017" in policy
    assert "RR-018" in policy
    assert "Public beta expansion authorised: false" in policy
    assert "Runtime KG implementation claimed: false" in policy


def test_rr014_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr014-public-beta-expansion-audit" in text
    assert "rr014-public-beta-expansion-check" in text
