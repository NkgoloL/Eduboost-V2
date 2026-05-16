from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_backend_runtime_compatibility_contract_mentions_surfaces():
    text = (ROOT / "docs/release/backend_runtime_compatibility_contract.md").read_text(encoding="utf-8")
    assert "Audit repository canonical interface" in text
    assert "Consent service runtime interface" in text
    assert "Deep-health evidence interface" in text


def test_backend_runtime_compatibility_checker_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_backend_runtime_compatibility.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_backend_runtime_report_generator_defines_expected_commands():
    module = _load_module(
        "scripts/generate_backend_runtime_compatibility_report.py",
        "backend_runtime_compatibility_report_for_test",
    )
    names = [name for name, _command in module.COMMANDS]
    assert "runtime compatibility" in names
    assert "audit compatibility" in names
    assert "consent compatibility" in names
    assert "health readiness" in names


def test_makefile_contains_backend_runtime_compatibility_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-runtime-compatibility-check:" in text
    assert "backend-runtime-compatibility-report:" in text
    assert "backend-runtime-compatibility-full-check:" in text
