from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr005_technical_debt_burndown.py"
    spec = importlib.util.spec_from_file_location("verify_rr005", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rr005_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is False
    assert "record is still pending evidence capture" in result["warnings"]


def test_rr005_record_becomes_valid_after_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".venv", "node_modules", "var", "htmlcov", ".pytest_cache")
    shutil.copytree(source, target, ignore=ignore)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_005_technical_debt_burndown_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "technical_debt_burndown_recorded": True,
            "ruff_debt_captured": True,
            "import_linter_exceptions_registered": True,
            "stale_route_comments_audited": True,
            "migration_history_audited": True,
            "dormant_router_review_recorded": True,
            "debt_burndown_backlog_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "technical_debt_audit": {"valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr005_audit_script_collects_required_debt_areas() -> None:
    root = Path.cwd()
    text = (root / "scripts/technical_debt/audit_rr005_technical_debt.py").read_text(encoding="utf-8")
    for token in (
        "collect_ruff_debt",
        "collect_import_linter_exceptions",
        "collect_stale_route_comments",
        "collect_migration_history",
        "collect_dormant_router_review",
    ):
        assert token in text


def test_rr005_docs_carry_required_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/engineering/technical_debt/rr005_technical_debt_burndown_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "Runtime KG" in policy
    assert "not authorised" in policy


def test_rr005_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr005-technical-debt-audit" in text
    assert "rr005-technical-debt-check" in text
