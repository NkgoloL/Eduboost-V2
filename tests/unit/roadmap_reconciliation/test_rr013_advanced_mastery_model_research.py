from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py"
    spec = importlib.util.spec_from_file_location("verify_rr013", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(root))
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)
    return module


def _copy_minimal_repo(source: Path, target: Path) -> None:
    paths = [
        "Makefile",
        ".github/workflows/rr013-advanced-mastery-model-research.yml",
        "scripts/mastery_research/audit_rr013_advanced_mastery_model_research.py",
        "scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py",
        "scripts/roadmap_reconciliation/capture_rr013_advanced_mastery_model_research_evidence.py",
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard_record.json",
        "docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research.md",
        "docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research_record.json",
        "docs/learning_science/mastery_model.md",
        "docs/diagnostics/mastery_model_assessment_contract.md",
        "app/modules/progress/mastery_model.py",
    ]
    for rel in paths:
        src = source / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copytree(source / "docs/research/mastery_model", target / "docs/research/mastery_model", dirs_exist_ok=True)


def _write_final_files(root: Path) -> None:
    base = root / "docs/research/mastery_model"
    base.mkdir(parents=True, exist_ok=True)
    (base / "rr013_mastery_model_literature_review.md").write_text(
        """# RR-013 Literature Review\n\nAdvanced mastery-model literature reviewed: true\nResearch source limitations recorded: true\nSouth African CAPS applicability reviewed: true\n""",
        encoding="utf-8",
    )
    (base / "rr013_candidate_model_comparison.md").write_text(
        """# RR-013 Candidate Model Comparison\n\nModel candidates compared: true\nBaseline mastery formula included: true\nBayesian Knowledge Tracing evaluated: true\nDeep Knowledge Tracing evaluated: true\nProduction deployment recommendation recorded: false\n""",
        encoding="utf-8",
    )
    (base / "rr013_evaluation_protocol.md").write_text(
        """# RR-013 Evaluation Protocol\n\nEvaluation protocol recorded: true\nOffline evaluation required: true\nA/B test requires separate approval: true\nCAPS alignment evaluation required: true\nFairness and bias evaluation required: true\n""",
        encoding="utf-8",
    )
    (base / "rr013_data_readiness_and_ethics_review.md").write_text(
        """# RR-013 Data Readiness and Ethics Review\n\nData readiness and ethics reviewed: true\nNo learner PII exported for research: true\nPOPIA lawful basis review required before learner-data research: true\nSynthetic or anonymised data preferred: true\nModel retraining on production learner data authorised: false\n""",
        encoding="utf-8",
    )
    (base / "rr013_research_decision_memo.md").write_text(
        """# RR-013 Research Decision Memo\n\nResearch backlog decision recorded: true\nExisting mastery model preserved: true\nRuntime KG north-star boundary preserved: true\nLearner-facing model deployment authorised: false\nRuntime KG implementation claimed: false\n""",
        encoding="utf-8",
    )


def test_rr013_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True, result


def test_rr013_record_becomes_valid_after_final_files_and_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    _copy_minimal_repo(source, target)
    _write_final_files(target)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "advanced_mastery_model_research_recorded": True,
            "rr012_production_telemetry_dashboard_valid": True,
            "research_only_boundary_recorded": True,
            "existing_mastery_model_preserved": True,
            "literature_review_recorded": True,
            "model_candidates_compared": True,
            "evaluation_protocol_recorded": True,
            "data_readiness_ethics_reviewed": True,
            "caps_alignment_evaluation_required": True,
            "human_review_required_before_deployment": True,
            "no_learner_pii_exported_for_research": True,
            "runtime_kg_north_star_boundary_preserved": True,
            "research_decision_memo_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr014_public_beta_expansion_remaining_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "advanced_mastery_model_research_audit": {"valid": True, "final_outputs_valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr013_audit_rejects_missing_final_files_when_required(tmp_path: Path) -> None:
    source = Path.cwd()
    root = tmp_path / "repo"
    _copy_minimal_repo(source, root)
    for path in (
        "rr013_mastery_model_literature_review.md",
        "rr013_candidate_model_comparison.md",
        "rr013_evaluation_protocol.md",
        "rr013_data_readiness_and_ethics_review.md",
        "rr013_research_decision_memo.md",
    ):
        (root / "docs/research/mastery_model" / path).unlink()
    audit_path = root / "scripts/mastery_research/audit_rr013_advanced_mastery_model_research.py"
    spec = importlib.util.spec_from_file_location("audit_rr013", audit_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit(root, require_final=True)
    assert result["authority_valid"] is True, result
    assert result["final_outputs_valid"] is False
    assert any("missing final RR-013 evidence file" in error for error in result["errors"])


def test_rr013_policy_carries_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/research/mastery_model/rr013_mastery_model_research_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "non-required" in policy
    assert "RR-014" in policy
    assert "RR-015" in policy
    assert "RR-016" in policy
    assert "Runtime KG implementation claimed: false" in policy
    assert "Learner-facing model deployment authorised: false" in policy


def test_rr013_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr013-advanced-mastery-model-research-audit" in text
    assert "rr013-advanced-mastery-model-research-check" in text
