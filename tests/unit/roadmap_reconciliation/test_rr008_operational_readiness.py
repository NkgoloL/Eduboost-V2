from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr008_operational_readiness.py"
    spec = importlib.util.spec_from_file_location("verify_rr008", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rr008_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True
    assert not result.get("errors", [])


def test_rr008_record_becomes_valid_after_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".venv", "node_modules", "var", "htmlcov", ".pytest_cache")
    shutil.copytree(source, target, ignore=ignore)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_008_operational_readiness_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "operational_readiness_recorded": True,
            "incident_response_runbook_recorded": True,
            "slo_definitions_recorded": True,
            "capacity_planning_recorded": True,
            "llm_cost_model_recorded": True,
            "grafana_alert_linkage_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr016_drills_remaining_visible": True,
            "operational_readiness_audit": {"valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr008_audit_script_collects_required_gate_areas() -> None:
    root = Path.cwd()
    text = (root / "scripts/operations_readiness/audit_rr008_operational_readiness.py").read_text(encoding="utf-8")
    for token in (
        "incident_response_runbook_recorded",
        "slo_definitions_recorded",
        "capacity_planning_recorded",
        "llm_cost_model_recorded",
        "grafana_alert_linkage_recorded",
    ):
        assert token in text


def test_rr008_docs_carry_required_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/operations/readiness/rr008_operational_readiness_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "non-required" in policy
    assert "RR-016" in policy
    assert "Runtime KG" in policy
    assert "not authorised" in policy


def test_rr008_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr008-operational-readiness-audit" in text
    assert "rr008-operational-readiness-check" in text
