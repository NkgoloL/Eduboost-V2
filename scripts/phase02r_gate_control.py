#!/usr/bin/env python3
"""Validate Phase 2R gate-state, evidence, approvals, and transition consistency.

This version is gate-aware for Gate 2R.1 and later transitions. It validates
whichever gate is recorded as approved in phase_02r_start_gate_control.json,
not only Gate 2R.1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTROL_PATH = ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json"
AUTOMATION_PATH = ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_automation.json"
PLAN_PATH = ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
GATE_ORDER = ["2R.0", "2R.1", "2R.2", "2R.3", "2R.4", "2R.5", "2R.6", "2R.7", "2R.8"]
REQUIRED_ROLES = {
    "engineering_approver",
    "rights_reviewer",
    "curriculum_reviewer",
    "evidence_custodian",
    "release_manager",
}
APPROVED_DECISIONS = {"approved", "approved_with_disclosed_self_review_exception"}


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing control artifact: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def _parse_time(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field} is required")
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} must be ISO-8601")
        return None


def _gate_slug(gate: str) -> str:
    return gate.lower().replace(".", "")


def _approvals_path(gate: str) -> Path:
    return ROOT / f"docs/roadmap/execution/atlas/phase_02r_gate_{_gate_slug(gate)}_approvals.json"


def _evidence_index_path(gate: str) -> Path:
    return ROOT / f"docs/release-evidence/atlas/phase-02r/gate-{_gate_slug(gate)}/evidence_index.md"


def _evidence_raw_dir(gate: str) -> Path:
    return ROOT / f"docs/release-evidence/atlas/phase-02r/gate-{_gate_slug(gate)}/raw"


def _evidence_index_metadata(gate: str, path: Path, errors: list[str]) -> tuple[datetime | None, str | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"Gate {gate} evidence index is missing")
        return None, None, None
    generated_match = re.search(r"\*\*Generated:\*\*\s+(.+)", text)
    source_match = re.search(r"\*\*Source commit:\*\*\s+`([0-9a-f]{40})`", text)
    status_match = re.search(r"\*\*Status:\*\*\s+(.+)", text)
    generated = _parse_time(generated_match.group(1).strip() if generated_match else None, f"Gate {gate} evidence index Generated", errors)
    if not source_match:
        errors.append(f"Gate {gate} evidence index lacks a 40-character source commit")
    status = status_match.group(1).strip() if status_match else None
    if status != "Candidate verification passed — human approval pending":
        errors.append(f"Gate {gate} evidence index is not a passing candidate evidence record")
    return generated, source_match.group(1) if source_match else None, status


def _validate_raw_checksums(gate: str, raw_dir: Path, errors: list[str]) -> None:
    manifest = raw_dir / "SHA256SUMS.txt"
    if not manifest.is_file():
        errors.append(f"Gate {gate} raw SHA256SUMS.txt is missing")
        return
    for line_number, raw_line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})\s{2}(.+)", line)
        if not match:
            errors.append(f"Gate {gate} invalid raw checksum line {line_number}")
            continue
        expected, name = match.groups()
        candidate = raw_dir / name
        if not candidate.is_file():
            errors.append(f"Gate {gate} raw evidence file is missing: {name}")
            continue
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"Gate {gate} raw evidence checksum mismatch: {name}")


def _validate_plan_current_state(authorised_gate: str, approved_gate: str, errors: list[str]) -> None:
    try:
        plan = PLAN_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("Phase 2R execution plan is missing")
        return
    expected_auth = f"**Execution authorisation:** Gate {authorised_gate} only"
    if expected_auth not in plan:
        errors.append(f"execution plan is missing current execution authorisation statement: {expected_auth}")
    expected_status = f"Gate {approved_gate} verified complete; Gate {authorised_gate} authorised"
    if approved_gate != "2R.0" and expected_status not in plan:
        errors.append(f"execution plan is missing current gate status phrase: {expected_status}")


def _validate_gate_approval(
    *,
    approved_gate: str,
    authorised_gate: str,
    control: dict[str, Any],
    require_approval_roles: bool,
    require_evidence_index_sha: bool,
    errors: list[str],
) -> None:
    if approved_gate == "2R.0":
        if require_approval_roles:
            errors.append("--require-approval-roles is only valid after Gate 2R.1 or later approval")
        if require_evidence_index_sha:
            errors.append("--require-evidence-index-sha is only valid after Gate 2R.1 or later approval")
        return

    approvals_path = _approvals_path(approved_gate)
    evidence_index = _evidence_index_path(approved_gate)
    raw_dir = _evidence_raw_dir(approved_gate)

    evidence_generated, evidence_source_sha, _evidence_status = _evidence_index_metadata(approved_gate, evidence_index, errors)
    _validate_raw_checksums(approved_gate, raw_dir, errors)
    try:
        approvals = _load(approvals_path)
    except ValueError as exc:
        errors.append(str(exc))
        return

    if approvals.get("gate") != approved_gate:
        errors.append(f"Gate {approved_gate} approvals manifest has wrong gate")
    if approvals.get("decision") not in APPROVED_DECISIONS or approvals.get("authorised_next_gate") != authorised_gate:
        errors.append(f"Gate {approved_gate} approvals do not authorise Gate {authorised_gate}")
    if approvals.get("evidence_source_sha") != evidence_source_sha:
        errors.append(f"Gate {approved_gate} approvals do not reference the evidence source commit")

    evidence_commit_sha = str(approvals.get("evidence_commit_sha") or "")
    approval_decision_commit_sha = str(control.get("approval_decision_commit_sha") or "")
    transition_commit_sha = str(control.get("transition_commit_sha") or "")
    remote_branch_sha_at_transition = str(control.get("remote_branch_sha_at_transition") or "")
    if not SHA_RE.fullmatch(evidence_commit_sha):
        errors.append(f"Gate {approved_gate} approvals require a real evidence_commit_sha")
    if not SHA_RE.fullmatch(approval_decision_commit_sha):
        errors.append("control.approval_decision_commit_sha must be a real 40-character lowercase Git SHA")
    if not SHA_RE.fullmatch(transition_commit_sha):
        errors.append("control.transition_commit_sha must be a real 40-character lowercase Git SHA")
    if not SHA_RE.fullmatch(remote_branch_sha_at_transition):
        errors.append("control.remote_branch_sha_at_transition must be a real 40-character lowercase Git SHA")
    if control.get("evidence_commit_sha") != evidence_commit_sha:
        errors.append("gate control evidence_commit_sha must equal the approved evidence commit")
    if approval_decision_commit_sha == evidence_commit_sha:
        errors.append("approval decision commit must be separate from the evidence commit")
    if transition_commit_sha == evidence_commit_sha:
        errors.append("transition commit must be separate from the evidence commit")
    if transition_commit_sha == approval_decision_commit_sha:
        errors.append("transition commit must be separate from the approval decision commit")
    if remote_branch_sha_at_transition != transition_commit_sha:
        errors.append("remote_branch_sha_at_transition must equal the transition_commit_sha")

    approved_roles: set[str] = set()
    decision_times: list[datetime] = []
    for item in approvals.get("decisions", []):
        decided_at = _parse_time(item.get("decided_at"), f"approval {item.get('role')} decided_at", errors) if item.get("decision") == "approved" else None
        if (
            item.get("decision") == "approved"
            and item.get("reviewer")
            and decided_at is not None
            and item.get("immutable_reference") == evidence_commit_sha
        ):
            approved_roles.add(str(item.get("role")))
            decision_times.append(decided_at)
            if evidence_generated and decided_at < evidence_generated:
                errors.append(f"approval {item.get('role')} predates candidate evidence")
    if require_approval_roles:
        missing_roles = REQUIRED_ROLES - approved_roles
        if missing_roles:
            errors.append(f"Gate {approved_gate} approvals missing roles: {', '.join(sorted(missing_roles))}")

    if require_evidence_index_sha and evidence_index.exists():
        expected = approvals.get("evidence_index_sha256")
        actual = hashlib.sha256(evidence_index.read_bytes()).hexdigest()
        if expected != actual:
            errors.append(f"Gate {approved_gate} approval evidence_index_sha256 does not match")

    control_time = _parse_time(control.get("approved_at"), "control.approved_at", errors)
    overall_decision_time = _parse_time(approvals.get("decided_at"), f"Gate {approved_gate} approvals decided_at", errors)
    if evidence_generated and overall_decision_time and overall_decision_time < evidence_generated:
        errors.append(f"Gate {approved_gate} overall decision predates candidate evidence")
    if control_time and decision_times and control_time < max(decision_times):
        errors.append("gate transition approval predates one or more required reviewer decisions")


def validate_state(
    *,
    expected_authorised_gate: str | None = None,
    expected_approved_gate: str | None = None,
    require_approval_roles: bool = False,
    require_evidence_index_sha: bool = False,
) -> list[str]:
    errors: list[str] = []
    try:
        control = _load(CONTROL_PATH)
        automation = _load(AUTOMATION_PATH)
    except ValueError as exc:
        return [str(exc)]

    if control.get("phase") != "02R":
        errors.append("control.phase must be 02R")
    if not isinstance(control.get("start_approved"), bool):
        errors.append("control.start_approved must be boolean")

    approved_gate = str(control.get("approved_gate") or "")
    authorised_gate = str(control.get("authorised_next_gate") or "")
    if approved_gate not in GATE_ORDER:
        errors.append("control.approved_gate is invalid")
    if authorised_gate not in GATE_ORDER:
        errors.append("control.authorised_next_gate is invalid")
    if expected_approved_gate and approved_gate != expected_approved_gate:
        errors.append(f"approved_gate must be {expected_approved_gate}")
    if expected_authorised_gate and authorised_gate != expected_authorised_gate:
        errors.append(f"authorised_next_gate must be {expected_authorised_gate}")
    if approved_gate in GATE_ORDER and authorised_gate in GATE_ORDER:
        if GATE_ORDER.index(authorised_gate) != GATE_ORDER.index(approved_gate) + 1:
            errors.append("authorised_next_gate must be exactly one gate after approved_gate")

    if control.get("start_approved") is True:
        for field in ("approval_decision_commit_sha", "evidence_commit_sha", "transition_commit_sha", "remote_branch_sha_at_transition"):
            if not SHA_RE.fullmatch(str(control.get(field, ""))):
                errors.append(f"control.{field} must be a real 40-character lowercase Git SHA")
        _parse_time(control.get("approved_at"), "control.approved_at", errors)

    supported = (automation.get("supported_gates") or {}).get(authorised_gate, {})
    if authorised_gate and not all(supported.get(name) is True for name in ("preflight", "verify", "collect")):
        errors.append(f"automation for authorised gate {authorised_gate} is incomplete")
    if authorised_gate != "2R.0" and supported.get("apply") is not True:
        errors.append(f"automation for authorised gate {authorised_gate} lacks apply support")

    if approved_gate in GATE_ORDER and authorised_gate in GATE_ORDER:
        _validate_plan_current_state(authorised_gate, approved_gate, errors)
        _validate_gate_approval(
            approved_gate=approved_gate,
            authorised_gate=authorised_gate,
            control=control,
            require_approval_roles=require_approval_roles,
            require_evidence_index_sha=require_evidence_index_sha,
            errors=errors,
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-approved-gate")
    parser.add_argument("--expected-authorised-gate")
    parser.add_argument("--require-approval-roles", action="store_true")
    parser.add_argument("--require-evidence-index-sha", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors = validate_state(
        expected_authorised_gate=args.expected_authorised_gate,
        expected_approved_gate=args.expected_approved_gate,
        require_approval_roles=args.require_approval_roles,
        require_evidence_index_sha=args.require_evidence_index_sha,
    )
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2, sort_keys=True))
    elif errors:
        print("Phase 2R gate-control validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("Phase 2R gate-control validation passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
