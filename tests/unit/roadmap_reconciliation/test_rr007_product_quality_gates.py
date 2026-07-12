from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr007_product_quality_gates.py"
    spec = importlib.util.spec_from_file_location("verify_rr007", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rr007_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True
    assert not result.get("errors", [])


def test_rr007_record_becomes_valid_after_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".venv", "node_modules", "var", "htmlcov", ".pytest_cache")
    shutil.copytree(source, target, ignore=ignore)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_007_product_quality_gates_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "product_quality_gates_recorded": True,
            "playwright_ci_visible": True,
            "content_expansion_roadmap_recorded": True,
            "load_testing_plan_recorded": True,
            "accessibility_audit_plan_recorded": True,
            "pwa_offline_verification_plan_recorded": True,
            "multilingual_lesson_proof_plan_recorded": True,
            "supabase_postgres_adr_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "product_quality_audit": {"valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr007_audit_script_collects_required_gate_areas() -> None:
    root = Path.cwd()
    text = (root / "scripts/product_quality/audit_rr007_product_quality_gates.py").read_text(encoding="utf-8")
    for token in (
        "playwright_ci_visible",
        "content_expansion_roadmap_recorded",
        "load_testing_plan_recorded",
        "accessibility_audit_plan_recorded",
        "pwa_offline_verification_plan_recorded",
        "multilingual_lesson_proof_plan_recorded",
        "supabase_postgres_adr_recorded",
    ):
        assert token in text


def test_rr007_docs_carry_required_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/product_quality/rr007_product_quality_gate_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "Runtime KG" in policy
    assert "not authorised" in policy


def test_rr007_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr007-product-quality-audit" in text
    assert "rr007-product-quality-check" in text
