#!/usr/bin/env python3
"""Validate production-readiness evidence for AI, LLM safety, lesson generation, and CAPS validation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "app/services/llm/__init__.py",
    "app/services/llm/gateway.py",
    "app/services/content_safety/__init__.py",
    "app/services/content_safety/pii.py",
    "app/services/content_safety/lesson_contracts.py",
    "docs/ai/production_llm_gateway_contract.md",
    "docs/ai/production_ai_pii_safety_contract.md",
    "docs/ai/production_lesson_generation_validation_contract.md",
    "docs/curriculum/caps_topic_map_production_contract.md",
    "tests/fixtures/ai/golden_prompt_coverage.json",
    "tests/unit/test_ai_llm_safety_caps_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/services/llm/gateway.py": (
        "class CanonicalLLMGateway",
        "class DeterministicMockProvider",
        "provider_name",
        "model_version",
        "prompt_template_version",
        "input_schema",
        "output_schema",
        "latency_ms",
        "token_usage",
        "safety_status",
        "fallback_status",
        "timeout_seconds",
        "retry_count",
        "circuit_breaker_status",
        "budget_status",
        "DISABLE_LESSON_GENERATION",
    ),
    "app/services/content_safety/pii.py": (
        "pseudonym_id",
        "learner_name",
        "guardian_name",
        "email",
        "phone",
        "address",
        "learner_uuid",
        "scrub_feedback_for_rlhf",
        "consent_granted",
    ),
    "app/services/content_safety/lesson_contracts.py": (
        "class LessonOutput",
        "CAPS_TOPIC_MAP",
        "phase",
        "grade",
        "subject",
        "term",
        "topic",
        "subtopic",
        "prerequisites",
        "assessment_standards",
        "validate_lesson_output",
        "arithmetic_expression_is_correct",
        "answer key missing or inconsistent",
    ),
    "docs/ai/production_llm_gateway_contract.md": (
        "provider name is required in gateway metadata",
        "model/version is required in gateway metadata",
        "prompt template version is required in gateway metadata",
        "input schema is required in gateway metadata",
        "output schema is required in gateway metadata",
        "latency is required in gateway metadata",
        "token usage is required in gateway metadata",
        "safety status is required in gateway metadata",
        "fallback status is required in gateway metadata",
        "deterministic mock provider is supported",
        "emergency flag DISABLE_LESSON_GENERATION disables lesson generation",
    ),
    "docs/ai/production_ai_pii_safety_contract.md": (
        "no raw learner name enters prompts",
        "no guardian name enters prompts",
        "no email enters prompts",
        "no phone number enters prompts",
        "no address enters prompts",
        "pseudonym_id is used for LLM context",
        "PII seeded tests cover lesson generation context",
        "PII seeded tests cover parent summaries context",
        "PII seeded tests cover RLHF feedback context",
        "PII seeded tests cover log-style text redaction",
        "CI fails if PII is detected in prompt paths",
    ),
    "docs/ai/production_lesson_generation_validation_contract.md": (
        "topic",
        "grade",
        "subject",
        "CAPS reference",
        "objectives",
        "explanation",
        "worked examples",
        "practice questions",
        "answer key",
        "remediation hints",
        "difficulty",
        "language level",
        "safety classification",
        "alignment confidence",
        "quality score",
        "reject generated lesson if schema invalid",
        "reject generated lesson if CAPS alignment invalid",
        "reject generated lesson if age-inappropriate",
        "reject generated lesson if unsafe",
        "reject generated lesson if PII detected",
        "reject generated lesson if answer key missing",
        "reject generated lesson if answer key inconsistent",
        "golden prompt test for isiZulu",
        "golden prompt test for Afrikaans",
        "golden prompt test for isiXhosa",
    ),
    "docs/curriculum/caps_topic_map_production_contract.md": (
        "phase",
        "grade",
        "subject",
        "term",
        "topic",
        "subtopic",
        "prerequisites",
        "assessment standards",
        "generated content references a valid CAPS topic",
        "full CAPS coverage claims are prevented until coverage is validated",
        "alignment confidence score is required per lesson",
    ),
    "tests/fixtures/ai/golden_prompt_coverage.json": (
        "English",
        "isiZulu",
        "Afrikaans",
        "isiXhosa",
        "standard",
        "visual",
        "story_based",
        "step_by_step",
        "exam_style",
        "real_world_sa",
    ),
}


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    detail: str


def run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []
    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        results.append(CheckResult(path.exists(), f"required file exists: {rel_path}" if path.exists() else f"missing required file: {rel_path}"))
    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(CheckResult(snippet in text, f"{rel_path} contains {snippet!r}" if snippet in text else f"{rel_path} missing {snippet!r}"))
    return results


def main() -> int:
    results = run_checks()
    print("AI, LLM safety, lesson generation, and CAPS validation production-readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
