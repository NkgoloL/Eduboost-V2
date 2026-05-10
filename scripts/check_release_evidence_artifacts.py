#!/usr/bin/env python3
"""Validate release-evidence artifact coverage and drift."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ARTIFACTS = (
    "docs/operations/release_evidence_manifest.md",
    "docs/operations/staging_release_gate.md",
    "docs/operations/deployment_readiness_checklist.md",
    "docs/operations/cluster_d_closure_check.md",
    "docs/security/environment_security_contract.md",
    "docs/security/production_secret_placeholder_guard.md",
    "docs/security/production_key_vault_behavior.md",
    "docs/security/dev_only_endpoint_exposure.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/security/PHASE2_AUTHORIZATION_CLOSURE.md",
    "docs/openapi.json",
    "docs/route_inventory.md",
)

REQUIRED_MANIFEST_SNIPPETS = (
    "make runtime-check",
    "make openapi-check",
    "make route-inventory-check",
    "make pr002r-check",
    "make phase2-authz-closure",
    "make popia-consent-closure-check",
    "make cluster-d-closure-check",
)

REQUIRED_GATE_SNIPPETS = (
    "Production promotion is blocked",
    "docs/operations/release_evidence_manifest.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/security/PHASE2_AUTHORIZATION_CLOSURE.md",
)


@dataclass(frozen=True)
class ReleaseEvidenceResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ReleaseEvidenceResult]:
    results: list[ReleaseEvidenceResult] = []

    for rel_path in REQUIRED_ARTIFACTS:
        path = REPO_ROOT / rel_path
        results.append(
            ReleaseEvidenceResult(
                category="artifact",
                target=rel_path,
                ok=path.exists(),
                detail="present" if path.exists() else "missing",
            )
        )

    manifest = REPO_ROOT / "docs" / "operations" / "release_evidence_manifest.md"
    manifest_text = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    for snippet in REQUIRED_MANIFEST_SNIPPETS:
        results.append(
            ReleaseEvidenceResult(
                category="manifest",
                target=str(manifest.relative_to(REPO_ROOT)),
                ok=snippet in manifest_text,
                detail=f"contains {snippet!r}" if snippet in manifest_text else f"missing {snippet!r}",
            )
        )

    gate = REPO_ROOT / "docs" / "operations" / "staging_release_gate.md"
    gate_text = gate.read_text(encoding="utf-8") if gate.exists() else ""
    for snippet in REQUIRED_GATE_SNIPPETS:
        results.append(
            ReleaseEvidenceResult(
                category="staging_gate",
                target=str(gate.relative_to(REPO_ROOT)),
                ok=snippet in gate_text,
                detail=f"contains {snippet!r}" if snippet in gate_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Release evidence artifact check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
