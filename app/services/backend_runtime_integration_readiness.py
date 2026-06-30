from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from app.services.first_audit_runtime_wiring import (
    InMemoryFirstAuditRuntimeSink,
    record_first_audit_runtime_candidate,
)
from app.services.first_consent_runtime_wiring import build_first_consent_runtime_payload
from app.services.first_deep_readiness_runtime_wiring import build_first_deep_readiness_runtime_plan


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "tests" / "fixtures" / "backend_consolidation" / "runtime_integration_readiness_registry.json"


class IntegrationArea(str, Enum):
    AUDIT = "audit"
    CONSENT = "consent"
    DEEP_READINESS = "deep_readiness"


@dataclass(frozen=True)
class RuntimeIntegrationTarget:
    id: str
    area: IntegrationArea
    candidate_id: str
    target_kind: str
    dry_run_supported: bool
    runtime_wiring_allowed: bool
    requires_route_registration: bool
    requires_schema_change: bool
    destructive: bool


@dataclass(frozen=True)
class RuntimeIntegrationDryRunResult:
    target_id: str
    area: IntegrationArea
    passed: bool
    message: str
    details: dict[str, Any]


def load_runtime_integration_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_runtime_integration_targets(path: Path = REGISTRY_PATH) -> tuple[RuntimeIntegrationTarget, ...]:
    payload = load_runtime_integration_registry(path)
    targets = []
    for item in payload.get("integration_targets", []):
        targets.append(
            RuntimeIntegrationTarget(
                id=item["id"],
                area=IntegrationArea(item["area"]),
                candidate_id=item["candidate_id"],
                target_kind=item["target_kind"],
                dry_run_supported=bool(item["dry_run_supported"]),
                runtime_wiring_allowed=bool(item["runtime_wiring_allowed"]),
                requires_route_registration=bool(item["requires_route_registration"]),
                requires_schema_change=bool(item["requires_schema_change"]),
                destructive=bool(item["destructive"]),
            )
        )
    return tuple(targets)


def safe_dry_run_targets() -> tuple[RuntimeIntegrationTarget, ...]:
    return tuple(
        target
        for target in load_runtime_integration_targets()
        if target.dry_run_supported
        and not target.runtime_wiring_allowed
        and not target.requires_route_registration
        and not target.requires_schema_change
        and not target.destructive
    )


def blocked_changes(path: Path = REGISTRY_PATH) -> tuple[str, ...]:
    return tuple(load_runtime_integration_registry(path).get("blocked_changes", []))


async def _run_audit_dry_run(target: RuntimeIntegrationTarget) -> RuntimeIntegrationDryRunResult:
    sink = InMemoryFirstAuditRuntimeSink()
    result = await record_first_audit_runtime_candidate(sink)
    passed = result.recorded and len(sink.events) == 1 and sink.events[0]["resource_id"] == "learner-runtime-pr"
    return RuntimeIntegrationDryRunResult(
        target_id=target.id,
        area=target.area,
        passed=passed,
        message="audit runtime candidate dry-run recorded to in-memory sink",
        details={"event_count": len(sink.events), "response": result.response},
    )


def _run_consent_dry_run(target: RuntimeIntegrationTarget) -> RuntimeIntegrationDryRunResult:
    payload = build_first_consent_runtime_payload().payload
    passed = payload["resource_id"] == "learner-consent-runtime-pr" and payload["metadata"]["operation_type"] == "write"
    return RuntimeIntegrationDryRunResult(
        target_id=target.id,
        area=target.area,
        passed=passed,
        message="consent runtime candidate dry-run produced audit-compatible payload",
        details={"action": payload["action"], "resource_id": payload["resource_id"], "operation_type": payload["metadata"]["operation_type"]},
    )


def _run_deep_readiness_dry_run(target: RuntimeIntegrationTarget) -> RuntimeIntegrationDryRunResult:
    plan = build_first_deep_readiness_runtime_plan()
    passed = plan.public_safe and not plan.mutates_state and bool(plan.checks)
    return RuntimeIntegrationDryRunResult(
        target_id=target.id,
        area=target.area,
        passed=passed,
        message="deep-readiness runtime candidate dry-run produced read-only plan",
        details={"check_count": len(plan.checks), "checks": list(plan.checks)},
    )


async def run_runtime_integration_dry_runs() -> tuple[RuntimeIntegrationDryRunResult, ...]:
    results: list[RuntimeIntegrationDryRunResult] = []
    for target in safe_dry_run_targets():
        if target.area is IntegrationArea.AUDIT:
            results.append(await _run_audit_dry_run(target))
        elif target.area is IntegrationArea.CONSENT:
            results.append(_run_consent_dry_run(target))
        elif target.area is IntegrationArea.DEEP_READINESS:
            results.append(_run_deep_readiness_dry_run(target))
        else:
            results.append(
                RuntimeIntegrationDryRunResult(
                    target_id=target.id,
                    area=target.area,
                    passed=False,
                    message=f"unsupported target area: {target.area}",
                    details={},
                )
            )
    return tuple(results)


def run_runtime_integration_dry_runs_sync() -> tuple[RuntimeIntegrationDryRunResult, ...]:
    return asyncio.run(run_runtime_integration_dry_runs())


def runtime_integration_ready_for_pr_planning() -> bool:
    results = run_runtime_integration_dry_runs_sync()
    return bool(results) and all(result.passed for result in results)


__all__ = [
    "REGISTRY_PATH",
    "IntegrationArea",
    "RuntimeIntegrationDryRunResult",
    "RuntimeIntegrationTarget",
    "blocked_changes",
    "load_runtime_integration_registry",
    "load_runtime_integration_targets",
    "runtime_integration_ready_for_pr_planning",
    "run_runtime_integration_dry_runs",
    "run_runtime_integration_dry_runs_sync",
    "safe_dry_run_targets",
]
