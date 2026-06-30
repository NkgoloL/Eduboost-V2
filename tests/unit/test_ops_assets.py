from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_ops_assets_validate_static_deployment_files() -> None:
    result = run_script("scripts/validate_ops_assets.py")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "Ops assets OK" in result.stdout


def test_runtime_env_validator_accepts_development_template() -> None:
    result = run_script(
        "scripts/validate_runtime_env.py",
        "--env",
        "development",
        "--env-file",
        ".env.example",
    )
    assert result.returncode == 0, result.stderr + result.stdout


def test_runtime_env_validator_rejects_production_placeholders() -> None:
    result = run_script(
        "scripts/validate_runtime_env.py",
        "--env",
        "production",
        "--env-file",
        ".env.example",
    )
    assert result.returncode != 0
    assert "placeholder" in result.stderr or "CHANGE_ME" in result.stderr


def test_release_evidence_manifest_generation(tmp_path: Path) -> None:
    output = tmp_path / "evidence"
    result = run_script(
        "scripts/build_release_evidence.py",
        "--output-dir",
        str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
    )
    # Use an absolute tmp path when relative_to is impossible in older runner layouts.
    if result.returncode != 0:
        result = run_script("scripts/build_release_evidence.py", "--output-dir", "reports/test_release_evidence")
        manifest = ROOT / "reports/test_release_evidence/release_evidence_manifest.json"
    else:
        manifest = output / "release_evidence_manifest.json"
    assert result.returncode == 0, result.stderr + result.stdout
    assert manifest.exists()
