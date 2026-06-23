"""Phase 02R Gate 2R.8 audit and closure-readiness aggregation."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.services.curriculum.evaluation import build_gate2r8_evaluation_report, sha256_json
from app.services.curriculum.legacy_migration import build_gate2r8_legacy_migration_manifest


CLOSURE_POLICY_VERSION = "phase02r-gate2r8-closure-v1"
REQUIRED_PREVIOUS_GATES = ("2R.4", "2R.5", "2R.6", "2R.7")


class Phase02RClosureRejectedError(ValueError):
    """Raised when Phase 02R closure readiness cannot be demonstrated."""


@dataclass(frozen=True)
class EvidenceReference:
    gate: str
    evidence_index_path: str
    approval_manifest_path: str
    evidence_index_sha256: str | None
    approval_decision: str | None
    authorised_next_gate: str | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Gate2R8ClosureReadiness:
    policy_version: str
    status: str
    evidence_references: tuple[EvidenceReference, ...]
    evaluation_status: str
    legacy_migration_status: str
    failure_reasons: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "policy_version": self.policy_version,
            "status": self.status,
            "evidence_references": [ref.as_dict() for ref in self.evidence_references],
            "evaluation_status": self.evaluation_status,
            "legacy_migration_status": self.legacy_migration_status,
            "failure_reasons": list(self.failure_reasons),
        }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_previous_gate_references(root: Path) -> tuple[EvidenceReference, ...]:
    refs: list[EvidenceReference] = []
    for gate in REQUIRED_PREVIOUS_GATES:
        gate_file = gate.replace(".", "").lower()
        gate_dir = gate.lower().replace(".", "")
        evidence_path = root / f"docs/release-evidence/atlas/phase-02r/gate-{gate_dir}/evidence_index.md"
        approval_path = root / f"docs/roadmap/execution/atlas/phase_02r_gate_{gate_file}_approvals.json"
        approval: dict[str, Any] = {}
        if approval_path.exists():
            approval = _load_json(approval_path)
        refs.append(
            EvidenceReference(
                gate=gate,
                evidence_index_path=str(evidence_path.relative_to(root)),
                approval_manifest_path=str(approval_path.relative_to(root)),
                evidence_index_sha256=file_sha256(evidence_path) if evidence_path.exists() else None,
                approval_decision=approval.get("decision"),
                authorised_next_gate=approval.get("authorised_next_gate"),
            )
        )
    return tuple(refs)


def evaluate_closure_readiness(root: Path) -> Gate2R8ClosureReadiness:
    refs = collect_previous_gate_references(root)
    failures: list[str] = []
    for ref in refs:
        if ref.evidence_index_sha256 is None:
            failures.append(f"missing evidence index for {ref.gate}")
        if ref.approval_decision != "approved_with_disclosed_self_review_exception":
            failures.append(f"missing approved manifest for {ref.gate}")
    eval_report = build_gate2r8_evaluation_report()
    legacy_manifest = build_gate2r8_legacy_migration_manifest()
    if eval_report.get("status") != "passed":
        failures.append("Gate 2R.8 evaluation report did not pass")
    if legacy_manifest.get("status") != "ready_for_review":
        failures.append("Gate 2R.8 legacy migration manifest is not review-ready")
    return Gate2R8ClosureReadiness(
        policy_version=CLOSURE_POLICY_VERSION,
        status="ready_for_candidate_closure_evidence" if not failures else "blocked",
        evidence_references=refs,
        evaluation_status=str(eval_report.get("status")),
        legacy_migration_status=str(legacy_manifest.get("status")),
        failure_reasons=tuple(failures),
    )


def build_gate2r8_audit_bundle(root: Path) -> dict[str, Any]:
    closure = evaluate_closure_readiness(root)
    evaluation_report = build_gate2r8_evaluation_report()
    legacy_manifest = build_gate2r8_legacy_migration_manifest()
    payload = {
        "gate": "2R.8",
        "policy_version": CLOSURE_POLICY_VERSION,
        "closure_readiness": closure.as_dict(),
        "evaluation_report_sha256": evaluation_report.get("report_sha256"),
        "legacy_migration_manifest_sha256": legacy_manifest.get("manifest_sha256"),
        "evidence_reference_count": len(closure.evidence_references),
        "gate_boundary": {
            "phase_02r_completion_declared": False,
            "production_activation_performed": False,
            "legacy_migration_executed": False,
            "live_database_executed": False,
        },
    }
    payload["audit_bundle_sha256"] = sha256_json(payload)
    return payload


__all__ = [
    "CLOSURE_POLICY_VERSION",
    "REQUIRED_PREVIOUS_GATES",
    "EvidenceReference",
    "Gate2R8ClosureReadiness",
    "Phase02RClosureRejectedError",
    "build_gate2r8_audit_bundle",
    "collect_previous_gate_references",
    "evaluate_closure_readiness",
    "file_sha256",
]
