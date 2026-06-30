#!/usr/bin/env python3
"""Validate Gate 2R.6 grounded generation fail-closed controls."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.corpus import ActiveCorpusRetriever, build_gate2r5_fixture_package
from app.services.curriculum.generation import (
    GROUND_VERIFIED_STATUS,
    GroundedGenerationRejectedError,
    GroundedGenerationRequest,
    GroundedGenerationService,
    build_gate2r6_fixture_artifact,
    build_gate2r6_generation_packet,
)


def validate() -> dict[str, object]:
    errors: list[str] = []
    checks: dict[str, object] = {}
    manifest, projection, binding, _ = build_gate2r5_fixture_package()
    service = GroundedGenerationService(retriever=ActiveCorpusRetriever(projection, binding))
    request = GroundedGenerationRequest(
        artifact_type="lesson_with_assessment",
        activation_key=binding.activation_key,
        corpus_version_id=binding.corpus_version_id,
        binding_epoch=binding.binding_epoch,
        language=manifest.language,
        topic="compare whole numbers and place value",
        objective_ids=("node-g4math-numbers-whole-numbers-v1",),
        top_k=2,
    )
    artifact = service.generate(request)
    checks["artifact_id"] = artifact.artifact_id
    checks["artifact_sha256"] = artifact.artifact_sha256
    checks["source_reference_count"] = len(artifact.source_references)
    if artifact.status != GROUND_VERIFIED_STATUS:
        errors.append("grounded generation artifact must be grounded_verified")
    if not artifact.grounding_decision.passed:
        errors.append("grounding decision must pass")
    if not artifact.source_snapshot_hash or len(artifact.source_snapshot_hash) != 64:
        errors.append("source snapshot hash must be present")
    if not artifact.claims:
        errors.append("artifact must carry validated claims")
    if not artifact.assessment_items:
        errors.append("lesson_with_assessment must include assessment items")
    if any(item.answer_verification_status != "passed" for item in artifact.assessment_items):
        errors.append("all assessment answers must pass deterministic verification")
    try:
        service.generate(replace(request, objective_ids=("node-does-not-exist",)))
        errors.append("unknown objective generation did not fail closed")
    except GroundedGenerationRejectedError:
        checks["unknown_objective_rejected"] = True
    fallback = service.generate(replace(request, objective_ids=("node-does-not-exist",), safe_fallback_allowed=True))
    if fallback.status != "safe_fallback":
        errors.append("explicit safe fallback did not return safe_fallback status")
    packet1 = build_gate2r6_generation_packet()
    packet2 = build_gate2r6_generation_packet()
    checks["packet_sha256"] = packet1.get("packet_sha256")
    if packet1.get("packet_sha256") != packet2.get("packet_sha256"):
        errors.append("generation packet export is not deterministic")
    if packet1.get("gate_boundary", {}).get("tutor_runtime_wired") is not False:
        errors.append("Gate 2R.6 packet must not wire tutor runtime")
    if packet1.get("gate_boundary", {}).get("learner_facing_endpoint_wired") is not False:
        errors.append("Gate 2R.6 packet must not wire learner-facing endpoint")
    if build_gate2r6_fixture_artifact("assessment").lesson_sections:
        errors.append("assessment-only artifact should not include lesson sections")
    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print("Phase 2R Gate 2R.6 grounded generation validation passed")
    else:
        print("Phase 2R Gate 2R.6 grounded generation validation failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
