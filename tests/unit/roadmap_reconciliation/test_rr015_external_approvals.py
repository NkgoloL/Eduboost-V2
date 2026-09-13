from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr015_external_approvals.py"
    spec = importlib.util.spec_from_file_location("verify_rr015", module_path)
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
        ".github/workflows/rr015-external-approvals.yml",
        "scripts/approvals/audit_rr015_external_approvals.py",
        "scripts/roadmap_reconciliation/verify_rr015_external_approvals.py",
        "scripts/roadmap_reconciliation/capture_rr015_external_approvals_evidence.py",
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_014_public_beta_expansion_record.json",
        "docs/roadmap/reconciliation/rr_015_external_approvals.md",
        "docs/roadmap/reconciliation/rr_015_external_approvals_record.json",
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
    shutil.copytree(source / "docs/approvals", target / "docs/approvals", dirs_exist_ok=True)


def _write_final_files(root: Path) -> None:
    base = root / "docs/approvals"
    base.mkdir(parents=True, exist_ok=True)
    (base / "rr015_security_review_attestation.md").write_text(
        """# RR-015 Security Review Attestation

Security review approved: true
Security reviewer named: true
Security evidence URL recorded: true
Security review date recorded: true
Critical security blockers open: false
""",
        encoding="utf-8",
    )
    (base / "rr015_popia_privacy_review_attestation.md").write_text(
        """# RR-015 POPIA Privacy Review Attestation

POPIA/privacy review approved: true
POPIA reviewer named: true
POPIA evidence URL recorded: true
POPIA review date recorded: true
Critical POPIA/privacy blockers open: false
""",
        encoding="utf-8",
    )
    (base / "rr015_legal_review_attestation.md").write_text(
        """# RR-015 Legal Review Attestation

Legal review approved: true
Legal reviewer named: true
Legal evidence URL recorded: true
Legal review date recorded: true
Critical legal blockers open: false
""",
        encoding="utf-8",
    )
    (base / "rr015_caps_content_review_attestation.md").write_text(
        """# RR-015 CAPS Content Review Attestation

CAPS/content review approved: true
Curriculum reviewer named: true
CAPS/content evidence URL recorded: true
CAPS/content review date recorded: true
Critical curriculum/content blockers open: false
""",
        encoding="utf-8",
    )
    (base / "rr015_release_owner_go_no_go_signoff.md").write_text(
        """# RR-015 Release Owner Go/No-Go Signoff

Release-owner go/no-go signoff recorded: true
Release owner named: true
Release-owner evidence URL recorded: true
Release-owner decision date recorded: true
Release-owner decision: proceed-to-next-governance-gate
""",
        encoding="utf-8",
    )
    (base / "rr015_external_approval_boundary.md").write_text(
        """# RR-015 External Approval Boundary

External approval boundary recorded: true
External approvals complete: true
Repository-only approval substitution allowed: false
Public beta expansion authorised: false
Public beta live traffic authorised: false
Production release authorised: false
Runtime KG implementation claimed: false
""",
        encoding="utf-8",
    )


def test_rr015_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True, result


def test_rr015_record_becomes_valid_after_final_files_and_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    _copy_minimal_repo(source, target)
    _write_final_files(target)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_015_external_approvals_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "external_approvals_recorded": True,
            "rr014_public_beta_expansion_valid": True,
            "security_review_approved": True,
            "popia_privacy_review_approved": True,
            "legal_review_approved": True,
            "caps_content_review_approved": True,
            "release_owner_go_no_go_signoff_recorded": True,
            "external_approval_boundary_recorded": True,
            "repository_only_approval_substitution_blocked": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "rr017_release_safety_controls_remaining_visible": True,
            "rr018_trustworthy_beta_quality_remaining_visible": True,
            "external_approvals_audit": {"valid": True, "final_outputs_valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr015_audit_rejects_missing_final_files_when_required(tmp_path: Path) -> None:
    source = Path.cwd()
    root = tmp_path / "repo"
    _copy_minimal_repo(source, root)
    for path in (
        "rr015_security_review_attestation.md",
        "rr015_popia_privacy_review_attestation.md",
        "rr015_legal_review_attestation.md",
        "rr015_caps_content_review_attestation.md",
        "rr015_release_owner_go_no_go_signoff.md",
        "rr015_external_approval_boundary.md",
    ):
        (root / "docs/approvals" / path).unlink()
    audit_path = root / "scripts/approvals/audit_rr015_external_approvals.py"
    spec = importlib.util.spec_from_file_location("audit_rr015", audit_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit(root, require_final=True)
    assert result["authority_valid"] is True, result
    assert result["final_outputs_valid"] is False
    assert any("missing final RR-015 evidence file" in error for error in result["errors"])


def test_rr015_policy_carries_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/approvals/rr015_external_approvals_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "non-required" in policy
    assert "RR-016" in policy
    assert "RR-017" in policy
    assert "RR-018" in policy
    assert "Public beta expansion authorised: false" in policy
    assert "Runtime KG implementation claimed: false" in policy


def test_rr015_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr015-external-approvals-audit" in text
    assert "rr015-external-approvals-check" in text
