"""Tests for deterministic route inventory generation."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate_route_inventory.py"


def _run_generator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.unit
def test_route_inventory_renders_canonical_runtime_in_isolated_process(tmp_path: Path) -> None:
    output_path = tmp_path / "route_inventory.md"

    result = _run_generator("--output", str(output_path))

    assert result.returncode == 0, result.stderr

    content = output_path.read_text(encoding="utf-8")
    assert "Canonical runtime: `app.api_v2:app`" in content
    assert "Legacy route prefixes present in canonical runtime: `no`" in content
    assert "/api/v2" in content
    assert "/v2" in content
    assert "/system" in content


@pytest.mark.unit
def test_route_inventory_excludes_legacy_v1_lesson_route_in_isolated_process(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "route_inventory.md"

    result = _run_generator("--output", str(output_path))

    assert result.returncode == 0, result.stderr

    content = output_path.read_text(encoding="utf-8")
    route_table = content.split("## Canonical Route Table", maxsplit=1)[1]

    assert "/api/v1/lessons/generate" not in route_table
    assert "/api/legacy" not in route_table
    assert "/legacy" not in route_table


@pytest.mark.unit
def test_generate_route_inventory_writes_document(tmp_path: Path) -> None:
    output_path = tmp_path / "route_inventory.md"

    result = _run_generator("--output", str(output_path))

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "Wrote route inventory" in result.stdout
    assert "Canonical runtime: `app.api_v2:app`" in output_path.read_text(encoding="utf-8")


@pytest.mark.unit
def test_generate_route_inventory_check_passes_when_current(tmp_path: Path) -> None:
    output_path = tmp_path / "route_inventory.md"

    generate_result = _run_generator("--output", str(output_path))
    assert generate_result.returncode == 0, generate_result.stderr

    check_result = _run_generator("--output", str(output_path), "--check")

    assert check_result.returncode == 0, check_result.stderr


@pytest.mark.unit
def test_generate_route_inventory_check_fails_on_drift(tmp_path: Path) -> None:
    output_path = tmp_path / "route_inventory.md"
    output_path.write_text("# stale\n", encoding="utf-8")

    result = _run_generator("--output", str(output_path), "--check")

    assert result.returncode == 1
    assert "Route inventory drift detected" in result.stderr
