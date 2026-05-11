"""Tests for runtime entrypoint verification."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_runtime_entrypoints.py"

spec = importlib.util.spec_from_file_location("check_runtime_entrypoints", SCRIPT)
assert spec is not None
assert spec.loader is not None

check_runtime_entrypoints = importlib.util.module_from_spec(spec)
sys.modules["check_runtime_entrypoints"] = check_runtime_entrypoints
spec.loader.exec_module(check_runtime_entrypoints)

DEFAULT_ENTRYPOINTS = check_runtime_entrypoints.DEFAULT_ENTRYPOINTS
REQUIRED_CANONICAL_ROUTES = check_runtime_entrypoints.REQUIRED_CANONICAL_ROUTES
check_entrypoints = check_runtime_entrypoints.check_entrypoints
load_app = check_runtime_entrypoints.load_app
route_paths = check_runtime_entrypoints.route_paths


@pytest.mark.unit
def test_canonical_runtime_entrypoint_loads_fastapi_app() -> None:
    app = load_app("app.api_v2:app")

    assert app.title == "EduBoost SA V2"
    assert route_paths(app)


@pytest.mark.unit
def test_canonical_runtime_contains_required_routes() -> None:
    app = load_app("app.api_v2:app")
    paths = route_paths(app)

    for route in REQUIRED_CANONICAL_ROUTES:
        assert route in paths

    assert any(path == "/api/v2" or path.startswith("/api/v2/") for path in paths)
    assert any(path == "/v2" or path.startswith("/v2/") for path in paths)


@pytest.mark.unit
def test_default_entrypoints_pass_contract() -> None:
    results = check_entrypoints(list(DEFAULT_ENTRYPOINTS))

    assert all(result.ok for result in results), results


@pytest.mark.unit
def test_runtime_check_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS app.api_v2:app" in result.stdout


@pytest.mark.unit
def test_runtime_check_cli_fails_for_missing_entrypoint() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--entrypoint",
            "missing.module:app",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "FAIL missing.module:app" in result.stdout
