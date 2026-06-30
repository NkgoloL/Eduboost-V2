#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "docs/POPIA_COMPLIANCE.md",
    "docs/compliance/popia_data_rights.md",
    "docs/compliance/data_retention_policy.md",
    "docs/compliance/subprocessor_register.md",
    "docs/legal/legal_documents_index.md",
    "docs/legal/policy_versioning.md",
    "docs/security/POPIA_CONSENT_AUDIT_BASELINE.md",
    "docs/security/audit_event_contracts.md",
    "tests/test_popia_negative.py",
    "tests/popia/test_right_to_erasure.py",
    "tests/unit/test_audit_event_contracts.py",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    results = [Result(path, (ROOT / path).exists(), "present" if (ROOT / path).exists() else "missing") for path in REQUIRED]
    text = (ROOT / "docs/legal/legal_documents_index.md").read_text(encoding="utf-8")
    for snippet in ("Privacy", "Terms", "Consent", "version"):
        results.append(Result("docs/legal/legal_documents_index.md", snippet.lower() in text.lower(), f"contains {snippet!r}"))
    return results


def main() -> int:
    results = check_all()
    print("POPIA/legal evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
