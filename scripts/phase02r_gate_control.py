#!/usr/bin/env python3
"""Validate Phase 2R gate-state, automation, plan, and approval consistency."""
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
APPROVALS_2R1_PATH = ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r1_approvals.json"
EVIDENCE_2R1_INDEX = ROOT / "docs/release-evidence/atlas/phase-02r/gate-2r1/evidence_index.md"
EVIDENCE_2R1_RAW = ROOT / "docs/release-evidence/atlas/phase-02r/gate-2r1/raw"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
GATE_ORDER = ["2R.0", "2R.1", "2R.2", "2R.3", "2R.4", "2R.5", "2R.6", "2R.7", "2R.8"]


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


def _evidence_index_metadata(path: Path, errors: list[str]) -> tuple[datetime | None, str | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("Gate 2R.1 evidence index is missing")
        return None, None, None
    generated_match = re.search(r"\*\*Generated:\*\*\s+(.+)", text)
    source_match = re.search(r"\*\*Source commit:\*\*\s+`([0-9a-f]{40})`", text)
    status_match = re.search(r"\*\*Status:\*\*\s+(.+)", text)
    generated = _parse_time(generated_match.group(1).strip() if generated_match else None, "evidence index Generated", errors)
    if not source_match:
        errors.append("Gate 2R.1 evidence index lacks a 40-character source commit")
    status = status_match.group(1).strip() if status_match else None
    if status != "Candidate verification passed — human approval pending":
        errors.append("Gate 2R.1 evidence index is not a passing candidate evidence record")
    return generated, source_match.group(1) if source_match else None, status


def _validate_raw_checksums(raw_dir: Path, errors: list[str]) -> None:
    manifest = raw_dir / "SHA256SUMS.txt"
    if not manifest.is_file():
        errors.append("Gate 2R.1 raw SHA256SUMS.txt is missing")
        return
    for line_number, raw_line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})\s{2}(.+)", line)
        if not match:
            errors.append(f"invalid raw checksum line {line_number}")
            continue
        expected, name = match.groups()
        candidate = raw_dir / name
        if not candidate.is_file():
            errors.append(f"raw evidence file is missing: {name}")
            continue
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"raw evidence checksum mismatch: {name}")


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

    approved_gate = control.get("approved_gate")
    authorised_gate = control.get("authorised_next_gate")
    if approved_gate not in GATE_ORDER:
        errors.append("control.approved_gate is invalid")
    if authorised_gate not in GATE_ORDER:
        errors.append("control.authorised_next_gate is invalid")
    if expected_approved_gate and approved_gate != expected_approved_gate:
        errors.append(f"approved_gate must be {expected_approved_gate}")
    if approved_gate in GATE_ORDER and authorised_gate in GATE_ORDER:
        if GATE_ORDER.index(authorised_gate) != GATE_ORDER.index(approved_gate) + 1:
            errors.append("authorised_next_gate must be exactly one gate after approved_gate")
    if expected_authorised_gate and authorised_gate != expected_authorised_gate:
        errors.append(f"authorised_next_gate must be {expected_authorised_gate}")

    if control.get("start_approved") is True:
        for field in ("approval_commit_sha", "parent_evidence_commit_sha", "remote_branch_sha"):
            if not SHA_RE.fullmatch(str(control.get(field, ""))):
                errors.append(f"control.{field} must be a real 40-character lowercase Git SHA")
        _parse_time(control.get("approved_at"), "control.approved_at", errors)

    supported = (automation.get("supported_gates") or {}).get(str(authorised_gate), {})
    if authorised_gate and not all(supported.get(name) is True for name in ("preflight", "verify", "collect")):
        errors.append(f"automation for authorised gate {authorised_gate} is incomplete")
    if authorised_gate != "2R.0" and supported.get("apply") is not True:
        errors.append(f"automation for authorised gate {authorised_gate} lacks apply support")

    try:
        plan = PLAN_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("Phase 2R execution plan is missing")
        plan = ""

    if authorised_gate == "2R.1":
        required_phrases = (
            "**Status:** Gate 2R.1 in progress; Gate 2R.2 blocked",
            "**Execution authorisation:** Gate 2R.1 only",
            "**Current decision:** Gate 2R.1 is In Progress. Gate 2R.2 is Blocked.",
        )
        for phrase in required_phrases:
            if phrase not in plan:
                errors.append(f"execution plan is missing current-state statement: {phrase}")
    elif approved_gate == "2R.1" and authorised_gate == "2R.2":
        required_phrases = (
            "**Status:** Gate 2R.1 verified complete; Gate 2R.2 authorised",
            "**Execution authorisation:** Gate 2R.2 only",
            "**Current decision:** Gate 2R.1 is Verified Complete. Gate 2R.2 is Authorised.",
        )
        for phrase in required_phrases:
            if phrase not in plan:
                errors.append(f"execution plan is missing post-transition statement: {phrase}")

    if require_approval_roles and approved_gate != "2R.1":
        errors.append("--require-approval-roles requires approved_gate to be 2R.1")
    if require_evidence_index_sha and approved_gate != "2R.1":
        errors.append("--require-evidence-index-sha requires approved_gate to be 2R.1")

    if approved_gate == "2R.1":
        for work_item in ("P02R-0101", "P02R-0102", "P02R-0103", "P02R-0104"):
            line = next((line for line in plan.splitlines() if line.startswith(f"| {work_item} |")), "")
            if not line or "Not started" in line or "In progress" in line or "verification pending" in line.lower():
                errors.append(f"{work_item} is not recorded as complete")

        evidence_generated, evidence_source_sha, _evidence_status = _evidence_index_metadata(EVIDENCE_2R1_INDEX, errors)
        _validate_raw_checksums(EVIDENCE_2R1_RAW, errors)
        approvals = _load(APPROVALS_2R1_PATH)
        if approvals.get("decision") != "approved" or approvals.get("authorised_next_gate") != "2R.2":
            errors.append("Gate 2R.1 approvals do not authorise Gate 2R.2")
        if approvals.get("evidence_source_sha") != evidence_source_sha:
            errors.append("Gate 2R.1 approvals do not reference the evidence source commit")
        evidence_commit_sha = str(approvals.get("evidence_commit_sha") or "")
        if not SHA_RE.fullmatch(evidence_commit_sha):
            errors.append("Gate 2R.1 approvals require a real evidence_commit_sha")
        if control.get("parent_evidence_commit_sha") != evidence_commit_sha:
            errors.append("gate control parent_evidence_commit_sha must equal the approved evidence commit")
        if control.get("approval_commit_sha") == control.get("parent_evidence_commit_sha"):
            errors.append("approval commit must be separate from the evidence commit")
        if control.get("remote_branch_sha") != control.get("approval_commit_sha"):
            errors.append("remote_branch_sha must equal the immutable gate approval commit")

        required_roles = {
            "engineering_approver",
            "rights_reviewer",
            "curriculum_reviewer",
            "evidence_custodian",
            "release_manager",
        }
        approved_roles: set[str] = set()
        decision_times: list[datetime] = []
        for item in approvals.get("decisions", []):
            decided_at = _parse_time(item.get("decided_at"), f"approval {item.get('role')} decided_at", errors) if item.get("decision") == "approved" else None
            if (
                item.get("decision") == "approved"
                and item.get("reviewer")
                and decided_at is not None
                and item.get("immutable_reference")
            ):
                approved_roles.add(str(item.get("role")))
                decision_times.append(decided_at)
                if evidence_generated and decided_at < evidence_generated:
                    errors.append(f"approval {item.get('role')} predates candidate evidence")
        missing_roles = required_roles - approved_roles
        if missing_roles:
            errors.append(f"Gate 2R.1 approvals missing roles: {', '.join(sorted(missing_roles))}")

        if EVIDENCE_2R1_INDEX.exists():
            expected = approvals.get("evidence_index_sha256")
            actual = hashlib.sha256(EVIDENCE_2R1_INDEX.read_bytes()).hexdigest()
            if expected != actual:
                errors.append("Gate 2R.1 approval evidence_index_sha256 does not match")

        control_time = _parse_time(control.get("approved_at"), "control.approved_at", errors)
        overall_decision_time = _parse_time(approvals.get("decided_at"), "Gate 2R.1 approvals decided_at", errors)
        if evidence_generated and overall_decision_time and overall_decision_time < evidence_generated:
            errors.append("Gate 2R.1 overall decision predates candidate evidence")
        if control_time and decision_times and control_time < max(decision_times):
            errors.append("gate transition approval predates one or more required reviewer decisions")

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
