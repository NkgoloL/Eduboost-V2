#!/usr/bin/env python3
"""Generate a database backup evidence manifest."""
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "operations" / "database_backup_manifest.md"


@dataclass(frozen=True)
class BackupManifestInput:
    backup_artifact_id: str
    target_environment: str
    retention_days: int
    encrypted: bool


def _git_value(args: list[str], fallback: str = "unknown") -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    return result.stdout.strip() or fallback


def stable_manifest_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def render_manifest(data: BackupManifestInput) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    manifest_id = stable_manifest_id(f"{data.backup_artifact_id}:{data.target_environment}:{commit}")
    encrypted_status = "yes" if data.encrypted else "no"
    return f"""# Database Backup Manifest

Manifest ID: `{manifest_id}`
Generated: `{stamp}`
Branch: `{branch}`
Commit: `{commit}`

## Backup Metadata

| Field | Value |
| --- | --- |
| Backup artifact ID | `{data.backup_artifact_id}` |
| Target environment | `{data.target_environment}` |
| Retention days | `{data.retention_days}` |
| Encrypted | `{encrypted_status}` |

## Required Verification

- backup artifact is encrypted
- backup artifact ID is recorded
- retention period is recorded
- restore drill evidence is linked before production promotion

## Related Commands

```bash
make database-backup-dry-run
make database-backup-contract-check
make database-restore-drill-docs-check
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate database backup evidence manifest.")
    parser.add_argument("--backup-artifact-id", default="pending-backup-artifact")
    parser.add_argument("--target-environment", default="staging")
    parser.add_argument("--retention-days", type=int, default=30)
    parser.add_argument("--encrypted", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_manifest(
            BackupManifestInput(
                backup_artifact_id=args.backup_artifact_id,
                target_environment=args.target_environment,
                retention_days=args.retention_days,
                encrypted=args.encrypted,
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
