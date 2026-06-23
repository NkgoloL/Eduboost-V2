#!/usr/bin/env python3
"""Validate Gate 2R.7 grounded tutor controls and fallbacks."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


def validate() -> dict[str, object]:
    errors: list[str] = []
    checks: dict[str, object] = {}

    response = build_gate2r7_fixture_response()
    checks["grounded_tutor_message_id"] = response.tutor_message_id
    checks["grounded_provenance_sha256"] = response.provenance_sha256
    if response.response_status != TUTOR_RESPONSE_GROUNDED:
        errors.append("fixture response must be grounded_tutor_response")
    if response.trace.grounding_status != GROUNDING_STATUS_PASSED:
        errors.append("grounded response trace must have passed grounding")
    if not response.trace.source_chunk_ids:
        errors.append("grounded response must carry source_chunk_ids")
    if not response.trace.source_snapshot_sha256 or len(response.trace.source_snapshot_sha256) != 64:
        errors.append("grounded response must carry source_snapshot_sha256")
    if response.trace.claim_validation_status != "passed":
        errors.append("grounded response must carry passing claim validation")

    service, request, store = build_gate2r7_fixture_service()
    first = service.answer(request)
    checks["persisted_record_count_after_grounded"] = len(store)
    if len(store) != 1 or store.get(first.tutor_message_id).source_chunk_ids != first.trace.source_chunk_ids:
        errors.append("grounded tutor provenance was not persisted")
    try:
        service.answer(request)
        errors.append("append-only provenance allowed duplicate tutor_message_id")
    except TutorGroundingError:
        checks["duplicate_provenance_rejected"] = True

    fallback = service.answer(
        replace(
            request,
            tutor_message_id="tutor-msg-g2r7-validation-fallback",
            curriculum_dependent=True,
            curriculum_node_version_ids=("node-does-not-exist",),
            learner_question="Explain this topic without source evidence",
            safe_fallback_allowed=True,
        )
    )
    if fallback.response_status != TUTOR_RESPONSE_SAFE_FALLBACK:
        errors.append("missing active grounding must produce explicit safe fallback when allowed")
    if fallback.trace.grounding_status != GROUNDING_STATUS_FALLBACK:
        errors.append("fallback trace must have fallback grounding status")
    if fallback.trace.source_chunk_ids:
        errors.append("fallback must not cite source chunks as authoritative grounding")
    if "CAPS requires" in fallback.learner_response:
        errors.append("fallback must not emit CAPS authority claims")

    try:
        service.answer(
            replace(
                request,
                tutor_message_id="tutor-msg-g2r7-validation-no-fallback",
                curriculum_node_version_ids=("node-does-not-exist",),
                safe_fallback_allowed=False,
            )
        )
        errors.append("missing grounding without fallback did not fail closed")
    except TutorGroundingError:
        checks["missing_grounding_without_fallback_rejected"] = True

    try:
        service.answer(
            replace(
                request,
                tutor_message_id="tutor-msg-g2r7-validation-controls",
                controls=TutorRequestControls(active_consent_verified=False),
            )
        )
        errors.append("failed consent control did not reject tutor request")
    except TutorGroundingError:
        checks["failed_consent_control_rejected"] = True

    learner_view = render_tutor_provenance_for_audience(response, "learner")
    auditor_view = render_tutor_provenance_for_audience(response, "auditor")
    if "source_chunk_version_ids" in learner_view:
        errors.append("learner provenance view should not expose raw source chunk ids")
    if "source_references" not in auditor_view:
        errors.append("auditor provenance view must expose full source references")

    packet1 = build_gate2r7_tutor_packet()
    packet2 = build_gate2r7_tutor_packet()
    checks["packet_sha256"] = packet1.get("packet_sha256")
    if packet1.get("packet_sha256") != packet2.get("packet_sha256"):
        errors.append("tutor packet export is not deterministic")
    if packet1.get("gate_boundary", {}).get("gate_2r8_authorised") is not False:
        errors.append("Gate 2R.7 package must not authorise Gate 2R.8")
    if packet1.get("gate_boundary", {}).get("legacy_migration_wired") is not False:
        errors.append("Gate 2R.7 package must not wire Gate 2R.8 legacy migration")
    if len(packet1.get("persisted_provenance_records", [])) < 2:
        errors.append("tutor packet must include grounded and fallback provenance records")

    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print("Phase 2R Gate 2R.7 grounded tutor validation passed")
    else:
        print("Phase 2R Gate 2R.7 grounded tutor validation failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
