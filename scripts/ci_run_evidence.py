from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_EVIDENCE = ROOT / "docs/release/ci_evidence.md"
STATUS_JSON = ROOT / "docs/release/ci_run_evidence_status.json"
STATUS_MD = ROOT / "docs/release/ci_run_evidence_status.md"

RUN_URL_RE = re.compile(r"^https://github\.com/[^/\s]+/[^/\s]+/actions/runs/[0-9]+(?:[/?#][^\s]*)?$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
PASS_VALUES = {"pass", "passed", "success", "successful", "green", "ok"}
PENDING_VALUES = {"", "pending", "todo", "tbd", "null", "none", "n/a", "unknown", "not set"}


@dataclass(frozen=True)
class CIRunEvidence:
    repository: str
    branch: str
    commit_sha: str
    github_actions_run_url: str
    result: str
    workflow: str
    verified_by: str
    date_verified: str
    notes: str


@dataclass(frozen=True)
class CIRunEvidenceStatus:
    generated_at: str
    current_commit: str
    evidence_file: str
    status: str
    evidence: CIRunEvidence
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
    normalized = value.strip().strip("`").strip().lower()
    return normalized in PENDING_VALUES or normalized.startswith("pending")


def _field(text: str, name: str) -> str:
    match = re.search(rf"\*\*{re.escape(name)}:\*\*\s*(.+)", text, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip().strip("`").strip()


def validate_run_url(run_url: str) -> bool:
    return bool(RUN_URL_RE.match(run_url.strip()))


def validate_commit_sha(commit_sha: str) -> bool:
    return bool(SHA_RE.match(commit_sha.strip()))


def evidence_template() -> str:
    return """# CI Authority Evidence

**Item:** CI-001

Status: pending remote CI verification

**Status:** external-blocked

This file must be updated with an actual GitHub Actions run URL before CI-001 can move beyond `external-blocked`.

## Required evidence

**Repository:** NkgoloL/Eduboost-V2

**Branch:** codex/production_readiness

**Commit SHA:** pending

**GitHub Actions run URL:** pending

**Result:** pending

**Workflow:** pending

**Verified by:** pending

**Date verified:** pending

**Route alias policy:** pending

**Notes:** pending

## No false closure rule

Local command success is not remote CI authority. CI-001 remains `external-blocked` until an actual GitHub Actions run URL and passing result metadata are attached.
"""


def write_template() -> None:
    if not CI_EVIDENCE.exists() or "**Item:** CI-001" not in CI_EVIDENCE.read_text(encoding="utf-8"):
        CI_EVIDENCE.write_text(evidence_template(), encoding="utf-8")
        return

    text = CI_EVIDENCE.read_text(encoding="utf-8")
    defaults = {
        "Repository": "NkgoloL/Eduboost-V2",
        "Branch": "codex/production_readiness",
        "Commit SHA": "pending",
        "GitHub Actions run URL": "pending",
        "Result": "pending",
        "Workflow": "pending",
        "Verified by": "pending",
        "Date verified": "pending",
        "Notes": "pending",
    }
    missing = [name for name in defaults if f"**{name}:**" not in text]
    if missing:
        addition = ["", "## CI-RUN-001 metadata extension", ""]
        for name in missing:
            addition.extend([f"**{name}:** {defaults[name]}", ""])
        CI_EVIDENCE.write_text(text.rstrip() + "\n" + "\n".join(addition), encoding="utf-8")


def read_evidence_text(text: str) -> CIRunEvidence:
    return CIRunEvidence(
        repository=_field(text, "Repository"),
        branch=_field(text, "Branch"),
        commit_sha=_field(text, "Commit SHA"),
        github_actions_run_url=_field(text, "GitHub Actions run URL"),
        result=_field(text, "Result"),
        workflow=_field(text, "Workflow"),
        verified_by=_field(text, "Verified by"),
        date_verified=_field(text, "Date verified"),
        notes=_field(text, "Notes"),
    )


def read_evidence() -> CIRunEvidence:
    write_template()
    return read_evidence_text(CI_EVIDENCE.read_text(encoding="utf-8"))


def blockers_for(evidence: CIRunEvidence) -> list[str]:
    blockers: list[str] = []
    if _is_pending(evidence.repository):
        blockers.append("repository is pending")
    if _is_pending(evidence.branch):
        blockers.append("branch is pending")
    if _is_pending(evidence.commit_sha) or not validate_commit_sha(evidence.commit_sha):
        blockers.append("commit SHA is pending or invalid")
    if _is_pending(evidence.github_actions_run_url) or not validate_run_url(evidence.github_actions_run_url):
        blockers.append("GitHub Actions run URL is pending or invalid")
    if _is_pending(evidence.result) or evidence.result.strip().lower() not in PASS_VALUES:
        blockers.append("result must be pass/passed/success/successful/green/ok")
    if _is_pending(evidence.workflow):
        blockers.append("workflow is pending")
    if _is_pending(evidence.verified_by):
        blockers.append("verified by is pending")
    if _is_pending(evidence.date_verified):
        blockers.append("date verified is pending")
    return blockers


def build_status() -> CIRunEvidenceStatus:
    evidence = read_evidence()
    blockers = blockers_for(evidence)
    return CIRunEvidenceStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        evidence_file="docs/release/ci_evidence.md",
        status="ci-evidence-accepted" if not blockers else "external-blocked",
        evidence=evidence,
        blockers=blockers,
    )


def render_evidence(evidence: CIRunEvidence, status: str) -> str:
    return f"""# CI Authority Evidence

**Item:** CI-001

Status: {'accepted' if status == 'ci-evidence-accepted' else 'pending remote CI verification'}

**Status:** {'accepted' if status == 'ci-evidence-accepted' else 'external-blocked'}

## Required evidence

**Repository:** {evidence.repository}

**Branch:** {evidence.branch}

**Commit SHA:** {evidence.commit_sha}

**GitHub Actions run URL:** {evidence.github_actions_run_url}

**Result:** {evidence.result}

**Workflow:** {evidence.workflow}

**Verified by:** {evidence.verified_by}

**Date verified:** {evidence.date_verified}

**Route alias policy:** pending

**Notes:** {evidence.notes or 'none'}

## No false closure rule

CI-001 can only move beyond `external-blocked` when this file records a valid GitHub Actions run URL and passing result metadata. This helper does not query GitHub.
"""


def write_status() -> CIRunEvidenceStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# CI Run Evidence Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Repository | `{status.evidence.repository}` |",
        f"| Branch | `{status.evidence.branch}` |",
        f"| Commit SHA | `{status.evidence.commit_sha}` |",
        f"| GitHub Actions run URL | `{status.evidence.github_actions_run_url}` |",
        f"| Result | `{status.evidence.result}` |",
        f"| Workflow | `{status.evidence.workflow}` |",
        f"| Verified by | `{status.evidence.verified_by}` |",
        f"| Date verified | `{status.evidence.date_verified}` |",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(f"- {b}" for b in status.blockers) if status.blockers else lines.append("- None")
    lines.extend(["", "## Interpretation", "", "This status validates recorded evidence metadata only. It does not query GitHub or independently prove the remote run result.", ""])
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")
    return status


def attach_evidence(
    *,
    run_url: str,
    result: str,
    commit_sha: str,
    repository: str,
    branch: str,
    workflow: str,
    verified_by: str,
    date_verified: str,
    notes: str,
) -> CIRunEvidenceStatus:
    evidence = CIRunEvidence(
        repository=repository,
        branch=branch,
        commit_sha=commit_sha,
        github_actions_run_url=run_url,
        result=result,
        workflow=workflow,
        verified_by=verified_by,
        date_verified=date_verified,
        notes=notes,
    )
    blockers = blockers_for(evidence)
    status = "ci-evidence-accepted" if not blockers else "external-blocked"
    CI_EVIDENCE.write_text(render_evidence(evidence, status), encoding="utf-8")
    return write_status()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--attach", action="store_true")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--result", default="pending")
    parser.add_argument("--commit-sha", default=current_commit())
    parser.add_argument("--repository", default="NkgoloL/Eduboost-V2")
    parser.add_argument("--branch", default="codex/production_readiness")
    parser.add_argument("--workflow", default="pending")
    parser.add_argument("--verified-by", default="pending")
    parser.add_argument("--date-verified", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--notes", default="attached through CI-RUN-001 helper")
    args = parser.parse_args()

    if args.attach:
        status = attach_evidence(
            run_url=args.run_url,
            result=args.result,
            commit_sha=args.commit_sha,
            repository=args.repository,
            branch=args.branch,
            workflow=args.workflow,
            verified_by=args.verified_by,
            date_verified=args.date_verified,
            notes=args.notes,
        )
        print(status.status)
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 0 if status.status == "ci-evidence-accepted" else 1

    if args.template:
        write_template()
        print("ci evidence template ready")
        return 0

    status = write_status()
    print(status.status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
