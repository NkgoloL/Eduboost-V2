from __future__ import annotations

import importlib.util
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


def test_capture_tool_defines_expected_scopes():
    module = _load_module(ROOT / "scripts/capture_pytest_release_evidence.py", "capture_pytest_release_evidence_for_test")
    assert set(module.RUNS) == {"unit", "integration", "full"}
    assert module.RUNS["unit"].output_path.name == "unit_latest_green.txt"
    assert module.RUNS["integration"].output_path.name == "integration_latest_green.txt"
    assert module.RUNS["full"].output_path.name == "full_pytest_latest_green.txt"


def test_check_tool_rejects_missing_evidence(tmp_path):
    module = _load_module(ROOT / "scripts/check_pytest_release_evidence.py", "check_pytest_release_evidence_for_test")
    missing = tmp_path / "missing.txt"
    assert module._file_is_green(missing) is False


def test_check_tool_accepts_green_evidence(tmp_path):
    module = _load_module(ROOT / "scripts/check_pytest_release_evidence.py", "check_pytest_release_evidence_green_for_test")
    path = tmp_path / "unit_latest_green.txt"
    path.write_text(
        "\n".join(
            [
                "# Command: pytest -c pytest.ini tests/unit -q --no-cov",
                "# Captured at: 2026-05-16T00:00:00Z",
                "# Return code: 0",
                "",
                "1455 passed, 1 skipped, 4 warnings in 128.67s",
            ]
        ),
        encoding="utf-8",
    )
    assert module._file_is_green(path) is True


def test_makefile_contains_pytest_release_evidence_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "capture-pytest-release-evidence:" in text
    assert "pytest-release-evidence-check:" in text
