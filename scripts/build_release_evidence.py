#!/usr/bin/env python3
"""Create a local release-evidence manifest from available CI/build artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACTS = [
    "docs/openapi.json",
    "coverage.xml",
    "prometheus.yml",
    "prometheus/alerts.yml",
    "docker/Dockerfile.v2",
    "docker-compose.yml",
    "docker-compose.prod.yml",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *cmd], cwd=ROOT, text=True).strip()
    except Exception:  # noqa: BLE001 - evidence should still be generated from ZIP snapshots
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reports/release_evidence")
    parser.add_argument("--version", default=os.getenv("APP_VERSION", "snapshot"))
    args = parser.parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = []
    for relative in DEFAULT_ARTIFACTS:
        path = ROOT / relative
        if path.exists():
            artifacts.append({"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size})

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": args.version,
        "commit": git(["rev-parse", "HEAD"]),
        "branch": git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "migration_head": git(["grep", "-h", "^revision", "--", "alembic/versions/*.py"]),
        "artifacts": artifacts,
        "required_external_evidence": [
            "backend image digest",
            "frontend image digest",
            "SBOM files",
            "Trivy/Bandit/gitleaks reports",
            "staging smoke JSON output",
            "backup and restore drill report",
        ],
    }
    (output_dir / "release_evidence_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(output_dir / "release_evidence_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
