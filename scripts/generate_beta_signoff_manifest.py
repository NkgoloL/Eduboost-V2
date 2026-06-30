#!/usr/bin/env python3
"""Generate beta release sign-off manifest."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "beta_signoff_manifest.md"

SIGNOFF_AREAS = (
    ("technical lead sign-off", "backend runtime, API, frontend journey, and release gates reviewed"),
    ("privacy/POPIA sign-off", "consent, audit, data-rights, and learner privacy boundaries reviewed"),
    ("data resilience sign-off", "backup, restore, integrity, and production restore approval boundaries reviewed"),
    ("AI safety sign-off", "CAPS alignment, prompt safety, output schemas, refusals, and leakage guards reviewed"),
    ("frontend journey sign-off", "learner, parent, denial, accessibility, and Playwright evidence reviewed"),
    ("rollback owner sign-off", "rollback procedure, owner, trigger, and communication path reviewed"),
)

REQUIRED_INPUTS = (
    "docs/operations/beta_release_readiness_contract.md",
    "docs/operations/staging_smoke_evidence_manifest.md",
    "docs/frontend/CLUSTER_G_CLOSURE.md",
    "docs/ai/CLUSTER_F_CLOSURE.md",
    "docs/operations/CLUSTER_E_CLOSURE.md",
)


@dataclass(frozen=True)
class SignoffArea:
    name: str
    evidence: str


def _git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def render_manifest(areas: tuple[SignoffArea, ...]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    release_candidate = os.environ.get("RELEASE_CANDIDATE", "unset")

    lines = [
        "# Beta Sign-Off Manifest",
        "",
        "## Metadata",
        "",
        f"- generated_at_utc: `{generated_at}`",
        f"- branch: `{branch}`",
        f"- commit: `{commit}`",
        f"- release_candidate: `{release_candidate}`",
        "",
        "## Required Sign-Off Areas",
        "",
        "| Area | Evidence expectation | Sign-off owner | Status |",
        "| --- | --- | --- | --- |",
    ]

    for area in areas:
        lines.append(f"| {area.name} | {area.evidence} | _pending_ | _pending_ |")

    lines.extend(
        [
            "",
            "## Required Input Evidence",
            "",
        ]
    )
    for rel_path in REQUIRED_INPUTS:
        lines.append(f"- `{rel_path}`")

    lines.extend(
        [
            "",
            "## Release Boundary",
            "",
            "Beta sign-off is valid only for the referenced commit and release candidate.",
            "Any material code, infrastructure, database, consent, AI safety, or frontend",
            "journey change requires a refreshed sign-off manifest.",
            "",
            "## Command",
            "",
            "```bash",
            "make beta-signoff-manifest",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    areas = tuple(SignoffArea(name, evidence) for name, evidence in SIGNOFF_AREAS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_manifest(areas), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(areas)} sign-off area(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
