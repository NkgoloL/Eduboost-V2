from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr006_security_posture_deepening.py"
    spec = importlib.util.spec_from_file_location("verify_rr006", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rr006_authority_files_are_valid():
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is False
    assert "record is still pending evidence capture" in result["warnings"]


def test_rr006_record_becomes_valid_after_capture_shape(tmp_path: Path):
    source = Path.cwd()
    target = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".venv", "node_modules", "var", "htmlcov", ".pytest_cache")
    shutil.copytree(source, target, ignore=ignore)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_006_security_posture_deepening_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "security_posture_deepening_recorded": True,
            "v2_threat_model_reviewed": True,
            "v2_pen_test_checklist_recorded": True,
            "dependency_vulnerability_scan_enforced": True,
            "python_dependency_audit_enforced": True,
            "secrets_scanning_precommit_enforced": True,
            "secrets_scanning_ci_enforced": True,
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr006_precommit_and_ci_secret_scanning_are_detected():
    root = Path.cwd()
    precommit = (root / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/rr006-security-posture.yml").read_text(encoding="utf-8")
    assert "detect-secrets" in precommit
    assert "detect-secrets" in workflow


def test_rr006_python_dependency_audit_is_ci_visible():
    root = Path.cwd()
    workflow = (root / ".github/workflows/rr006-security-posture.yml").read_text(encoding="utf-8")
    policy = (root / "docs/security/python_dependency_audit_policy.md").read_text(encoding="utf-8")
    assert "pip-audit" in workflow
    assert "pip-audit" in policy


def test_rr006_boundary_flags_remain_false():
    root = Path.cwd()
    record = json.loads((root / "docs/roadmap/reconciliation/rr_006_security_posture_deepening_record.json").read_text(encoding="utf-8"))
    for key in (
        "production_release_authorised",
        "deployment_authorised",
        "release_tag_authorised",
        "public_beta_authorised",
        "runtime_kg_implementation_claimed",
    ):
        assert record[key] is False
