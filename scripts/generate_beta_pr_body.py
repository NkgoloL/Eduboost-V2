#!/usr/bin/env python3
"""Generate beta release PR body template.

Generator identifier: generate_beta_pr_body.
"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "beta_release_pr_body.md"


def _git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def render_pr_body() -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    release_candidate = os.environ.get("RELEASE_CANDIDATE", "unset")

    return f"""# Beta Release PR Body

## Summary

This PR closes the EduBoost V2 staging/beta release evidence layer.

- release_candidate: `{release_candidate}`
- branch: `{branch}`
- commit: `{commit}`
- generated_at_utc: `{generated_at}`

## Verification

```bash
make final-release-verification
make cluster-h-release-readiness-check
make cluster-h-closure-check
```

## Release Boundary

This PR supports controlled staging/beta validation only. It does not authorize unrestricted production launch, production data migration, or release tag push without manual approval.

## Rollback

Rollback evidence:

- `docs/operations/beta_rollback_runbook.md`
- rollback owner: _pending_
- post-deploy verification owner: _pending_

## Evidence Index

- `docs/operations/project_release_closure_index.md`
- `docs/operations/beta_release_evidence_bundle.md`
- `docs/operations/CLUSTER_H_CLOSURE.md`
- `docs/operations/beta_release_final_checklist.md`
- `docs/operations/pr_closeout_evidence_checklist.md`

## Known Follow-Ups

- normalize frontend package scripts
- move mocked browser checks into automatic CI when runtime server command is canonical
- complete manual sign-off fields before release tag creation
- attach or link platform workflow logs for approval and post-deploy smoke runs
"""


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_pr_body(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
