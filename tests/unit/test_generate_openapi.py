"""Tests for the deterministic OpenAPI generation script."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate_openapi.py"


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.unit
def test_generate_openapi_writes_schema(tmp_path: Path) -> None:
    output = tmp_path / "openapi.json"

    result = _run_script("--output", str(output))

    assert result.returncode == 0, result.stderr
    assert output.exists()

    schema = json.loads(output.read_text(encoding="utf-8"))
    assert schema["info"]["title"] == "EduBoost SA V2"
    assert schema["openapi"].startswith("3.")
    assert "/health" in schema["paths"]
    assert "/ready" in schema["paths"]


@pytest.mark.unit
def test_generate_openapi_check_passes_when_file_is_current(tmp_path: Path) -> None:
    output = tmp_path / "openapi.json"

    generate = _run_script("--output", str(output))
    assert generate.returncode == 0, generate.stderr

    check = _run_script("--output", str(output), "--check")
    assert check.returncode == 0, check.stderr


@pytest.mark.unit
def test_generate_openapi_check_fails_when_file_has_drift(tmp_path: Path) -> None:
    output = tmp_path / "openapi.json"

    generate = _run_script("--output", str(output))
    assert generate.returncode == 0, generate.stderr

    output.write_text('{"stale": true}\n', encoding="utf-8")
    check = _run_script("--output", str(output), "--check")

    assert check.returncode == 1
    assert "OpenAPI drift detected" in check.stderr


@pytest.mark.unit
def test_generate_openapi_check_fails_when_file_is_missing(tmp_path: Path) -> None:
    output = tmp_path / "missing-openapi.json"

    check = _run_script("--output", str(output), "--check")

    assert check.returncode == 1
    assert "OpenAPI file is missing" in check.stderr
