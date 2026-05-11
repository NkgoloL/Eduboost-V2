#!/usr/bin/env python3
"""Validate privacy, consent, POPIA, authorization, and audit evidence wiring."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/security/object_authorization.md",
    "docs/security/authorization_dependencies.md",
    "docs/security/PHASE2_AUTHORIZATION_CLOSURE.md",
    "docs/security/popia_consent_gate_inventory.md",
    "docs/security/popia_consent_boundary_matrix.md",
    "docs/security/POPIA_CONSENT_AUDIT_BASELINE.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/security/audit_event_contracts.md",
    "docs/compliance/popia_data_rights.md",
    "docs/compliance/data_retention_policy.md",
    "docs/security/privacy_boundary_evidence.md",
    "scripts/check_phase2_authorization_evidence.py",
    "scripts/check_phase2_authorization_closure.py",
    "scripts/generate_consent_gate_inventory.py",
    "scripts/check_consent_gate_inventory.py",
    "scripts/generate_popia_consent_boundary_matrix.py",
    "scripts/check_popia_consent_boundary_matrix.py",
    "scripts/check_popia_consent_audit_evidence.py",
    "scripts/check_audit_event_contracts.py",
    "tests/unit/test_privacy_boundary_evidence.py",
)

CONTENT_REQUIREMENTS = {
    "docs/security/privacy_boundary_evidence.md": (
        "Object Authorization",
        "Consent Gates",
        "POPIA Data Rights",
        "Audit Completeness",
        "make privacy-boundary-check",
        "Verification Gaps",
    ),
    "Makefile": (
        "phase2-authz-check",
        "popia-consent-gate-check",
        "popia-consent-boundary-check",
        "popia-consent-audit-check",
        "audit-contract-check",
        "privacy-boundary-check",
    ),
}


@dataclass(frozen=True)
class EvidenceResult:
    target: str
    ok: bool
    detail: str


def check_all() -> list[EvidenceResult]:
    results: list[EvidenceResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing")
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                EvidenceResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = check_all()
    print("Privacy boundary evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
