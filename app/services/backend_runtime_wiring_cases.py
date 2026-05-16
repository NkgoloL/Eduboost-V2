from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.audit_migration_orchestrator import build_audit_migration_event
from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload
from app.services.deep_readiness_route_contracts import DEFAULT_DEEP_READINESS_CHECKS


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "backend_consolidation"

AUDIT_CASES_PATH = FIXTURE_DIR / "audit_runtime_wiring_cases.json"
CONSENT_CASES_PATH = FIXTURE_DIR / "consent_runtime_wiring_cases.json"
READINESS_CASES_PATH = FIXTURE_DIR / "deep_readiness_route_wiring_cases.json"


@dataclass(frozen=True)
class WiringCaseResult:
    case_name: str
    passed: bool
    message: str
    details: dict[str, Any]


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError(f"{path} must contain cases list")
    return cases


def run_audit_wiring_cases() -> tuple[WiringCaseResult, ...]:
    results: list[WiringCaseResult] = []
    for case in _load_cases(AUDIT_CASES_PATH):
        envelope = build_audit_migration_event(
            candidate_name=case["candidate_name"],
            action=case["action"],
            actor_id=case.get("actor_id"),
            learner_id=case.get("learner_id"),
            resource_type=case.get("resource_type"),
        )
        payload = envelope.to_event_input().to_canonical_payload()
        expected_metadata = case.get("expected_metadata", {})
        metadata = payload["payload"]
        passed = (
            payload["action"] == case["action"]
            and payload["resource_id"] == case["expected_resource_id"]
            and all(metadata.get(key) == value for key, value in expected_metadata.items())
        )
        results.append(
            WiringCaseResult(
                case_name=case["name"],
                passed=passed,
                message="audit fixture maps to canonical payload",
                details={"payload": payload},
            )
        )
    return tuple(results)


def run_consent_wiring_cases() -> tuple[WiringCaseResult, ...]:
    results: list[WiringCaseResult] = []
    for case in _load_cases(CONSENT_CASES_PATH):
        payload = build_consent_runtime_audit_payload(
            action=case["action"],
            actor_id=case["actor_id"],
            learner_id=case["learner_id"],
        )
        metadata = payload["metadata"]
        passed = (
            payload["resource_type"] == case["expected_resource_type"]
            and metadata["operation_type"] == case["expected_operation_type"]
            and payload["resource_id"] == case["learner_id"]
        )
        results.append(
            WiringCaseResult(
                case_name=case["name"],
                passed=passed,
                message="consent fixture maps to audit-compatible payload",
                details={"payload": payload},
            )
        )
    return tuple(results)


def run_deep_readiness_wiring_cases() -> tuple[WiringCaseResult, ...]:
    catalogue = {check.name: check for check in DEFAULT_DEEP_READINESS_CHECKS}
    results: list[WiringCaseResult] = []
    for case in _load_cases(READINESS_CASES_PATH):
        check = catalogue.get(case["name"])
        if check is None:
            results.append(
                WiringCaseResult(
                    case_name=case["name"],
                    passed=False,
                    message="deep-readiness case missing from catalogue",
                    details={},
                )
            )
            continue

        passed = (
            check.required_for_release == case["required_for_release"]
            and check.public_safe == case["public_safe"]
            and check.mutates_state == case["mutates_state"]
        )
        results.append(
            WiringCaseResult(
                case_name=case["name"],
                passed=passed,
                message="deep-readiness fixture matches catalogue",
                details={
                    "mode": check.mode.value,
                    "dependency": check.dependency,
                    "public_safe": check.public_safe,
                    "mutates_state": check.mutates_state,
                    "required_for_release": check.required_for_release,
                },
            )
        )
    return tuple(results)


def run_all_wiring_cases() -> tuple[WiringCaseResult, ...]:
    return (
        *run_audit_wiring_cases(),
        *run_consent_wiring_cases(),
        *run_deep_readiness_wiring_cases(),
    )


def all_wiring_cases_pass() -> bool:
    return all(result.passed for result in run_all_wiring_cases())


__all__ = [
    "AUDIT_CASES_PATH",
    "CONSENT_CASES_PATH",
    "READINESS_CASES_PATH",
    "WiringCaseResult",
    "all_wiring_cases_pass",
    "run_all_wiring_cases",
    "run_audit_wiring_cases",
    "run_consent_wiring_cases",
    "run_deep_readiness_wiring_cases",
]
