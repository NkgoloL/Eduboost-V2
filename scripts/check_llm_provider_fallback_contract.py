#!/usr/bin/env python3
"""Validate LLM provider fallback evidence contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "ai" / "llm_provider_fallback_contract.md"
CONFIG = REPO_ROOT / "app" / "core" / "config.py"

DOC_SNIPPETS = (
    "LLM Provider Fallback Contract",
    "fallback must not bypass consent or object authorization",
    "fallback must preserve CAPS-aligned prompt inputs",
    "fallback must preserve AI safety boundary instructions",
    "fallback must not expose provider secrets",
    "fallback must fail closed when no safe provider is available",
    "local fallback must use bounded token and temperature settings",
)

CONFIG_SNIPPETS = (
    "LLM_PROVIDER",
    "LLM_TIMEOUT_SECONDS",
    "LLM_MAX_RETRIES",
    "ANTHROPIC_MODEL",
    "LOCAL_BASE_MODEL_ID",
    "LOCAL_ADAPTER_PATH",
    "LOCAL_MERGED_MODEL_PATH",
    "LOCAL_LLM_MAX_NEW_TOKENS",
    "LOCAL_LLM_TEMPERATURE",
)


@dataclass(frozen=True)
class LlmFallbackResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[LlmFallbackResult]:
    results: list[LlmFallbackResult] = []
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    config_text = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""

    results.append(
        LlmFallbackResult(
            str(DOC.relative_to(REPO_ROOT)),
            DOC.exists(),
            "contract present" if DOC.exists() else "contract missing",
        )
    )

    for snippet in DOC_SNIPPETS:
        results.append(
            LlmFallbackResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in CONFIG_SNIPPETS:
        results.append(
            LlmFallbackResult(
                str(CONFIG.relative_to(REPO_ROOT)),
                snippet in config_text,
                f"contains {snippet!r}" if snippet in config_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("LLM provider fallback contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
