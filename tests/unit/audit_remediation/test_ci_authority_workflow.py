from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_remediation import verify_ci_authority_workflow
from scripts.audit_remediation import verify_ci_authority_workflow_evidence

ROOT = Path(__file__).resolve().parents[3]


def test_ci_cd_workflow_uses_pnpm_and_supported_actions() -> None:
    wf = ROOT / ".github/workflows/ci-cd.yml"
    if not wf.exists() and (ROOT / "archive/github_workflows/ci-cd.yml").exists():
        wf = ROOT / "archive/github_workflows/ci-cd.yml"
    text = wf.read_text(encoding="utf-8")
    assert "npm ci" not in text
    assert "package-lock.json" not in text
    assert "app/frontend/node_modules/.bin/playwright" not in text
    assert "actions/upload-artifact@v7" not in text
    assert "actions/setup-node@v6" not in text
    assert "actions/setup-python@v6" not in text
    assert "actions/upload-artifact@v4" in text
    assert "pnpm --dir app/frontend install --frozen-lockfile" in text
    assert "pnpm exec playwright test" in text
    assert "pnpm run env-check" in text


def test_phase04_verifier_accepts_current_workflow_contract() -> None:
    payload = verify_ci_authority_workflow.verify()
    assert payload["valid"] is True, payload
    assert len(payload["job_ids"]) == len(set(payload["job_ids"]))


def test_phase04_evidence_verifier_rejects_self_hash(tmp_path: Path) -> None:
    evidence = tmp_path / "ci-authority-workflow"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    (evidence / "evidence_index.md").write_text("# Evidence\n", encoding="utf-8")
    verification = {"valid": True, "findings": [{"valid": True, "message": "workflow job ids are unique"}, {"valid": True, "message": "required snippet present: actions/upload-artifact@v4"}, {"valid": True, "message": "required snippet present: pnpm --dir app/frontend install --frozen-lockfile"}, {"valid": True, "message": "required snippet present: pnpm exec playwright test"}, {"valid": True, "message": "TA-CI-001 blocker registered"}]}
    (raw / "ci_authority_workflow_verification.json").write_text(json.dumps(verification), encoding="utf-8")
    (raw / "ci_authority_workflow_evidence_check.json").write_text("{}", encoding="utf-8")
    digest = hashlib.sha256((raw / "ci_authority_workflow_evidence_check.json").read_bytes()).hexdigest()
    (raw / "SHA256SUMS.txt").write_text(f"{digest}  ci_authority_workflow_evidence_check.json\n", encoding="utf-8")
    payload = verify_ci_authority_workflow_evidence.verify(evidence)
    assert payload["valid"] is False
    assert any("must not be self-hashed" in finding["message"] for finding in payload["findings"])


def test_phase04_evidence_verifier_accepts_minimal_complete_bundle(tmp_path: Path) -> None:
    evidence = tmp_path / "ci-authority-workflow"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    (evidence / "evidence_index.md").write_text("# Evidence\n", encoding="utf-8")
    verification = {
        "valid": True,
        "findings": [
            {"valid": True, "message": "workflow job ids are unique"},
            {"valid": True, "message": "required snippet present: actions/upload-artifact@v4"},
            {"valid": True, "message": "required snippet present: pnpm --dir app/frontend install --frozen-lockfile"},
            {"valid": True, "message": "required snippet present: pnpm exec playwright test"},
            {"valid": True, "message": "TA-CI-001 blocker registered"},
        ],
    }
    target = raw / "ci_authority_workflow_verification.json"
    target.write_text(json.dumps(verification), encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (raw / "SHA256SUMS.txt").write_text(f"{digest}  ci_authority_workflow_verification.json\n", encoding="utf-8")
    payload = verify_ci_authority_workflow_evidence.verify(evidence)
    assert payload["valid"] is True, payload
