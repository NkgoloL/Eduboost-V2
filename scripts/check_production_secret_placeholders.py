#!/usr/bin/env python3
"""Validate production placeholder-secret guardrails."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CONFIG = REPO_ROOT / "app" / "core" / "config.py"

PLACEHOLDER_MARKERS = (
    "CHANGE_ME_IN_PRODUCTION_AT_LEAST_32_CHARS",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    "test-encryption-salt",
    "dev-audit-secret",
)

REQUIRED_PRODUCTION_GATES = (
    "def is_production(self) -> bool:",
    "load_production_secrets_from_key_vault",
    "refresh_from_key_vault",
    "AZURE_KEY_VAULT_URL is required when APP_ENV is production",
    "Azure Key Vault returned an empty value",
    "KEY_VAULT_SECRET_NAMES",
)


@dataclass(frozen=True)
class PlaceholderResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[PlaceholderResult]:
    text = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""
    results: list[PlaceholderResult] = []

    for marker in PLACEHOLDER_MARKERS:
        results.append(
            PlaceholderResult(
                target="dev_placeholder_documented",
                ok=marker in text,
                detail=f"contains dev placeholder {marker!r}" if marker in text else f"missing dev placeholder marker {marker!r}",
            )
        )

    for gate in REQUIRED_PRODUCTION_GATES:
        results.append(
            PlaceholderResult(
                target="production_fail_closed_gate",
                ok=gate in text,
                detail=f"contains production gate {gate!r}" if gate in text else f"missing production gate {gate!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Production placeholder-secret guard check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
