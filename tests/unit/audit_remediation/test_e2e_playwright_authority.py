from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def test_e2e_playwright_authority_verifier_passes() -> None:
    module = _load_module(
        "verify_e2e_playwright_authority",
        ROOT / "scripts/audit_remediation/verify_e2e_playwright_authority.py",
    )
    payload = module.verify()
    assert payload["valid"] is True, payload
    messages = "\n".join(item["message"] for item in payload["findings"])
    assert "Playwright default base URL uses Next.js port 3050" in messages
    assert "workflow contains required E2E snippet: pnpm exec playwright test" in messages
    assert payload["remote_ci_run_claimed"] is False


def _read_wf(rel: str) -> str:
    path = ROOT / rel
    if not path.exists() and rel.startswith(".github/workflows/"):
        archived = ROOT / "archive/github_workflows" / Path(rel).name
        if archived.exists():
            path = archived
    return path.read_text(encoding="utf-8")


def test_e2e_workflows_use_pnpm_and_supported_artifact_uploads() -> None:
    combined = "\n".join(
        _read_wf(path)
        for path in (
            ".github/workflows/ci-cd.yml",
            ".github/workflows/e2e.yml",
            ".github/workflows/frontend-e2e.yml",
        )
    )
    assert "pnpm install --frozen-lockfile" in combined
    assert "pnpm --dir app/frontend install --frozen-lockfile" in combined
    assert "pnpm exec playwright install --with-deps chromium" in combined
    assert "pnpm exec playwright test" in combined
    assert "actions/upload-artifact@v4" in combined
    assert "npm ci" not in combined
    assert "npx playwright" not in combined
    assert "actions/setup-node@v6" not in combined


def test_playwright_authority_runner_records_required_steps(tmp_path: Path, monkeypatch) -> None:
    module = _load_module(
        "run_e2e_playwright_authority",
        ROOT / "scripts/audit_remediation/run_e2e_playwright_authority.py",
    )

    def fake_run_step(name, command, output_dir, env, timeout):
        (output_dir / f"{name}.stdout.txt").write_text("ok", encoding="utf-8")
        (output_dir / f"{name}.stderr.txt").write_text("", encoding="utf-8")
        return module.StepResult(
            name=name,
            command=command,
            returncode=0,
            duration_seconds=0.01,
            stdout_path=f"{name}.stdout.txt",
            stderr_path=f"{name}.stderr.txt",
        )

    monkeypatch.setattr(module, "_run_step", fake_run_step)
    payload = module.run_authority(tmp_path, install_browsers=False, run_tests=False)
    assert (tmp_path / "e2e_playwright_authority_result.json").exists()
    step_names = {step["name"] for step in payload["steps"]}
    assert {"pnpm_version", "root_pnpm_install", "frontend_pnpm_install", "playwright_version"}.issubset(step_names)


def test_e2e_playwright_evidence_verifier_accepts_complete_fixture(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir(parents=True)
    verification = {"valid": True, "findings": [{"valid": True, "message": "ok"}]}
    result = {
        "valid": True,
        "remote_ci_run_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "steps": [
            {"name": "pnpm_version", "returncode": 0},
            {"name": "root_pnpm_install", "returncode": 0},
            {"name": "frontend_pnpm_install", "returncode": 0},
            {"name": "playwright_version", "returncode": 0},
            {"name": "playwright_mocked_journeys", "returncode": 0},
        ],
    }
    (raw / "e2e_playwright_authority_verification.json").write_text(json.dumps(verification), encoding="utf-8")
    (raw / "e2e_playwright_authority_result.json").write_text(json.dumps(result), encoding="utf-8")
    for snapshot in ("ci-cd.yml.snapshot", "e2e.yml.snapshot", "frontend-e2e.yml.snapshot", "playwright.config.ts.snapshot"):
        (raw / snapshot).write_text("snapshot", encoding="utf-8")
    lines = []
    for path in sorted(p for p in raw.iterdir() if p.name != "SHA256SUMS.txt"):
        import hashlib
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (raw / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (tmp_path / "evidence_index.md").write_text("# evidence", encoding="utf-8")

    module = _load_module(
        "verify_e2e_playwright_evidence",
        ROOT / "scripts/audit_remediation/verify_e2e_playwright_evidence.py",
    )
    payload = module.verify(tmp_path)
    assert payload["valid"] is True, payload


def test_e2e_playwright_evidence_verifier_rejects_failed_step(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir(parents=True)
    (tmp_path / "evidence_index.md").write_text("# evidence", encoding="utf-8")
    (raw / "e2e_playwright_authority_verification.json").write_text(json.dumps({"valid": True}), encoding="utf-8")
    (raw / "e2e_playwright_authority_result.json").write_text(json.dumps({"valid": False, "remote_ci_run_claimed": False, "full_backend_backed_e2e_claimed": False, "steps": [{"name": "playwright_mocked_journeys", "returncode": 1}]}), encoding="utf-8")
    for snapshot in ("ci-cd.yml.snapshot", "e2e.yml.snapshot", "frontend-e2e.yml.snapshot", "playwright.config.ts.snapshot"):
        (raw / snapshot).write_text("snapshot", encoding="utf-8")
    (raw / "SHA256SUMS.txt").write_text("", encoding="utf-8")

    module = _load_module(
        "verify_e2e_playwright_evidence",
        ROOT / "scripts/audit_remediation/verify_e2e_playwright_evidence.py",
    )
    payload = module.verify(tmp_path)
    assert payload["valid"] is False
