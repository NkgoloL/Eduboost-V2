#!/usr/bin/env python3
"""Generate beta release evidence bundle index."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "operations" / "beta_release_evidence_bundle.md"

BUNDLE_ARTIFACTS = (
    ("backend runtime/API", "docs/openapi.json"),
    ("release evidence manifest", "docs/operations/release_evidence_manifest.md"),
    ("staging release gate", "docs/operations/staging_release_gate.md"),
    ("deployment readiness", "docs/operations/deployment_readiness_checklist.md"),
    ("project evidence index", "docs/operations/project_evidence_index.md"),
    ("beta readiness contract", "docs/operations/beta_release_readiness_contract.md"),
    ("staging smoke manifest", "docs/operations/staging_smoke_evidence_manifest.md"),
    ("beta sign-off manifest", "docs/operations/beta_signoff_manifest.md"),
    ("rollback runbook", "docs/operations/beta_rollback_runbook.md"),
    ("post-deploy smoke checklist", "docs/operations/post_deploy_staging_smoke_checklist.md"),
    ("Cluster C POPIA consent closure", "docs/security/POPIA_CONSENT_GATE_CLOSURE.md"),
    ("Cluster D closure", "docs/operations/CLUSTER_D_CLOSURE.md"),
    ("Cluster E closure", "docs/operations/CLUSTER_E_CLOSURE.md"),
    ("Cluster F closure", "docs/ai/CLUSTER_F_CLOSURE.md"),
    ("Cluster G closure", "docs/frontend/CLUSTER_G_CLOSURE.md"),
)


@dataclass(frozen=True)
class BundleArtifact:
    category: str
    path: str


def _git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def render_bundle(artifacts: tuple[BundleArtifact, ...]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    branch = _git_value(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_value(["rev-parse", "HEAD"])
    release_candidate = os.environ.get("RELEASE_CANDIDATE", "unset")

    lines = [
        "# Beta Release Evidence Bundle",
        "",
        "## Metadata",
        "",
        f"- generated_at_utc: `{generated_at}`",
        f"- branch: `{branch}`",
        f"- commit: `{commit}`",
        f"- release_candidate: `{release_candidate}`",
        "",
        "## Evidence Artifacts",
        "",
        "| Category | Artifact | Present |",
        "| --- | --- | --- |",
    ]

    for artifact in artifacts:
        present = "yes" if (REPO_ROOT / artifact.path).exists() else "no"
        lines.append(f"| {artifact.category} | `{artifact.path}` | `{present}` |")

    lines.extend(
        [
            "",
            "## Bundle Boundary",
            "",
            "The beta release evidence bundle indexes release artifacts. It does not replace execution logs, approvals, or deployment platform records.",
            "",
            "## Command",
            "",
            "```bash",
            "make beta-release-evidence-bundle",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    artifacts = tuple(BundleArtifact(category, path) for category, path in BUNDLE_ARTIFACTS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_bundle(artifacts), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(artifacts)} artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
