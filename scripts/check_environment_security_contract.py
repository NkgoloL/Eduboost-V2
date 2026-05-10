#!/usr/bin/env python3
"""Validate production environment-security configuration contracts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIREMENTS = {
    "app/core/config.py": (
        'ENVIRONMENT: Literal["development", "test", "staging", "production"]',
        'APP_ENV: Literal["development", "test", "staging", "production"]',
        "def is_production(self) -> bool:",
        "AZURE_KEY_VAULT_URL",
        "refresh_from_key_vault",
        "load_production_secrets_from_key_vault",
        "AZURE_KEY_VAULT_URL is required when APP_ENV is production",
        "KEY_VAULT_SECRET_NAMES",
        "JWT_SECRET",
        "ENCRYPTION_KEY",
        "GROQ_API_KEY",
        "ANTHROPIC_API_KEY",
    ),
}


@dataclass(frozen=True)
class EnvContractResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[EnvContractResult]:
    results: list[EnvContractResult] = []
    for rel_path, snippets in REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                EnvContractResult(
                    target=rel_path,
                    ok=snippet in text,
                    detail=f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )
    return results


def main() -> int:
    results = run_checks()
    print("Environment security contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
