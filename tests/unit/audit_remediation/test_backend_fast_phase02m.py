from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load(name: str):
    module_path = ROOT / "scripts" / "audit_remediation" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_phase02m_verifier_assets_are_present() -> None:
    module = _load("verify_backend_fast_phase02m")
    result = module.verify(ROOT)
    assert result["valid"], result


def test_historical_phase_verifiers_are_not_pinned_to_active_slice() -> None:
    for name in ["verify_backend_fast_phase02k", "verify_backend_fast_phase02l"]:
        module = _load(name)
        result = module.verify(ROOT)
        assert result["valid"], result


def test_project_assistance_status_is_current() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/project_assistance_status.py", "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_pr_contract_documents_are_restored() -> None:
    required = [
        "docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md",
        "docs/pr/combined_runtime_wiring_pr_checklist.md",
        "docs/pr/first_audit_runtime_wiring_pr_checklist.md",
        "docs/pr/backend_runtime_wiring_pr_template.md",
        "docs/pr/runtime_integration_pr_template.md",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel
