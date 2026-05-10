#!/usr/bin/env python3
"""Generate staging smoke evidence manifest."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "staging_smoke_evidence_manifest.md"

SMOKE_CHECKS = (
    ("runtime import smoke", "python3 -m py_compile app/api_v2.py"),
    ("OpenAPI drift smoke", "make openapi-check"),
    ("staging release gate", "make staging-release-gate-check"),
    ("release evidence artifacts", "make release-evidence-artifacts-check"),
    ("Cluster D deployment closure", "make cluster-d-closure-check"),
    ("Cluster E data resilience closure", "make cluster-e-closure-check"),
    ("Cluster F AI safety closure", "make cluster-f-closure-check"),
    ("Cluster G frontend journey closure", "make cluster-g-closure-check"),
)


@dataclass(frozen=True)
class SmokeEntry:
    name: str
    command: str


def _git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def render_manifest(entries: tuple[SmokeEntry, ...]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    environment = os.environ.get("APP_ENV") or os.environ.get("ENVIRONMENT") or "staging"

    lines = [
        "# Staging Smoke Evidence Manifest",
        "",
        "## Metadata",
        "",
        f"- generated_at_utc: `{generated_at}`",
        f"- branch: `{branch}`",
        f"- commit: `{commit}`",
        f"- target_environment: `{environment}`",
        "",
        "## Required Smoke Checks",
        "",
        "| Check | Command |",
        "| --- | --- |",
    ]

    for entry in entries:
        lines.append(f"| {entry.name} | `{entry.command}` |")

    lines.extend(
        [
            "",
            "## Release Boundary",
            "",
            "Staging smoke evidence records required checks. It does not itself prove the",
            "checks were executed unless paired with CI logs or signed release evidence.",
            "",
            "## Command",
            "",
            "```bash",
            "make staging-smoke-evidence-manifest",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    entries = tuple(SmokeEntry(name, command) for name, command in SMOKE_CHECKS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_manifest(entries), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(entries)} smoke check(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
