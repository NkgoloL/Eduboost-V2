# Cluster F AI/CAPS/Diagnostics Safety Closure

## Scope

Cluster F establishes the first-pass evidence baseline for AI-generated lessons,
diagnostics, remediation, provider fallback, prompt inputs, and structured output
contracts.

## Closure Commands

```bash
make caps-alignment-contract-check
make ai-safety-boundary-check
make ai-prompt-input-contract-check
make diagnostic-generation-safety-check
make lesson-generation-safety-check
make remediation-safety-contract-check
make llm-provider-fallback-contract-check
make ai-output-schema-contract-check
make ai-output-fixture-validation-check
make ai-prompt-surface-inventory-check
make ai-refusal-fixture-check
make ai-prompt-secret-leakage-check
make ai-fixture-coverage-check
make cluster-f-ai-safety-check
make cluster-f-closure-check
```

## Closure Artifacts

- `docs/ai/ai_safety_evidence_index.md`
- `docs/ai/caps_alignment_contract.md`
- `docs/ai/ai_safety_boundary_contract.md`
- `docs/ai/ai_prompt_input_contract.md`
- `docs/ai/ai_prompt_surface_inventory.md`
- `docs/ai/ai_prompt_secret_leakage_guard.md`
- `docs/ai/diagnostic_generation_safety_contract.md`
- `docs/ai/lesson_generation_safety_contract.md`
- `docs/ai/remediation_safety_contract.md`
- `docs/ai/llm_provider_fallback_contract.md`
- `docs/ai/ai_output_schema_contract.md`
- `docs/ai/ai_output_fixtures.md`
- `docs/ai/ai_refusal_regression_fixtures.md`
- `docs/ai/ai_fixture_coverage_matrix.md`
- `.github/workflows/cluster-f-ai-safety.yml`

## Closure Stamp

Cluster F is first-pass closed when `make cluster-f-closure-check` passes.

## Current Boundary

This closure is an evidence scaffold. It does not perform live model calls in
CI. Runtime model-response sampling, adversarial prompt suites, and provider
integration tests remain future hardening targets.

## Next Hardening Targets

1. Add fixture-based model output validation.
2. Add prompt-template source scanning.
3. Add AI refusal regression fixtures.
4. Add staging-only provider smoke tests.
