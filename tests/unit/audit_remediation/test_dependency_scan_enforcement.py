from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scripts.audit_remediation import verify_dependency_scan_enforcement, verify_dependency_scan_evidence
ROOT = Path(__file__).resolve().parents[3]

def test_dependency_scan_workflow_fails_closed_and_uses_supported_artifact_action() -> None:
    wf = ROOT / ".github/workflows/dependency-scan.yml"
    if not wf.exists() and (ROOT / "archive/github_workflows/dependency-scan.yml").exists():
        wf = ROOT / "archive/github_workflows/dependency-scan.yml"
    text = wf.read_text(encoding="utf-8")
    assert "|| true" not in text
    assert "actions/upload-artifact@v7" not in text
    assert "actions/upload-artifact@v4" in text
    assert "steps.publish.outputs.result_url" not in text
    assert "set -euo pipefail" in text
    assert "pnpm audit --audit-level=critical --json" in text
    assert "fail-on-severity: critical" in text
    assert "process.exitCode = 1" in text

def test_dependency_scan_verifier_accepts_current_contract() -> None:
    payload = verify_dependency_scan_enforcement.verify()
    assert payload["valid"] is True, payload
    messages = "\n".join(item["message"] for item in payload["findings"])
    assert "pip-audit uses fail-closed shell options" in messages
    assert "pnpm-audit uses fail-closed shell options" in messages
    assert "all dependency scan artifact uploads use v4" in messages

def test_dependency_scan_evidence_verifier_rejects_self_hash(tmp_path: Path) -> None:
    evidence = tmp_path / "dependency-scan-enforcement"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    (evidence / "evidence_index.md").write_text("# Evidence\n", encoding="utf-8")
    verification = {"valid": True, "findings": [
        {"valid": True, "message": "pip-audit uses fail-closed shell options"},
        {"valid": True, "message": "pnpm-audit uses fail-closed shell options"},
        {"valid": True, "message": "pnpm critical vulnerabilities fail the job"},
        {"valid": True, "message": "all dependency scan artifact uploads use v4"},
        {"valid": True, "message": "TA-SECURITY-001 blocker registered"},
    ]}
    (raw / "dependency_scan_enforcement_verification.json").write_text(json.dumps(verification), encoding="utf-8")
    (raw / "dependency-scan.yml.snapshot").write_text("actions/upload-artifact@v4\nset -euo pipefail\n", encoding="utf-8")
    (raw / "dependency_scan_evidence_check.json").write_text("{}", encoding="utf-8")
    digest = hashlib.sha256((raw / "dependency_scan_evidence_check.json").read_bytes()).hexdigest()
    (raw / "SHA256SUMS.txt").write_text(f"{digest}  dependency_scan_evidence_check.json\n", encoding="utf-8")
    payload = verify_dependency_scan_evidence.verify(evidence)
    assert payload["valid"] is False
    assert any("must not be self-hashed" in finding["message"] for finding in payload["findings"])

def test_dependency_scan_evidence_verifier_accepts_minimal_complete_bundle(tmp_path: Path) -> None:
    evidence = tmp_path / "dependency-scan-enforcement"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    (evidence / "evidence_index.md").write_text("# Evidence\n", encoding="utf-8")
    verification = {"valid": True, "findings": [
        {"valid": True, "message": "pip-audit uses fail-closed shell options"},
        {"valid": True, "message": "pnpm-audit uses fail-closed shell options"},
        {"valid": True, "message": "pnpm critical vulnerabilities fail the job"},
        {"valid": True, "message": "all dependency scan artifact uploads use v4"},
        {"valid": True, "message": "TA-SECURITY-001 blocker registered"},
    ]}
    verification_path = raw / "dependency_scan_enforcement_verification.json"
    snapshot_path = raw / "dependency-scan.yml.snapshot"
    verification_path.write_text(json.dumps(verification), encoding="utf-8")
    snapshot_path.write_text("actions/upload-artifact@v4\nset -euo pipefail\n", encoding="utf-8")
    lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in (snapshot_path, verification_path)]
    (raw / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = verify_dependency_scan_evidence.verify(evidence)
    assert payload["valid"] is True, payload
