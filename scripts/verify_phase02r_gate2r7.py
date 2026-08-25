#!/usr/bin/env python3
"""Gate 2R.7 implementation verifier."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

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
    if control.get("approved_gate") != "2R.6":
        errors.append(f"Gate 2R.7 implementation requires approved_gate=2R.6, found {control.get('approved_gate')!r}")
    if control.get("authorised_next_gate") != "2R.7":
        errors.append(f"Gate 2R.7 implementation requires authorised_next_gate=2R.7, found {control.get('authorised_next_gate')!r}")
    if control.get("authorised_next_gate") == "2R.8":
        errors.append("Gate 2R.8 is already authorised; refusing Gate 2R.7 implementation verification")
    if (ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r7_approvals.json").exists():
        errors.append("Gate 2R.7 approval manifest already exists; implementation verifier must run before approval")
    return errors


def _behavioral_errors() -> list[str]:
    errors: list[str] = []
    try:
        from dataclasses import replace

        from app.services.curriculum.tutor_grounding import (
            GROUNDING_STATUS_FALLBACK,
            GROUNDING_STATUS_PASSED,
            TUTOR_RESPONSE_GROUNDED,
            TUTOR_RESPONSE_SAFE_FALLBACK,
            TutorGroundingError,
            TutorRequestControls,
            build_gate2r7_fixture_response,
            build_gate2r7_fixture_service,
            build_gate2r7_tutor_packet,
            render_tutor_provenance_for_audience,
        )

        response = build_gate2r7_fixture_response()
        if response.response_status != TUTOR_RESPONSE_GROUNDED:
            errors.append("fixture tutor response is not grounded")
        if response.trace.grounding_status != GROUNDING_STATUS_PASSED:
            errors.append("fixture tutor trace did not pass grounding")
        if not response.trace.source_chunk_ids or not response.trace.source_snapshot_sha256:
            errors.append("fixture tutor trace lacks source provenance")
        if response.trace.claim_validation_status != "passed":
            errors.append("fixture tutor claim validation did not pass")
        service, request, store = build_gate2r7_fixture_service()
        grounded = service.answer(request)
        if len(store) != 1:
            errors.append("tutor provenance was not persisted")
        try:
            service.answer(request)
            errors.append("duplicate tutor_message_id was not rejected")
        except Exception:  # best-effort probe, cannot fail-close
            pass
        fallback = service.answer(replace(
            request,
            tutor_message_id="verify-g2r7-fallback",
            curriculum_node_version_ids=("node-does-not-exist",),
            learner_question="Explain an unsupported topic",
            safe_fallback_allowed=True,
        ))
        if fallback.response_status != TUTOR_RESPONSE_SAFE_FALLBACK or fallback.trace.grounding_status != GROUNDING_STATUS_FALLBACK:
            errors.append("safe fallback contract failed")
        if fallback.trace.source_chunk_ids or "CAPS requires" in fallback.learner_response:
            errors.append("safe fallback emitted authoritative grounding")
        try:
            service.answer(replace(
                request,
                tutor_message_id="verify-g2r7-no-fallback",
                curriculum_node_version_ids=("node-does-not-exist",),
                safe_fallback_allowed=False,
            ))
            errors.append("missing grounding without fallback did not fail closed")
        except Exception:  # best-effort probe, cannot fail-close
            pass
        try:
            service.answer(replace(
                request,
                tutor_message_id="verify-g2r7-consent",
                controls=TutorRequestControls(active_consent_verified=False),
            ))
            errors.append("failed consent control did not block tutor request")
        except Exception:  # best-effort probe, cannot fail-close
            pass
        learner_view = render_tutor_provenance_for_audience(grounded, "learner")
        auditor_view = render_tutor_provenance_for_audience(grounded, "auditor")
        if "source_chunk_version_ids" in learner_view:
            errors.append("learner provenance view exposes raw source chunk ids")
        if "source_references" not in auditor_view:
            errors.append("auditor provenance view lacks source references")
        packet1 = build_gate2r7_tutor_packet()
        packet2 = build_gate2r7_tutor_packet()
        if packet1.get("packet_sha256") != packet2.get("packet_sha256"):
            errors.append("tutor packet hash is not deterministic")
        if packet1.get("gate_boundary", {}).get("gate_2r8_authorised") is not False:
            errors.append("Gate 2R.7 packet must not authorise Gate 2R.8")
        if packet1.get("gate_boundary", {}).get("legacy_migration_wired") is not False:
            errors.append("Gate 2R.7 packet must not wire legacy migration")
    except Exception as exc:
        errors.append(f"Gate 2R.7 behavioral checks failed to execute: {exc}")
    return errors


def verify(mode: str) -> dict[str, Any]:
    from app.services.curriculum.phase02r_verification import validate_required_paths

    errors: list[str] = []
    checks: list[dict[str, Any]] = []
    errors.extend(_control_errors())
    errors.extend(validate_required_paths("2R.7"))

    compile_targets = [
        "app/services/curriculum/tutor_grounding.py",
        "app/services/curriculum/phase02r_verification.py",
        "scripts/verify_phase02r_gate2r7.py",
        "scripts/curriculum/build_phase02r_gate2r7_grounded_tutor.py",
        "scripts/curriculum/export_phase02r_gate2r7_tutor_packet.py",
        "scripts/curriculum/validate_phase02r_gate2r7_tutor.py",
        "tests/unit/phase02r/test_gate2r7_grounded_tutor.py",
    ]
    checks.append(_run([sys.executable, "-m", "compileall", "-q", *compile_targets]))
    if checks[-1]["exit_code"] != 0:
        errors.append("compileall failed for Gate 2R.7 files")

    for command, message in [
        ([sys.executable, "scripts/curriculum/build_phase02r_gate2r7_grounded_tutor.py", "--json"], "grounded tutor fixture build failed"),
        ([sys.executable, "scripts/curriculum/export_phase02r_gate2r7_tutor_packet.py", "--json"], "tutor packet export failed"),
        ([sys.executable, "scripts/curriculum/validate_phase02r_gate2r7_tutor.py", "--json"], "grounded tutor validation failed"),
        ([sys.executable, "scripts/verify_migration_graph.py"], "migration graph check failed"),
    ]:
        checks.append(_run(command))
        if checks[-1]["exit_code"] != 0:
            errors.append(message)

    errors.extend(_behavioral_errors())
    if mode == "closure":
        errors.append("Gate 2R.7 closure requires committed candidate evidence, approvals, and a separate transition; implementation verifier cannot close the gate")
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
        print(f"Phase 2R Gate 2R.7 {args.mode} verification passed")
    else:
        print(f"Phase 2R Gate 2R.7 {args.mode} verification failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
