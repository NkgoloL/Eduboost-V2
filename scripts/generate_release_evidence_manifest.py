#!/usr/bin/env python3
"""Generate a release evidence manifest for staged EduBoost V2 releases."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "release_evidence_manifest.md"

EVIDENCE_COMMANDS = (
    ("Runtime contract", "make runtime-check"),
    ("OpenAPI drift", "make openapi-check"),
    ("Route inventory", "make route-inventory-check"),
    ("PR-002R evidence", "make pr002r-check"),
    ("Phase 2 authorization", "make phase2-authz-closure"),
    ("POPIA consent/audit", "make popia-consent-closure-check"),
    ("Cluster D environment/deployment", "make cluster-d-closure-check"),
)


@dataclass(frozen=True)
class EvidenceCommand:
    name: str
    command: str


def _git_value(args: list[str], fallback: str = "unknown") -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    return value or fallback


def collect_commands() -> list[EvidenceCommand]:
    return [EvidenceCommand(name, command) for name, command in EVIDENCE_COMMANDS]


def render_manifest() -> str:
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        "# Release Evidence Manifest",
        "",
        f"Generated: `{stamp}`",
        f"Branch: `{branch}`",
        f"Commit: `{commit}`",
        "",
        "## Required Evidence Commands",
        "",
        "| Area | Command | Evidence Status |",
        "| --- | --- | --- |",
    ]

    for item in collect_commands():
        lines.append(f"| {item.name} | `{item.command}` | pending |")

    lines.extend(
        [
            "",
            "## Release Evidence Notes",
            "",
            "Attach command output for each row before staging or production promotion.",
            "",
            "## Artifact References",
            "",
            "- `docs/openapi.json`",
            "- `docs/route_inventory.md`",
            "- `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`",
            "- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`",
            "- `docs/operations/deployment_readiness_checklist.md`",
            "- `docs/operations/cluster_d_closure_check.md`",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_manifest(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
