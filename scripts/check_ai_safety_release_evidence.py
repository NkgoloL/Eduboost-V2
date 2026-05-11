#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "app/core/llm_gateway.py",
    "app/services/ai_safety.py",
    "app/services/pii_sweep.py",
    "docs/ai/ai_safety_boundary_contract.md",
    "docs/ai/ai_prompt_input_contract.md",
    "docs/ai/ai_output_schema_contract.md",
    "docs/ai/ai_refusal_regression_fixtures.md",
    "docs/ai/llm_provider_fallback_contract.md",
    "docs/ai/remediation_safety_contract.md",
    "tests/fixtures/ai/refusals/privacy_leakage_refusal.json",
    "tests/unit/test_ai_safety_boundary_contract.py",
    "tests/unit/test_ai_prompt_input_contract.py",
    "tests/unit/test_ai_output_schema_contract.py",
    "tests/unit/test_ai_refusal_fixtures.py",
    "tests/unit/test_llm_provider_fallback_contract.py",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    return [Result(p, (ROOT / p).exists(), "present" if (ROOT / p).exists() else "missing") for p in REQUIRED]


def main() -> int:
    results = check_all()
    print("AI safety release evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
