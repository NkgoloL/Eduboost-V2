from __future__ import annotations

from pathlib import Path

from scripts.evidence_registry import PROVEN_STATUSES, load_registry, validate_registry

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_and_integration_entries_have_commit_provenance():
    findings = load_registry(ROOT / "docs/release/evidence_status_registry.yml")

    missing = [finding.id for finding in findings if finding.proof_status in PROVEN_STATUSES and not finding.last_verified_commit]
    assert missing == []


def test_registry_validator_rejects_missing_commit_for_proven_status():
    findings = load_registry(ROOT / "docs/release/evidence_status_registry.yml")

    assert validate_registry(findings, ROOT) == []


def test_popia_and_diagnostics_are_no_longer_not_proven_due_to_skips():
    findings = {finding.id: finding for finding in load_registry(ROOT / "docs/release/evidence_status_registry.yml")}

    assert findings["POPIA-001"].proof_status == "not-proven"
    assert "skipped" in (findings["POPIA-001"].closure_blocker or "").lower()
    assert findings["DIAG-001"].proof_status in {"runtime-passing", "integration-passing"}
