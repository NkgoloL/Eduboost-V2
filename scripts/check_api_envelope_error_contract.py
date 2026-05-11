#!/usr/bin/env python3
"""Validate API envelope and error-contract evidence wiring."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "app/domain/api_v2_models.py",
    "app/core/exceptions.py",
    "docs/error_contract.md",
    "docs/api_envelope_contract.md",
    "tests/unit/test_api_v2_envelope.py",
    "tests/unit/test_exception_envelopes.py",
    "tests/unit/test_api_envelope_error_contract.py",
    "scripts/check_api_envelope_error_contract.py",
)

CONTENT_REQUIREMENTS = {
    "app/domain/api_v2_models.py": (
        "class ApiMeta",
        "class ApiError",
        "class ApiEnvelope",
        "class PaginationMeta",
        "def ok",
        "def fail",
        "def paginated",
        "request_id",
        "api_version",
    ),
    "app/core/exceptions.py": (
        "register_exception_handlers",
        "RequestValidationError",
        "RateLimitExceeded",
        "ConsentRequiredError",
        "ConsentExpiredError",
        "internal_error",
        "An unexpected error occurred",
    ),
    "docs/error_contract.md": (
        "Canonical Shape",
        "Baseline Error Codes",
        "validation_error",
        "consent_required",
        "popia_violation",
        "Security Rules",
    ),
    "docs/api_envelope_contract.md": (
        "Success Envelope",
        "Error Envelope",
        "Pagination Envelope",
        "Router Rollout",
        "make api-envelope-error-contract-check",
        "Verification Gaps",
    ),
    "Makefile": (
        "api-envelope-error-contract-check",
    ),
}

BASELINE_ERROR_CODES = (
    "validation_error",
    "unauthorized",
    "forbidden",
    "not_found",
    "conflict",
    "rate_limited",
    "consent_required",
    "consent_expired",
    "dependency_unavailable",
    "internal_error",
    "popia_violation",
    "http_error",
)


@dataclass(frozen=True)
class EvidenceResult:
    target: str
    ok: bool
    detail: str


def check_all() -> list[EvidenceResult]:
    results: list[EvidenceResult] = []
    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))

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

    error_doc = (REPO_ROOT / "docs/error_contract.md").read_text(encoding="utf-8")
    for code in BASELINE_ERROR_CODES:
        results.append(
            EvidenceResult(
                "docs/error_contract.md",
                f"`{code}`" in error_doc,
                f"documents `{code}`" if f"`{code}`" in error_doc else f"missing `{code}`",
            )
        )

    return results


def main() -> int:
    results = check_all()
    print("API envelope/error contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
