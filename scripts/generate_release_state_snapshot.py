#!/usr/bin/env python3
"""Generate release state snapshot for Cluster H.

Generator identifier: generate_release_state_snapshot.
"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "release_state_snapshot.md"

STATE_ARTIFACTS = (
    "docs/operations/beta_release_readiness_contract.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/beta_release_final_checklist.md",
    "docs/operations/beta_release_execution_plan.md",
    "docs/operations/beta_release_pr_body.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/project_release_closure_index.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "audits/reports/PR_INTEGRATION_SUMMARY.md",
    "docs/project_status.md",
)


def _git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def render_snapshot() -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    status = _git_value(["status", "--short"])
    release_candidate = os.environ.get("RELEASE_CANDIDATE", "unset")

    lines = [
        "# Release State Snapshot",
        "",
        "## Metadata",
        "",
        f"- generated_at_utc: `{generated_at}`",
        f"- branch: `{branch}`",
        f"- commit: `{commit}`",
        f"- release_candidate: `{release_candidate}`",
        "",
        "## Working Tree Status",
        "",
        "```text",
        status or "clean",
        "```",
        "",
        "## State Artifacts",
        "",
        "| Artifact | Present |",
        "| --- | --- |",
    ]

    for rel_path in STATE_ARTIFACTS:
        present = "yes" if (REPO_ROOT / rel_path).exists() else "no"
        lines.append(f"| `{rel_path}` | `{present}` |")

    lines.extend(
        [
            "",
            "## Snapshot Boundary",
            "",
            "This release state snapshot records local repository state at generation time.",
            "It does not replace CI logs, platform approvals, or release tag history.",
            "",
            "## Command",
            "",
            "```bash",
            "make release-state-snapshot",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_snapshot(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
