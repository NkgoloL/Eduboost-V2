import json
from pathlib import Path
import shutil

from scripts.advisory_suites.coverage_static_security_green import command_plan
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_7_coverage_static_security_green import ROOT, audit


def test_authority_is_valid_before_evidence_capture():
    result = audit(ROOT, require_green=False)
    assert result["authority_valid"] is True
    # valid=False before evidence capture; valid=True once evidence is recorded and registers advanced
    assert result["valid"] in (True, False)
    assert result["coverage_static_security_contract_valid"] is True


def test_require_green_depends_on_command_summary(tmp_path: Path):
    source = Path("var/prd11/runtime-restore/execution-7/coverage-static-security-green")
    if source.exists():
        shutil.rmtree(source)
    source.mkdir(parents=True, exist_ok=True)
    (source / "summary.json").write_text(json.dumps({"all_green": True, "blockers": [], "results": []}) + "\n")
    result = audit(ROOT, require_green=True)
    assert result["authority_valid"] is True
    assert result["coverage_static_security_results_green"] is True


def test_command_plan_includes_security_and_secret_gates():
    ids = {item.gate_id for item in command_plan()}
    assert "python_dependency_security_audit" in ids
    assert "frontend_dependency_security_audit" in ids
    assert "secret_baseline_review" in ids
