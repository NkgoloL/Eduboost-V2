from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any


VALID_STATUSES = {
    "not-started",
    "static-passing",
    "runtime-passing",
    "integration-passing",
    "production-ready",
    "config-passing",
    "policy-accepted",
    "external-blocked",
    "contradicted",
    "not-proven",
}

P0_P1 = {"P0", "P1"}
PROVEN_STATUSES = {"runtime-passing", "integration-passing", "production-ready"}


@dataclass(frozen=True)
class EvidenceFinding:
    id: str
    title: str
    severity: str
    gate: str
    owner: str
    implementation_batch: str
    proof_status: str
    proof_command: str
    evidence_file: str | None
    last_verified_commit: str | None
    closure_blocker: str | None
    blocks_beta: bool
    external_dependency: bool


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "~", ""}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_registry(path: Path) -> list[EvidenceFinding]:
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "findings:":
            continue
        if stripped.startswith("- "):
            if current:
                findings.append(current)
            current = {}
            remainder = stripped[2:].strip()
            if remainder:
                key, _, value = remainder.partition(":")
                current[key.strip()] = _parse_scalar(value)
            continue
        if current is not None and ":" in stripped:
            key, _, value = stripped.partition(":")
            current[key.strip()] = _parse_scalar(value)

    if current:
        findings.append(current)
    allowed_fields = {field.name for field in fields(EvidenceFinding)}
    return [EvidenceFinding(**{key: value for key, value in item.items() if key in allowed_fields}) for item in findings]


def validate_registry(findings: list[EvidenceFinding], root: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()

    for finding in findings:
        if finding.id in seen:
            errors.append(f"duplicate finding id: {finding.id}")
        seen.add(finding.id)

        if finding.proof_status not in VALID_STATUSES:
            errors.append(f"{finding.id}: invalid proof_status {finding.proof_status!r}")

        if finding.severity in P0_P1 and finding.proof_status == "static-passing":
            errors.append(f"{finding.id}: P0/P1 item cannot close on static-passing proof")

        if finding.proof_status in PROVEN_STATUSES and not finding.last_verified_commit:
            errors.append(f"{finding.id}: {finding.proof_status} requires last_verified_commit")

        if finding.proof_status == "production-ready":
            if not finding.evidence_file:
                errors.append(f"{finding.id}: production-ready requires evidence_file")
            if finding.closure_blocker:
                errors.append(f"{finding.id}: production-ready cannot have closure_blocker")

        if finding.blocks_beta and finding.proof_status in {"not-started", "static-passing", "not-proven", "contradicted"}:
            if not finding.closure_blocker:
                errors.append(f"{finding.id}: beta-blocking incomplete item must name closure_blocker")

        if finding.evidence_file and finding.evidence_file not in {"null", "~"}:
            evidence_path = root / finding.evidence_file
            if (
                not finding.external_dependency
                and finding.proof_status in PROVEN_STATUSES
                and not evidence_path.exists()
            ):
                errors.append(f"{finding.id}: evidence_file missing: {finding.evidence_file}")

    return errors
