#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs/release/ci_evidence.md"
JSON_OUT = ROOT / "docs/release/ci_evidence.json"


def _looks_like_url(value: str) -> bool:
    return bool(re.match(r"^https://github\.com/.+/actions/runs/\d+", value.strip()))


def main() -> int:
    run_url = os.getenv("GITHUB_ACTIONS_RUN_URL", "").strip()
    commit_sha = os.getenv("CI_COMMIT_SHA", "").strip()
    branch = os.getenv("CI_BRANCH", os.getenv("GITHUB_REF_NAME", "")).strip()
    result = os.getenv("CI_RESULT", "").strip().lower()
    test_summary = os.getenv("CI_TEST_SUMMARY", "").strip()

    green = _looks_like_url(run_url) and result in {"success", "passed", "green"}
    status_label = "green" if green else "pending_remote_ci_evidence"
    status_md = "green" if green else "pending remote CI verification"
    payload = {
        "status": status_label,
        "run_url": run_url,
        "commit_sha": commit_sha,
        "branch": branch,
        "result": result,
        "test_summary": test_summary,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required": True,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    MD.write_text("\n".join([
        "# CI Evidence", "", f"Status: {status_md}", "", f"**Status:** {status_md}", "",
        "| Field | Value |", "|---|---|",
        f"| GitHub Actions run URL | {run_url or 'PENDING'} |",
        f"| Commit SHA | {commit_sha or 'PENDING'} |",
        f"| Branch | {branch or 'PENDING'} |",
        f"| Result | {result or 'PENDING'} |",
        f"| Test summary | {test_summary or 'PENDING'} |",
        f"| Captured at | {payload['captured_at']} |", "",
        "## Usage", "", "```bash",
        "GITHUB_ACTIONS_RUN_URL=https://github.com/<owner>/<repo>/actions/runs/<id> \\",
        "CI_RESULT=success \\",
        "CI_COMMIT_SHA=<sha> \\",
        "CI_BRANCH=codex/production_readiness \\",
        "make remote-ci-evidence-capture", "```", "",
        "## Checklists",
        "- Route alias policy: pending verification", "",
    ]), encoding="utf-8")
    print(f"Wrote {MD.relative_to(ROOT)}")
    print(f"Wrote {JSON_OUT.relative_to(ROOT)}")
    return 0 if green else 2


if __name__ == "__main__":
    raise SystemExit(main())
