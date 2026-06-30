from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_remediation.verify_frontend_tooling_authority import run_checks
from scripts.audit_remediation.verify_frontend_tooling_evidence import verify


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _complete_evidence(tmp_path: Path, *, valid: bool = True, diagnostic_only: bool = False) -> Path:
    evidence = tmp_path / "frontend-tooling-authority"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    steps = []
    for name in (
        "pnpm_version",
        "pnpm_install_frozen_lockfile",
        "frontend_env_check",
        "frontend_type_check",
        "frontend_lint",
        "frontend_vitest",
    ):
        _write(raw / f"{name}_stdout.txt", "ok\n")
        _write(raw / f"{name}_stderr.txt", "")
        _write_json(
            raw / f"{name}_result.json",
            {
                "name": name,
                "command": ["pnpm"],
                "cwd": ".",
                "returncode": 0,
                "duration_seconds": 0.01,
                "stdout_file": f"{name}_stdout.txt",
                "stderr_file": f"{name}_stderr.txt",
            },
        )
        steps.append({"name": name, "returncode": 0})
    _write_json(
        raw / "frontend_tooling_authority_result.json",
        {
            "valid": valid,
            "diagnostic_only": diagnostic_only,
            "authority": "frontend-tooling-authority",
            "source_commit": "a" * 40,
            "branch": "feature/test",
            "expected_steps": [step["name"] for step in steps],
            "missing_steps": [],
            "failed_steps": [],
            "steps": steps,
        },
    )
    _write(evidence / "evidence_index.md", "# evidence\n")
    lines = []
    for path in sorted(raw.iterdir()):
        if path.name == "SHA256SUMS.txt":
            continue
        lines.append(f"{_sha(path)}  {path.name}")
    _write(raw / "SHA256SUMS.txt", "\n".join(lines) + "\n")
    return evidence


def test_phase03_static_assets_are_present() -> None:
    payload = {check.name: check for check in run_checks()}
    required = [
        "scripts/audit_remediation/run_frontend_tooling_authority.py",
        "scripts/audit_remediation/verify_frontend_tooling_authority.py",
        "scripts/audit_remediation/verify_frontend_tooling_evidence.py",
        "scripts/audit_remediation/collect_frontend_tooling_authority_evidence.sh",
        "docs/roadmap/execution/technical_audit_remediation/03_frontend_tooling_authority.md",
    ]
    for name in required:
        assert payload[name].valid, payload[name]


def test_phase03_static_verifier_requires_pnpm_and_frontend_scripts() -> None:
    checks = run_checks()
    names = {check.name: check for check in checks}
    assert names["root packageManager"].valid
    assert names["frontend packageManager"].valid
    for script in ("env-check", "type-check", "lint", "test"):
        assert names[f"frontend script {script}"].valid


def test_frontend_tooling_evidence_verifier_accepts_complete_evidence(tmp_path: Path) -> None:
    evidence = _complete_evidence(tmp_path)
    payload = verify(evidence)
    assert payload["valid"] is True, payload


def test_frontend_tooling_evidence_verifier_rejects_diagnostic_only(tmp_path: Path) -> None:
    evidence = _complete_evidence(tmp_path, diagnostic_only=True)
    payload = verify(evidence)
    assert payload["valid"] is False
    assert any("diagnostic-only" in finding["message"] for finding in payload["findings"])


def test_frontend_tooling_evidence_verifier_rejects_failed_step(tmp_path: Path) -> None:
    evidence = _complete_evidence(tmp_path)
    result = json.loads((evidence / "raw" / "frontend_tooling_authority_result.json").read_text())
    result["valid"] = False
    result["steps"][2]["returncode"] = 1
    _write_json(evidence / "raw" / "frontend_tooling_authority_result.json", result)
    lines = []
    for path in sorted((evidence / "raw").iterdir()):
        if path.name == "SHA256SUMS.txt":
            continue
        lines.append(f"{_sha(path)}  {path.name}")
    _write(evidence / "raw" / "SHA256SUMS.txt", "\n".join(lines) + "\n")
    payload = verify(evidence)
    assert payload["valid"] is False
    assert any("frontend_env_check returncode 1" in finding["message"] for finding in payload["findings"])
