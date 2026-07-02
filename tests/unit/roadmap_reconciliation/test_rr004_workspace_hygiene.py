from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr004_workspace_hygiene.py"
    spec = importlib.util.spec_from_file_location("verify_rr004", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rr004_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is False
    assert "record is still pending evidence capture" in result["warnings"]


def test_rr004_record_becomes_valid_after_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".venv", "node_modules", "var", "htmlcov", ".pytest_cache")
    shutil.copytree(source, target, ignore=ignore)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_004_workspace_hygiene_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "workspace_hygiene_recorded": True,
            "safe_cleanup_target_recorded": True,
            "tracked_file_audit_inventory_recorded": True,
            "reproducible_scanner_counts_recorded": True,
            "ignored_artifact_cleanup_dry_run_only": True,
            "scanner_counts": {"tracked_file_count": 123},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr004_audit_script_mentions_tracked_file_inventory() -> None:
    root = Path.cwd()
    text = (root / "scripts/workspace_hygiene/audit_workspace_hygiene.py").read_text(encoding="utf-8")
    assert "git ls-files" in text
    assert "tracked_file_count" in text
    assert "extension_counts" in text


def test_rr004_cleanup_helper_is_dry_run_first() -> None:
    root = Path.cwd()
    text = (root / "scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py").read_text(encoding="utf-8")
    assert "git" in text
    assert "-ndX" in text
    assert "--confirm-delete-ignored-artifacts" in text


def test_rr004_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr004-workspace-hygiene-audit" in text
    assert "rr004-ignored-artifact-clean-dry-run" in text
