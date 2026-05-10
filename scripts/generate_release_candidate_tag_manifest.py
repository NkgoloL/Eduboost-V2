#!/usr/bin/env python3
"""Generate release candidate tag manifest."""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "release_candidate_tag_manifest.md"


def _git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def render_manifest() -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    short_commit = _git_value(["rev-parse", "--short", "HEAD"])
    release_candidate = os.environ.get("RELEASE_CANDIDATE", f"beta-{short_commit}")

    return f"""# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `{generated_at}`
- branch: `{branch}`
- commit: `{commit}`
- release_candidate: `{release_candidate}`

## Tagging Convention

- beta release candidate tag format: `beta-<short-sha>` or explicit `RELEASE_CANDIDATE`
- release tags must point to reviewed commits
- release tags must be paired with beta release evidence bundle
- release tags must be paired with beta sign-off manifest
- release tags must be paired with rollback owner assignment

## Required Evidence Before Tagging

- `docs/operations/beta_release_evidence_bundle.md`
- `docs/operations/beta_signoff_manifest.md`
- `docs/operations/staging_smoke_evidence_manifest.md`
- `docs/operations/beta_rollback_runbook.md`
- `docs/operations/post_deploy_staging_smoke_checklist.md`

## Example Commands

```bash
git tag -a {release_candidate} -m "Beta release candidate {release_candidate}"
git push origin {release_candidate}
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
"""


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_manifest(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
