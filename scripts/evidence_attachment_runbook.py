from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs/release/evidence_attachment_runbook.md"
OUT_JSON = ROOT / "docs/release/evidence_attachment_runbook_manifest.json"

@dataclass(frozen=True)
class EvidenceCommand:
    id: str
    category: str
    purpose: str
    command: str
    expected_until_evidence: str

@dataclass(frozen=True)
class EvidenceAttachmentRunbookManifest:
    generated_at: str
    current_commit: str
    runbook_file: str
    command_count: int
    commands: list[EvidenceCommand]
    release_mode_sequence: list[str]
    no_false_closure_rules: list[str]

def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"

COMMANDS: list[EvidenceCommand] = [
    EvidenceCommand("CI-001", "ci", "Attach authoritative GitHub Actions run metadata.", 'CI_RUN_URL="https://github.com/NkgoloL/Eduboost-V2/actions/runs/<run_id>" CI_RESULT="passed" CI_WORKFLOW="release" CI_VERIFIED_BY="<name>" make ci-run-evidence-attach', "make ci-run-evidence-release-check fails until accepted CI metadata is recorded"),
    EvidenceCommand("LEGAL-001", "approval", "Attach POPIA/legal approval metadata.", 'APPROVAL_ID="LEGAL-001" APPROVAL_DECISION="approved" APPROVAL_APPROVER="<legal-owner>" APPROVAL_EVIDENCE_URL="https://<approval-record>" APPROVAL_SCOPE="beta release POPIA/legal review" make approval-evidence-attach', "make approval-evidence-release-check fails until all legal/security/content approvals are complete"),
    EvidenceCommand("SEC-001", "approval", "Attach security approval metadata.", 'APPROVAL_ID="SEC-001" APPROVAL_DECISION="approved" APPROVAL_APPROVER="<security-owner>" APPROVAL_EVIDENCE_URL="https://<security-report>" APPROVAL_SCOPE="beta release security review" make approval-evidence-attach', "make approval-evidence-release-check fails until all legal/security/content approvals are complete"),
    EvidenceCommand("CONTENT-001", "approval", "Attach educator/content approval metadata.", 'APPROVAL_ID="CONTENT-001" APPROVAL_DECISION="approved" APPROVAL_APPROVER="<content-owner>" APPROVAL_EVIDENCE_URL="https://<content-signoff>" APPROVAL_SCOPE="beta release content review" make approval-evidence-attach', "make approval-evidence-release-check fails until all legal/security/content approvals are complete"),
    EvidenceCommand("STAGING-001", "staging", "Attach staging smoke evidence by editing docs/release/staging_smoke_evidence.md and rerunning checks.", "make staging-acceptance-status && make staging-acceptance-local-check", "make staging-acceptance-release-check fails until staging evidence fields contain real accepted metadata"),
    EvidenceCommand("ROUTE-TX-AUTH-001", "live-db", "Attach auth route live DB rollback evidence.", 'TX_SLICE="auth" TX_EVIDENCE_URL="https://<auth-live-db-proof>" TX_TEST_RESULT="passed" TX_DATABASE="postgresql-staging" TX_VERIFIED_BY="<name>" make live-db-tx-evidence-attach', "make live-db-tx-evidence-release-check fails until all route transaction slices have accepted live DB evidence"),
    EvidenceCommand("ROUTE-TX-POPIA-001", "live-db", "Attach POPIA route live DB rollback evidence.", 'TX_SLICE="popia" TX_EVIDENCE_URL="https://<popia-live-db-proof>" TX_TEST_RESULT="passed" TX_DATABASE="postgresql-staging" TX_VERIFIED_BY="<name>" make live-db-tx-evidence-attach', "make live-db-tx-evidence-release-check fails until all route transaction slices have accepted live DB evidence"),
    EvidenceCommand("ROUTE-TX-DIAG-001", "live-db", "Attach diagnostics route live DB rollback evidence.", 'TX_SLICE="diagnostics" TX_EVIDENCE_URL="https://<diagnostics-live-db-proof>" TX_TEST_RESULT="passed" TX_DATABASE="postgresql-staging" TX_VERIFIED_BY="<name>" make live-db-tx-evidence-attach', "make live-db-tx-evidence-release-check fails until all route transaction slices have accepted live DB evidence"),
]

RELEASE_MODE_SEQUENCE = [
    "make ci-run-evidence-release-check",
    "make approval-evidence-release-check",
    "make external-approval-release-check",
    "make staging-acceptance-release-check",
    "make live-db-tx-evidence-release-check",
    "make route-tx-slice-rollup-release-check",
    "make beta-blocker-burndown-release-check",
    "make release-go-no-go-release-check",
    "make final-gate-refresh-release-check",
]

NO_FALSE_CLOSURE_RULES = [
    "Do not replace real GitHub Actions evidence with local pytest or Make output.",
    "Do not replace legal, security, or content sign-off with generated templates.",
    "Do not replace staging acceptance with local smoke checks.",
    "Do not replace live DB rollback proof with route-source scans.",
    "Do not change the beta decision to GO without release-owner sign-off after all release-mode checks pass.",
]

def build_manifest() -> EvidenceAttachmentRunbookManifest:
    return EvidenceAttachmentRunbookManifest(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        runbook_file="docs/release/evidence_attachment_runbook.md",
        command_count=len(COMMANDS),
        commands=COMMANDS,
        release_mode_sequence=RELEASE_MODE_SEQUENCE,
        no_false_closure_rules=NO_FALSE_CLOSURE_RULES,
    )

def render_runbook(manifest: EvidenceAttachmentRunbookManifest) -> str:
    lines = [
        "# Evidence Attachment Runbook", "", f"Generated at: `{manifest.generated_at}`", f"Commit: `{manifest.current_commit}`", "",
        "## Purpose", "", "This runbook tells an operator how to attach real release evidence for CI, external approvals, staging, and live database transaction proof.", "", "It is not evidence by itself.", "",
        "## Evidence attachment commands", "", "| ID | Category | Purpose | Command | Expected until evidence is attached |", "|---|---|---|---|---|",
    ]
    for command in manifest.commands:
        lines.append(f"| `{command.id}` | `{command.category}` | {command.purpose} | `{command.command}` | {command.expected_until_evidence} |")
    lines.extend([
        "", "## Staging evidence fields", "",
        "For `STAGING-001`, update `docs/release/staging_smoke_evidence.md` with real values for:", "",
        "- `Environment`", "- `Staging URL`", "- `Commit SHA`", "- `GitHub Actions run URL`", "- `Smoke command`", "- `Smoke result`", "- `Health endpoint result`", "- `API smoke result`", "- `Database migration status`", "- `Verified by`", "- `Date verified`", "",
        "Then run:", "", "```bash", "make staging-acceptance-status", "make staging-acceptance-local-check", "make staging-acceptance-release-check", "```", "",
        "## Refresh sequence after attaching evidence", "", "```bash", "make ci-run-evidence-status", "make approval-evidence-status", "make external-approval-status", "make staging-acceptance-status", "make live-db-tx-evidence-status", "make route-tx-slice-rollup", "make release-go-no-go-status", "make beta-blocker-burndown-plan", "make final-gate-refresh", "```", "",
        "## Release-mode sequence", "", "Run these only after real evidence is attached:", "", "```bash",
    ])
    lines.extend(manifest.release_mode_sequence)
    lines.extend(["```", "", "## No false-closure rules", ""])
    lines.extend(f"- {rule}" for rule in manifest.no_false_closure_rules)
    lines.extend(["", "## Expected current state", "", "Until real CI, staging, approval, and live DB evidence is attached, the correct release posture is `NO-GO`.", ""])
    return "\n".join(lines)

def write_runbook() -> EvidenceAttachmentRunbookManifest:
    manifest = build_manifest()
    OUT_JSON.write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")
    OUT_MD.write_text(render_runbook(manifest), encoding="utf-8")
    return manifest

__all__ = ["COMMANDS", "NO_FALSE_CLOSURE_RULES", "RELEASE_MODE_SEQUENCE", "EvidenceAttachmentRunbookManifest", "EvidenceCommand", "build_manifest", "write_runbook"]
