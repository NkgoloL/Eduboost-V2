#!/usr/bin/env python3
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/staging-smoke.yml"
PROBE = ROOT / "scripts/staging_smoke_probe.py"
STATUS_JSON = ROOT / "docs/release/staging_smoke_workflow_status.json"
STATUS_MD = ROOT / "docs/release/staging_smoke_workflow_status.md"


@dataclass(frozen=True)
class WorkflowConfigStatus:
    generated_at: str
    current_commit: str
    status: str
    workflow_exists: bool
    probe_exists: bool
    has_workflow_dispatch: bool
    has_staging_base_url_secret: bool
    has_probe_step: bool
    has_artifact_upload: bool
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


def build_status() -> WorkflowConfigStatus:
    workflow_text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""
    blockers: list[str] = []

    workflow_exists = WORKFLOW.exists()
    probe_exists = PROBE.exists()
    has_workflow_dispatch = "workflow_dispatch:" in workflow_text
    has_staging_base_url_secret = "secrets.STAGING_SMOKE_BASE_URL" in workflow_text
    has_probe_step = "python scripts/staging_smoke_probe.py" in workflow_text
    has_artifact_upload = "actions/upload-artifact@v4" in workflow_text

    checks = {
        "workflow file missing": workflow_exists,
        "probe script missing": probe_exists,
        "workflow_dispatch missing": has_workflow_dispatch,
        "STAGING_SMOKE_BASE_URL secret reference missing": has_staging_base_url_secret,
        "staging smoke probe step missing": has_probe_step,
        "artifact upload missing": has_artifact_upload,
    }

    for blocker, passed in checks.items():
        if not passed:
            blockers.append(blocker)

    if probe_exists:
        ast.parse(PROBE.read_text(encoding="utf-8"))

    return WorkflowConfigStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="staging-smoke-workflow-configured" if not blockers else "staging-smoke-workflow-not-configured",
        workflow_exists=workflow_exists,
        probe_exists=probe_exists,
        has_workflow_dispatch=has_workflow_dispatch,
        has_staging_base_url_secret=has_staging_base_url_secret,
        has_probe_step=has_probe_step,
        has_artifact_upload=has_artifact_upload,
        blockers=blockers,
    )


def write_status() -> WorkflowConfigStatus:
    status = build_status()
    STATUS_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Staging Smoke Workflow Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Check | Passed |",
        "|---|---:|",
        f"| Workflow exists | {status.workflow_exists} |",
        f"| Probe exists | {status.probe_exists} |",
        f"| workflow_dispatch | {status.has_workflow_dispatch} |",
        f"| STAGING_SMOKE_BASE_URL secret reference | {status.has_staging_base_url_secret} |",
        f"| Probe step | {status.has_probe_step} |",
        f"| Artifact upload | {status.has_artifact_upload} |",
        "",
        "## Blockers",
        "",
    ]
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- This proves only workflow configuration.",
            "- STAGING-001 remains external-blocked until a real successful staging smoke run is attached.",
            "- Placeholder staging URLs and placeholder run IDs are not accepted evidence.",
            "",
        ]
    )

    STATUS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return status


def main() -> int:
    status = write_status()
    print("Staging smoke workflow configuration check")
    print(f"- INFO status: {status.status}")
    if status.blockers:
        print("Failures:")
        for blocker in status.blockers:
            print(f"- {blocker}")
        return 1
    print("- PASS staging smoke workflow configuration check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
