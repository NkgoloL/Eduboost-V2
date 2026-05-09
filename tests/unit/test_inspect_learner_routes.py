"""Tests for learner route inspection helper."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "inspect_learner_routes.py"

spec = importlib.util.spec_from_file_location("inspect_learner_routes", SCRIPT)
assert spec is not None
assert spec.loader is not None

inspect_learner_routes = importlib.util.module_from_spec(spec)
sys.modules["inspect_learner_routes"] = inspect_learner_routes
spec.loader.exec_module(inspect_learner_routes)

find_references = inspect_learner_routes.find_references
render_markdown = inspect_learner_routes.render_markdown


@pytest.mark.unit
def test_inspector_finds_learner_references() -> None:
    files = [REPO_ROOT / "app" / "api_v2.py"]
    references = find_references(files)

    assert isinstance(references, list)


@pytest.mark.unit
def test_inspector_renders_markdown_report() -> None:
    content = render_markdown([], [])

    assert "Learner Route Authorization Inspection" in content
    assert "Learner-Scoped Route Candidates" in content
    assert "Next Step" in content


@pytest.mark.unit
def test_inspector_cli_writes_report(tmp_path: Path) -> None:
    output_path = tmp_path / "learner_route_authorization_inspection.md"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(output_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "Route candidates:" in result.stdout
    assert "Learner Route Authorization Inspection" in output_path.read_text(encoding="utf-8")


@pytest.mark.unit
def test_inspector_cli_json_output() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert '"route_candidates"' in result.stdout
    assert '"references"' in result.stdout
