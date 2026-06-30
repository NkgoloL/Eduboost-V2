from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL_DIR = ROOT / "docs/release/external_approvals"
OUT_JSON = ROOT / "docs/release/external_approval_status.json"
OUT_MD = ROOT / "docs/release/external_approval_status.md"
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

REQUIRED_APPROVALS = {
    "LEGAL-001": {
        "title": "POPIA/legal release approval",
        "file": "legal_approval.md",
        "owner": "legal",
        "required_decision": "approved",
    },
    "SEC-001": {
        "title": "Security release approval",
        "file": "security_approval.md",
        "owner": "security",
        "required_decision": "approved",
    },
    "CONTENT-001": {
        "title": "Educator/content release approval",
        "file": "content_approval.md",
        "owner": "content",
        "required_decision": "approved",
    },
    "STAGING-001": {
        "title": "Staging acceptance approval",
        "file": "staging_acceptance.md",
        "owner": "release",
        "required_decision": "approved",
    },
}

PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "not set", "unknown"}


@dataclass(frozen=True)
class ApprovalRecord:
    id: str
    title: str
    file: str
    owner: str
    exists: bool
    decision: str
    approver: str
    evidence_url: str
    date_verified: str
    approved: bool
    blockers: list[str]


@dataclass(frozen=True)
class ExternalApprovalStatus:
    generated_at: str
    current_commit: str
    status: str
    approvals: list[ApprovalRecord]
    remaining_blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def _template(approval_id: str, meta: dict[str, str]) -> str:
    return "\n".join(
        [
            f"# {meta['title']}",
            "",
            f"**Item:** {approval_id}",
            "",
            "**Decision:** pending",
            "",
            "**Approver:** pending",
            "",
            "**Evidence URL:** pending",
            "",
            "**Date verified:** pending",
            "",
            "## Required sign-off basis",
            "",
            "- The approver has reviewed the release evidence relevant to this approval domain.",
            "- Any release-blocking conditions are either resolved or explicitly waived in writing.",
            "- This file has been updated by the accountable approval owner.",
            "",
            "## No false-closure rule",
            "",
            "This approval is not complete while any metadata field remains pending.",
            "",
        ]
    )


def write_templates() -> None:
    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    for approval_id, meta in REQUIRED_APPROVALS.items():
        path = APPROVAL_DIR / meta["file"]
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if f"**Item:** {approval_id}" in text:
                continue
        path.write_text(_template(approval_id, meta), encoding="utf-8")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip().strip("`").strip()


def _is_pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _is_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def read_approval(approval_id: str, meta: dict[str, str]) -> ApprovalRecord:
    path = APPROVAL_DIR / meta["file"]
    if not path.exists():
        return ApprovalRecord(
            id=approval_id,
            title=meta["title"],
            file=f"docs/release/external_approvals/{meta['file']}",
            owner=meta["owner"],
            exists=False,
            decision="",
            approver="",
            evidence_url="",
            date_verified="",
            approved=False,
            blockers=["approval evidence file missing"],
        )

    text = path.read_text(encoding="utf-8")
    decision = _field(text, "Decision")
    approver = _field(text, "Approver")
    evidence_url = _field(text, "Evidence URL")
    date_verified = _field(text, "Date verified")

    blockers: list[str] = []
    if decision.lower() != meta["required_decision"]:
        blockers.append(f"decision must be {meta['required_decision']}")
    if _is_pending(approver):
        blockers.append("approver is pending")
    if _is_pending(evidence_url) or not _is_url(evidence_url):
        blockers.append("evidence URL is pending or invalid")
    if _is_pending(date_verified):
        blockers.append("date verified is pending")

    return ApprovalRecord(
        id=approval_id,
        title=meta["title"],
        file=f"docs/release/external_approvals/{meta['file']}",
        owner=meta["owner"],
        exists=True,
        decision=decision,
        approver=approver,
        evidence_url=evidence_url,
        date_verified=date_verified,
        approved=not blockers,
        blockers=blockers,
    )


def build_status() -> ExternalApprovalStatus:
    write_templates()
    approvals = [read_approval(approval_id, meta) for approval_id, meta in REQUIRED_APPROVALS.items()]
    blockers: list[str] = []
    for approval in approvals:
        blockers.extend(f"{approval.id}: {blocker}" for blocker in approval.blockers)

    return ExternalApprovalStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="external-approvals-complete" if not blockers else "external-blocked",
        approvals=approvals,
        remaining_blockers=blockers,
    )


def write_status() -> ExternalApprovalStatus:
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# External Approval Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| ID | Title | Owner | Decision | Approver | Evidence URL | Date verified | Approved |",
        "|---|---|---|---|---|---|---|---:|",
    ]
    for approval in status.approvals:
        lines.append(
            f"| `{approval.id}` | {approval.title} | `{approval.owner}` | `{approval.decision}` | "
            f"`{approval.approver}` | `{approval.evidence_url}` | `{approval.date_verified}` | {approval.approved} |"
        )

    lines.extend(["", "## Remaining blockers", ""])
    if status.remaining_blockers:
        lines.extend(f"- {blocker}" for blocker in status.remaining_blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rule",
            "",
            "External approvals remain `external-blocked` until every required approval file contains a non-pending decision, approver, evidence URL, and verification date.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def registry_statuses() -> dict[str, str]:
    if not REGISTRY.exists():
        return {}
    text = REGISTRY.read_text(encoding="utf-8")
    statuses: dict[str, str] = {}
    for approval_id in REQUIRED_APPROVALS:
        marker = f"id: {approval_id}"
        index = text.find(marker)
        if index < 0:
            continue
        next_index = text.find("\n  - id:", index + 1)
        block = text[index:] if next_index < 0 else text[index:next_index]
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith("proof_status:"):
                statuses[approval_id] = stripped.split(":", 1)[1].strip()
    return statuses


__all__ = [
    "REQUIRED_APPROVALS",
    "ApprovalRecord",
    "ExternalApprovalStatus",
    "build_status",
    "registry_statuses",
    "write_status",
    "write_templates",
]
