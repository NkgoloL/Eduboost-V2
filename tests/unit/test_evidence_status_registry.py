from __future__ import annotations

from pathlib import Path

from scripts.evidence_registry import load_registry, validate_registry


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def test_evidence_status_registry_loads_required_findings():
    findings = load_registry(REGISTRY)
    ids = {finding.id for finding in findings}

    assert {"JWT-001", "ARQ-001", "POPIA-001", "EVID-001", "DIAG-001"}.issubset(ids)


def test_evidence_status_registry_validates():
    findings = load_registry(REGISTRY)

    assert validate_registry(findings, ROOT) == []


def test_p0_p1_static_passing_is_not_allowed():
    findings = load_registry(REGISTRY)
    for finding in findings:
        assert not (finding.severity in {"P0", "P1"} and finding.proof_status == "static-passing")


def test_skipped_popia_proof_is_not_misclassified_as_closed():
    findings = {finding.id: finding for finding in load_registry(REGISTRY)}

    assert findings["POPIA-001"].proof_status == "not-proven"
    assert "skipped" in (findings["POPIA-001"].closure_blocker or "").lower()


def test_release_blockers_are_tracked_as_external_blocked():
    findings = {finding.id: finding for finding in load_registry(REGISTRY)}

    for item in ["LEGAL-001", "SEC-001", "CONTENT-001"]:
        assert findings[item].external_dependency is True
        assert findings[item].blocks_beta is True
        assert findings[item].proof_status == "external-blocked"
