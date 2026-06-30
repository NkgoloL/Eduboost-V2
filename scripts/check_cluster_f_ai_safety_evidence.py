#!/usr/bin/env python3
"""Validate Cluster F AI/CAPS/safety evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "tests/unit/test_cluster_f_secret_fixture_coverage_evidence.py",
    "tests/unit/test_ai_fixture_coverage_matrix.py",
    "tests/unit/test_ai_prompt_secret_leakage.py",
    "docs/ai/ai_fixture_coverage_matrix.md",
    "docs/ai/ai_prompt_secret_leakage_guard.md",
    "scripts/check_ai_fixture_coverage_matrix.py",
    "scripts/check_ai_prompt_secret_leakage.py",
    "tests/unit/test_cluster_f_prompt_refusal_evidence.py",
    "tests/unit/test_ai_refusal_fixtures.py",
    "tests/unit/test_ai_prompt_surface_inventory.py",
    "tests/fixtures/ai/refusals/hidden_prompt_refusal.json",
    "tests/fixtures/ai/refusals/privacy_leakage_refusal.json",
    "tests/fixtures/ai/refusals/unsafe_instruction_refusal.json",
    "docs/ai/ai_refusal_regression_fixtures.md",
    "docs/ai/ai_prompt_surface_inventory.md",
    "scripts/check_ai_refusal_fixtures.py",
    "scripts/check_ai_prompt_surface_inventory.py",
    "scripts/generate_ai_prompt_surface_inventory.py",
    "tests/unit/test_cluster_f_fixture_validation_evidence.py",
    "tests/unit/test_validate_ai_output_fixtures.py",
    "tests/unit/test_ai_output_fixtures.py",
    "tests/fixtures/ai/refusal_output.json",
    "tests/fixtures/ai/safe_diagnostic_output.json",
    "tests/fixtures/ai/safe_lesson_output.json",
    "docs/ai/ai_output_fixtures.md",
    "scripts/validate_ai_output_fixtures.py",
    "tests/unit/test_cluster_f_release_gate_wiring.py",
    "tests/unit/test_cluster_f_closure_report.py",
    "docs/ai/CLUSTER_F_CLOSURE.md",
    "tests/unit/test_ai_safety_evidence_index.py",
    "docs/ai/ai_safety_evidence_index.md",
    "tests/unit/test_cluster_f_closure_check.py",
    "tests/unit/test_remediation_safety_contract.py",
    "tests/unit/test_lesson_generation_safety_contract.py",
    "docs/ai/remediation_safety_contract.md",
    "docs/ai/lesson_generation_safety_contract.md",
    "scripts/check_cluster_f_closure.py",
    "scripts/check_remediation_safety_contract.py",
    "scripts/check_lesson_generation_safety_contract.py",
    "tests/unit/test_ai_output_schema_contract.py",
    "tests/unit/test_llm_provider_fallback_contract.py",
    "docs/ai/ai_output_schema_contract.md",
    "docs/ai/llm_provider_fallback_contract.md",
    "scripts/check_ai_output_schema_contract.py",
    "scripts/check_llm_provider_fallback_contract.py",
    "tests/unit/test_diagnostic_generation_safety_contract.py",
    "tests/unit/test_ai_prompt_input_contract.py",
    "docs/ai/diagnostic_generation_safety_contract.md",
    "docs/ai/ai_prompt_input_contract.md",
    "scripts/check_diagnostic_generation_safety_contract.py",
    "scripts/check_ai_prompt_input_contract.py",
    "scripts/check_caps_alignment_contract.py",
    "scripts/check_ai_safety_boundary_contract.py",
    "docs/ai/caps_alignment_contract.md",
    "docs/ai/ai_safety_boundary_contract.md",
    "tests/unit/test_caps_alignment_contract.py",
    "tests/unit/test_ai_safety_boundary_contract.py",
)

CONTENT_REQUIREMENTS = {
    "docs/ai/ai_fixture_coverage_matrix.md": (
        "AI Fixture Coverage Matrix",
        "refusal does not disclose hidden prompts",
    ),
    "docs/ai/ai_prompt_secret_leakage_guard.md": (
        "AI Prompt Secret Leakage Guard",
        "ANTHROPIC_API_KEY",
    ),
    "docs/ai/ai_refusal_regression_fixtures.md": (
        "AI Refusal Regression Fixtures",
        "hidden prompt disclosure",
    ),
    "docs/ai/ai_prompt_surface_inventory.md": (
        "AI Prompt Surface Inventory",
        "no cross-learner data leakage",
    ),
    "scripts/validate_ai_output_fixtures.py": (
        "validate_fixture",
        "refusal suppresses unsafe detail and hidden prompts",
    ),
    "docs/ai/ai_output_fixtures.md": (
        "AI Output Fixtures",
        "safe educational redirection",
    ),
    "docs/operations/project_evidence_index.md": (
        "AI/CAPS Safety Contract",
        "docs/ai/ai_safety_evidence_index.md",
        "make cluster-f-closure-check",
    ),
    "docs/operations/staging_release_gate.md": (
        "make cluster-f-closure-check",
        "docs/ai/CLUSTER_F_CLOSURE.md",
    ),
    "docs/operations/release_evidence_manifest.md": (
        "Cluster F AI safety",
        "make cluster-f-closure-check",
    ),
    "docs/ai/CLUSTER_F_CLOSURE.md": (
        "Cluster F AI/CAPS/Diagnostics Safety Closure",
        "make cluster-f-closure-check",
        "evidence scaffold",
    ),
    "docs/ai/ai_safety_evidence_index.md": (
        "AI Safety Evidence Index",
        "Cluster F Closure",
        "Curriculum Alignment",
        "make cluster-f-closure-check",
    ),
    "docs/ai/remediation_safety_contract.md": (
        "Remediation Safety Contract",
        "remediation must avoid punitive or shaming language",
    ),
    "docs/ai/lesson_generation_safety_contract.md": (
        "Lesson Generation Safety Contract",
        "every lesson must map to a lesson objective",
    ),
    "docs/ai/ai_output_schema_contract.md": (
        "AI Output Schema Contract",
        "safe educational redirection",
    ),
    "docs/ai/llm_provider_fallback_contract.md": (
        "LLM Provider Fallback Contract",
        "fallback must fail closed when no safe provider is available",
    ),
    "docs/ai/diagnostic_generation_safety_contract.md": (
        "Diagnostic Generation Safety Contract",
        "every item must map to the diagnostic objective",
    ),
    "docs/ai/ai_prompt_input_contract.md": (
        "AI Prompt Input Contract",
        "prompts must avoid cross-learner data leakage",
    ),
    "Makefile": (
        "caps-alignment-contract-check:",
        "ai-safety-boundary-check:",
        "ai-prompt-input-contract-check:",
        "diagnostic-generation-safety-check:",
        "llm-provider-fallback-contract-check:",
        "ai-output-schema-contract-check:",
        "lesson-generation-safety-check:",
        "remediation-safety-contract-check:",
        "cluster-f-closure-check:",
        "ai-output-fixture-validation-check:",
        "ai-prompt-surface-inventory:",
        "ai-prompt-surface-inventory-check:",
        "ai-refusal-fixture-check:",
        "ai-prompt-secret-leakage-check:",
        "ai-fixture-coverage-check:",
    ),
    "docs/ai/caps_alignment_contract.md": (
        "CAPS Alignment Contract",
        "generated diagnostics must be objective-bound",
    ),
    "docs/ai/ai_safety_boundary_contract.md": (
        "AI Safety Boundary Contract",
        "Unsafe requests must be refused",
    ),
}


@dataclass(frozen=True)
class ClusterFResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ClusterFResult]:
    results: list[ClusterFResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(ClusterFResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                ClusterFResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Cluster F AI safety evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
