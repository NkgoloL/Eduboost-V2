#!/usr/bin/env python3
"""Gate 2R.6 implementation verifier."""
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
    control = json.loads((ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if control.get("start_approved") is not True:
        errors.append("Phase 02R start_approved must remain true")
    if control.get("approved_gate") != "2R.5":
        errors.append(f"Gate 2R.6 implementation requires approved_gate=2R.5, found {control.get('approved_gate')!r}")
    if control.get("authorised_next_gate") != "2R.6":
        errors.append(f"Gate 2R.6 implementation requires authorised_next_gate=2R.6, found {control.get('authorised_next_gate')!r}")
    if control.get("authorised_next_gate") in {"2R.7", "2R.8"}:
        errors.append("Gate 2R.7+ is authorised; Gate 2R.6 verifier must not run against downstream state")
    return errors


def _behavioral_errors() -> list[str]:
    errors: list[str] = []
    try:
        from dataclasses import replace
        from app.services.curriculum.corpus import ActiveCorpusRetriever, build_gate2r5_fixture_package
        from app.services.curriculum.generation import (
            GROUND_VERIFIED_STATUS,
            GENERATION_POLICY_VERSION,
            GroundedGenerationRejectedError,
            GroundedGenerationRequest,
            GroundedGenerationService,
            build_gate2r6_fixture_artifact,
            build_gate2r6_generation_packet,
        )
        from app.services.curriculum.claim_validation import Claim, ClaimValidator
        from app.services.curriculum.answer_verification import DeterministicMathAnswerVerifier

        artifact = build_gate2r6_fixture_artifact("lesson_with_assessment")
        if artifact.status != GROUND_VERIFIED_STATUS:
            errors.append("fixture artifact is not grounded_verified")
        if artifact.generation_policy_version != GENERATION_POLICY_VERSION:
            errors.append("generation policy version mismatch")
        if not artifact.source_references or not artifact.source_snapshot_hash:
            errors.append("artifact must carry source provenance")
        if any(ref.corpus_version_id != artifact.request.corpus_version_id for ref in artifact.source_references):
            errors.append("artifact contains mixed corpus provenance")
        if any(item.answer_verification_status != "passed" for item in artifact.assessment_items):
            errors.append("assessment item deterministic answer verification failed")
        if ClaimValidator().validate([Claim("curriculum_requirement", "Unsupported CAPS claim", [])]).status != "failed":
            errors.append("unsupported curriculum claim was not rejected")
        if DeterministicMathAnswerVerifier().verify_arithmetic_expression(question_expression="2 + 3 * 4", proposed_answer="13").status != "failed":
            errors.append("incorrect deterministic answer was not rejected")
        manifest, projection, binding, _ = build_gate2r5_fixture_package()
        service = GroundedGenerationService(retriever=ActiveCorpusRetriever(projection, binding))
        req = GroundedGenerationRequest(
            artifact_type="lesson_with_assessment",
            activation_key=binding.activation_key,
            corpus_version_id=binding.corpus_version_id,
            binding_epoch=binding.binding_epoch,
            language=manifest.language,
            topic="compare whole numbers and place value",
            objective_ids=("node-g4math-numbers-whole-numbers-v1",),
        )
        try:
            service.generate(replace(req, objective_ids=("missing-objective",)))
            errors.append("missing objective generation did not fail closed")
        except Exception:  # best-effort probe, cannot fail-close
            pass
        fallback = service.generate(replace(req, objective_ids=("missing-objective",), safe_fallback_allowed=True))
        if fallback.status != "safe_fallback":
            errors.append("explicit safe fallback contract failed")
        packet1 = build_gate2r6_generation_packet()
        packet2 = build_gate2r6_generation_packet()
        if packet1.get("packet_sha256") != packet2.get("packet_sha256"):
            errors.append("generation packet hash is not deterministic")
        if packet1.get("gate_boundary", {}).get("tutor_runtime_wired") is not False:
            errors.append("Gate 2R.6 must not wire tutor runtime behavior")
        if packet1.get("gate_boundary", {}).get("gate_2r7_authorised") is not False:
            errors.append("Gate 2R.6 packet must not authorise Gate 2R.7")
    except Exception as exc:
        errors.append(f"Gate 2R.6 behavioral checks failed to execute: {exc}")
    return errors


def verify(mode: str) -> dict[str, Any]:
    from app.services.curriculum.phase02r_verification import validate_required_paths

    errors: list[str] = []
    checks: list[dict[str, Any]] = []
    errors.extend(_control_errors())
    errors.extend(validate_required_paths("2R.6"))

    compile_targets = [
        "app/services/curriculum/grounding.py",
        "app/services/curriculum/claim_validation.py",
        "app/services/curriculum/answer_verification.py",
        "app/services/curriculum/generation.py",
        "app/services/curriculum/phase02r_verification.py",
        "scripts/verify_phase02r_gate2r6.py",
        "scripts/curriculum/build_phase02r_gate2r6_grounded_generation.py",
        "scripts/curriculum/export_phase02r_gate2r6_generation_packet.py",
        "scripts/curriculum/validate_phase02r_gate2r6_generation.py",
        "tests/unit/phase02r/test_gate2r6_grounded_generation.py",
    ]
    checks.append(_run([sys.executable, "-m", "compileall", "-q", *compile_targets]))
    if checks[-1]["exit_code"] != 0:
        errors.append("compileall failed for Gate 2R.6 files")

    for command, message in [
        ([sys.executable, "scripts/curriculum/build_phase02r_gate2r6_grounded_generation.py", "--json"], "grounded generation dry-run failed"),
        ([sys.executable, "scripts/curriculum/export_phase02r_gate2r6_generation_packet.py", "--json"], "generation packet export failed"),
        ([sys.executable, "scripts/curriculum/validate_phase02r_gate2r6_generation.py", "--json"], "grounded generation validation failed"),
        ([sys.executable, "scripts/verify_migration_graph.py"], "migration graph check failed"),
    ]:
        checks.append(_run(command))
        if checks[-1]["exit_code"] != 0:
            errors.append(message)

    errors.extend(_behavioral_errors())
    if mode == "closure":
        errors.append("Gate 2R.6 closure requires committed candidate evidence, approvals, and a separate transition; implementation verifier cannot close the gate")
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
        print(f"Phase 2R Gate 2R.6 {args.mode} verification passed")
    else:
        print(f"Phase 2R Gate 2R.6 {args.mode} verification failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
