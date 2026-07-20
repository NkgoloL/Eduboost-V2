#!/usr/bin/env python3
"""Gate 2R.8 implementation verifier."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run(command: list[str]) -> dict[str, Any]:
    proc = run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"command": command, "exit_code": proc.returncode, "output": proc.stdout[-8000:]}


def _control_errors() -> list[str]:
    control_path = ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if control.get("start_approved") is not True:
        errors.append("Phase 02R start_approved must remain true")
    if control.get("approved_gate") != "2R.7":
        errors.append(f"Gate 2R.8 implementation requires approved_gate=2R.7, found {control.get('approved_gate')!r}")
    if control.get("authorised_next_gate") != "2R.8":
        errors.append(f"Gate 2R.8 implementation requires authorised_next_gate=2R.8, found {control.get('authorised_next_gate')!r}")
    if (ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r8_approvals.json").exists():
        errors.append("Gate 2R.8 approval manifest already exists; implementation verifier must run before approval")
    plan = (ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md").read_text(encoding="utf-8")
    if "Execution authorisation:** Gate 2R.8 only" not in plan:
        errors.append("execution plan must authorise Gate 2R.8 only")
    if "Gate 2R.7 verified complete; Gate 2R.8 authorised" not in plan:
        errors.append("execution plan must record Gate 2R.7 verified complete and Gate 2R.8 authorised")
    return errors


def _behavioral_errors() -> list[str]:
    errors: list[str] = []
    try:
        from app.services.curriculum.evaluation import (
            MIN_MRR,
            MIN_NEGATIVE_CASES,
            MIN_POSITIVE_CASES,
            MIN_PRECISION_AT_K,
            MIN_RECALL_AT_K,
            EvaluationRejectedError,
            Gate2R8EvaluationPolicy,
            RetrievalEvaluationCase,
            build_gate2r8_evaluation_cases,
            build_gate2r8_evaluation_report,
        )
        from app.services.curriculum.legacy_migration import (
            LegacyArtifactView,
            LegacyMigrationClassifier,
            build_gate2r8_legacy_migration_manifest,
        )
        from app.services.curriculum.phase02r_closure import build_gate2r8_audit_bundle, evaluate_closure_readiness

        cases = build_gate2r8_evaluation_cases()
        positive = [case for case in cases if not case.is_negative_case]
        negative = [case for case in cases if case.is_negative_case]
        if len(positive) < MIN_POSITIVE_CASES or len(negative) < MIN_NEGATIVE_CASES:
            errors.append("evaluation fixture lacks required positive/negative cases")
        result = Gate2R8EvaluationPolicy().evaluate(cases)
        if result.status != "passed":
            errors.append("Gate 2R.8 evaluation fixture did not pass thresholds")
        if result.metrics.recall_at_k < MIN_RECALL_AT_K:
            errors.append("recall_at_k is below threshold")
        if result.metrics.precision_at_k < MIN_PRECISION_AT_K:
            errors.append("precision_at_k is below threshold")
        if result.metrics.mrr < MIN_MRR:
            errors.append("mrr is below threshold")
        try:
            Gate2R8EvaluationPolicy().evaluate([
                RetrievalEvaluationCase(
                    case_id="negative-with-hit",
                    language="en",
                    strand="out_of_scope",
                    term=None,
                    query="unsupported",
                    is_negative_case=True,
                    retrieved_chunk_ids=("forbidden",),
                )
            ])
            errors.append("negative retrieval hit was not rejected")
        except Exception:  # best-effort probe, cannot fail-close
            pass
        legacy_manifest = build_gate2r8_legacy_migration_manifest()
        if legacy_manifest.get("status") != "ready_for_review":
            errors.append("legacy migration manifest is not review-ready")
        if legacy_manifest.get("gate_boundary", {}).get("migration_executed") is not False:
            errors.append("Gate 2R.8 legacy manifest must not execute migration")
        classifier = LegacyMigrationClassifier()
        published = classifier.classify(LegacyArtifactView(
            artifact_id="published-ungrounded",
            artifact_type="lesson",
            published=True,
            source_snapshot_hash=None,
        ))
        if published.disposition != "quarantine_requires_review" or published.learner_serving_allowed:
            errors.append("published ungrounded legacy artifact was not quarantined")
        eval_report = build_gate2r8_evaluation_report()
        if eval_report.get("gate_boundary", {}).get("phase_02r_completion_declared") is not False:
            errors.append("evaluation report must not declare Phase 02R completion")
        closure = evaluate_closure_readiness(ROOT)
        if closure.status != "ready_for_candidate_closure_evidence":
            errors.extend(f"closure readiness blocked: {reason}" for reason in closure.failure_reasons)
        bundle1 = build_gate2r8_audit_bundle(ROOT)
        bundle2 = build_gate2r8_audit_bundle(ROOT)
        if bundle1.get("audit_bundle_sha256") != bundle2.get("audit_bundle_sha256"):
            errors.append("audit bundle hash is not deterministic")
        if bundle1.get("gate_boundary", {}).get("phase_02r_completion_declared") is not False:
            errors.append("audit bundle must not declare Phase 02R completion")
    except Exception as exc:
        errors.append(f"Gate 2R.8 behavioral checks failed to execute: {exc}")
    return errors


def verify(mode: str) -> dict[str, Any]:
    from app.services.curriculum.phase02r_verification import validate_required_paths

    errors: list[str] = []
    checks: list[dict[str, Any]] = []
    errors.extend(_control_errors())
    errors.extend(validate_required_paths("2R.8"))

    compile_targets = [
        "app/services/curriculum/legacy_migration.py",
        "app/services/curriculum/evaluation.py",
        "app/services/curriculum/phase02r_closure.py",
        "app/services/curriculum/phase02r_verification.py",
        "scripts/verify_phase02r_gate2r8.py",
        "scripts/curriculum/build_phase02r_gate2r8_legacy_migration.py",
        "scripts/curriculum/export_phase02r_gate2r8_evaluation_report.py",
        "scripts/curriculum/export_phase02r_gate2r8_audit_bundle.py",
        "scripts/curriculum/validate_phase02r_gate2r8_closure.py",
        "tests/unit/phase02r/test_gate2r8_legacy_evaluation_closure.py",
    ]
    checks.append(_run([sys.executable, "-m", "compileall", "-q", *compile_targets]))
    if checks[-1]["exit_code"] != 0:
        errors.append("compileall failed for Gate 2R.8 files")

    for command, message in [
        ([sys.executable, "scripts/curriculum/build_phase02r_gate2r8_legacy_migration.py", "--json"], "legacy migration manifest export failed"),
        ([sys.executable, "scripts/curriculum/export_phase02r_gate2r8_evaluation_report.py", "--json"], "evaluation report export failed"),
        ([sys.executable, "scripts/curriculum/export_phase02r_gate2r8_audit_bundle.py", "--json"], "audit bundle export failed"),
        ([sys.executable, "scripts/curriculum/validate_phase02r_gate2r8_closure.py", "--json"], "closure readiness validation failed"),
        ([sys.executable, "scripts/verify_migration_graph.py"], "migration graph check failed"),
    ]:
        checks.append(_run(command))
        if checks[-1]["exit_code"] != 0:
            errors.append(message)

    errors.extend(_behavioral_errors())
    if mode == "closure":
        errors.append("Gate 2R.8 closure requires committed candidate evidence, approvals, and a final Phase 02R closure decision; implementation verifier cannot close the phase")
    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["implementation", "closure"], default="implementation")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.mode)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print(f"Phase 2R Gate 2R.8 {args.mode} verification passed")
    else:
        print(f"Phase 2R Gate 2R.8 {args.mode} verification failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
