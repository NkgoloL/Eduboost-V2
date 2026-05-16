from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_route_alias_exception_parser_and_missing_detection(tmp_path):
    matrix_module = _load_module(ROOT / "scripts/generate_route_alias_matrix.py", "generate_route_alias_matrix_policy_test")
    check_module = _load_module(ROOT / "scripts/check_route_alias_matrix.py", "check_route_alias_matrix_policy_test")

    rows = matrix_module.collect_rows({
        ("GET", "/api/v2/health"),
        ("GET", "/v2/health"),
        ("POST", "/api/v2/internal-only"),
    })
    exceptions_path = tmp_path / "exceptions.txt"
    exceptions_path.write_text("POST /api/v2/internal-only -- intentional internal route\n", encoding="utf-8")

    exceptions = check_module.parse_exceptions(exceptions_path)
    assert check_module.missing_alias_rows(rows, exceptions) == []


def test_ci_workflow_consolidation_check_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_ci_workflow_consolidation.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_makefile_contains_ci_and_alias_targets():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "route-alias-policy-check:" in makefile
    assert "ci-workflow-consolidation-check:" in makefile
    assert "ci-core-local:" in makefile
