from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL_DIR = ROOT / "docs/release/external_approvals"
STATUS_JSON = ROOT / "docs/release/approval_evidence_status.json"
STATUS_MD = ROOT / "docs/release/approval_evidence_status.md"

APPROVALS = {
    "LEGAL-001": {
        "title": "POPIA/legal release approval",
        "file": "legal_approval.md",
        "owner": "legal",
    },
    "SEC-001": {
        "title": "Security release approval",
        "file": "security_approval.md",
        "owner": "security",
    },
    "CONTENT-001": {
        "title": "Educator/content release approval",
        "file": "content_approval.md",
        "owner": "content",
    },
}

PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}
APPROVED_VALUES = {"approved", "approve", "accepted", "pass", "passed", "green", "ok"}


@dataclass(frozen=True)
class ApprovalEvidence:
    id: str
    title: str
    owner: str
    decision: str
    approver: str
    evidence_url: str
    date_verified: str
    scope: str
    notes: str
    file: str


@dataclass(frozen=True)
class ApprovalEvidenceRecord:
    evidence: ApprovalEvidence
    status: str
    blockers: list[str]


@dataclass(frozen=True)
class ApprovalEvidenceStatus:
    generated_at: str
    current_commit: str
    status: str
    approvals: list[ApprovalEvidenceRecord]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _is_pending(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _is_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def _field(text: str, name: str) -> str:
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip().strip("`").strip()
    return ""


def approval_path(approval_id: str) -> Path:
    if approval_id not in APPROVALS:
        raise ValueError(f"Unknown approval id: {approval_id}")
    return APPROVAL_DIR / APPROVALS[approval_id]["file"]


def template_for(approval_id: str) -> str:
    meta = APPROVALS[approval_id]
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
            f"**Scope:** {meta['title']}",
            "",
            "**Notes:** pending",
            "",
            "## Required sign-off basis",
            "",
            "- The accountable owner reviewed release evidence for this approval domain.",
            "- Release-blocking conditions are resolved or explicitly waived in writing.",
            "- Evidence URL points to the approval record, report, ticket, or signed note.",
            "",
            "## No false-closure rule",
            "",
            "This approval is incomplete while decision, approver, evidence URL, or verification date is pending.",
            "",
        ]
    )


def write_templates() -> None:
    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    for approval_id in APPROVALS:
        path = approval_path(approval_id)
        if path.exists() and f"**Item:** {approval_id}" in path.read_text(encoding="utf-8"):
            continue
        path.write_text(template_for(approval_id), encoding="utf-8")


def read_evidence(approval_id: str) -> ApprovalEvidence:
    write_templates()
    meta = APPROVALS[approval_id]
    path = approval_path(approval_id)
    text = path.read_text(encoding="utf-8")
    return ApprovalEvidence(
        id=approval_id,
        title=meta["title"],
        owner=meta["owner"],
        decision=_field(text, "Decision"),
        approver=_field(text, "Approver"),
        evidence_url=_field(text, "Evidence URL"),
        date_verified=_field(text, "Date verified"),
        scope=_field(text, "Scope"),
        notes=_field(text, "Notes"),
        file=f"docs/release/external_approvals/{meta['file']}",
    )


def blockers_for(evidence: ApprovalEvidence) -> list[str]:
    blockers: list[str] = []

    if _is_pending(evidence.decision) or evidence.decision.strip().lower() not in APPROVED_VALUES:
        blockers.append("decision must be approved/accepted/pass")
    if _is_pending(evidence.approver):
        blockers.append("approver is pending")
    if _is_pending(evidence.evidence_url) or not _is_url(evidence.evidence_url):
        blockers.append("evidence URL is pending or invalid")
    if _is_pending(evidence.date_verified):
        blockers.append("date verified is pending")
    if _is_pending(evidence.scope):
        blockers.append("scope is pending")

    return blockers


def read_record(approval_id: str) -> ApprovalEvidenceRecord:
    evidence = read_evidence(approval_id)
    blockers = blockers_for(evidence)
    return ApprovalEvidenceRecord(
        evidence=evidence,
        status="approved" if not blockers else "external-blocked",
        blockers=blockers,
    )


def render_evidence(evidence: ApprovalEvidence, status: str) -> str:
    return "\n".join(
        [
            f"# {evidence.title}",
            "",
            f"**Item:** {evidence.id}",
            "",
            f"**Decision:** {evidence.decision}",
            "",
            f"**Approver:** {evidence.approver}",
            "",
            f"**Evidence URL:** {evidence.evidence_url}",
            "",
            f"**Date verified:** {evidence.date_verified}",
            "",
            f"**Scope:** {evidence.scope}",
            "",
            f"**Notes:** {evidence.notes or 'none'}",
            "",
            "## Approval status",
            "",
            f"`{status}`",
            "",
            "## No false-closure rule",
            "",
            "Approval is only complete when the generated approval evidence status reports this item as `approved`.",
            "",
        ]
    )


def attach_approval(
    *,
    approval_id: str,
    decision: str,
    approver: str,
    evidence_url: str,
    date_verified: str,
    scope: str,
    notes: str,
) -> ApprovalEvidenceRecord:
    if approval_id not in APPROVALS:
        raise ValueError(f"Unknown approval id: {approval_id}")
    meta = APPROVALS[approval_id]
    evidence = ApprovalEvidence(
        id=approval_id,
        title=meta["title"],
        owner=meta["owner"],
        decision=decision,
        approver=approver,
        evidence_url=evidence_url,
        date_verified=date_verified,
        scope=scope,
        notes=notes,
        file=f"docs/release/external_approvals/{meta['file']}",
    )
    blockers = blockers_for(evidence)
    status = "approved" if not blockers else "external-blocked"
    approval_path(approval_id).write_text(render_evidence(evidence, status), encoding="utf-8")
    return read_record(approval_id)


def build_status() -> ApprovalEvidenceStatus:
    records = [read_record(approval_id) for approval_id in APPROVALS]
    blockers: list[str] = []
    for record in records:
        blockers.extend(f"{record.evidence.id}: {blocker}" for blocker in record.blockers)

    return ApprovalEvidenceStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="approvals-complete" if not blockers else "external-blocked",
        approvals=records,
        blockers=blockers,
    )


def write_status() -> ApprovalEvidenceStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Approval Evidence Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| ID | Owner | Decision | Approver | Evidence URL | Date verified | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in status.approvals:
        evidence = record.evidence
        lines.append(
            f"| `{evidence.id}` | `{evidence.owner}` | `{evidence.decision}` | `{evidence.approver}` | "
            f"`{evidence.evidence_url}` | `{evidence.date_verified}` | `{record.status}` |"
        )

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This status validates recorded approval metadata. It does not perform the legal, security, or content review.",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--templates", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--attach", choices=sorted(APPROVALS))
    parser.add_argument("--decision", default="pending")
    parser.add_argument("--approver", default="pending")
    parser.add_argument("--evidence-url", default="pending")
    parser.add_argument("--date-verified", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--scope", default="pending")
    parser.add_argument("--notes", default="attached through APPROVAL-EVID-001 helper")
    args = parser.parse_args(argv)

    if args.templates:
        write_templates()
        print("approval templates ready")
        return 0

    if args.attach:
        record = attach_approval(
            approval_id=args.attach,
            decision=args.decision,
            approver=args.approver,
            evidence_url=args.evidence_url,
            date_verified=args.date_verified,
            scope=args.scope,
            notes=args.notes,
        )
        status = write_status()
        print(record.status)
        if record.status != "approved":
            for blocker in record.blockers:
                print(f"- {blocker}")
            return 1
        print(status.status)
        return 0

    status = write_status()
    print(status.status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
