#!/usr/bin/env python3
"""Generate a database restore evidence record."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "operations" / "database_restore_evidence.md"


@dataclass(frozen=True)
class RestoreEvidenceInput:
    backup_artifact_id: str
    target_environment: str
    integrity_status: str
    learner_count_status: str
    consent_count_status: str
    audit_count_status: str


def _git_value(args: list[str], fallback: str = "unknown") -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    return result.stdout.strip() or fallback


def render_evidence(data: RestoreEvidenceInput) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    return f"""# Database Restore Evidence

Generated: `{stamp}`
Branch: `{branch}`
Commit: `{commit}`

## Restore Metadata

| Field | Value |
| --- | --- |
| Backup artifact ID | `{data.backup_artifact_id}` |
| Target environment | `{data.target_environment}` |
| Integrity status | `{data.integrity_status}` |
| Learner count status | `{data.learner_count_status}` |
| Consent count status | `{data.consent_count_status}` |
| Audit count status | `{data.audit_count_status}` |

## Required Verification Commands

```bash
make database-restore-dry-run
make runtime-check
make route-inventory-check
make popia-consent-closure-check
make cluster-d-closure-check
```

## Release Use

Production promotion is blocked until restore evidence records learner,
consent, and audit integrity status.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate database restore evidence.")
    parser.add_argument("--backup-artifact-id", default="pending-backup-artifact")
    parser.add_argument("--target-environment", default="staging")
    parser.add_argument("--integrity-status", default="pending")
    parser.add_argument("--learner-count-status", default="pending")
    parser.add_argument("--consent-count-status", default="pending")
    parser.add_argument("--audit-count-status", default="pending")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_evidence(
            RestoreEvidenceInput(
                backup_artifact_id=args.backup_artifact_id,
                target_environment=args.target_environment,
                integrity_status=args.integrity_status,
                learner_count_status=args.learner_count_status,
                consent_count_status=args.consent_count_status,
                audit_count_status=args.audit_count_status,
            )
        ),
        encoding="utf-8",
    )
    try:
        display = output.relative_to(REPO_ROOT)
    except ValueError:
        display = output
    print(f"Wrote {display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
