# AI Safety Evidence Index

## Cluster F Closure

- `scripts/check_cluster_f_closure.py`
- `.github/workflows/cluster-f-ai-safety.yml`

## Curriculum Alignment

- `docs/ai/caps_alignment_contract.md`
- `docs/ai/ai_prompt_input_contract.md`
- `docs/ai/ai_prompt_surface_inventory.md`
- `docs/ai/ai_prompt_secret_leakage_guard.md`

## Safety Boundaries

- `docs/ai/ai_safety_boundary_contract.md`
- `docs/ai/diagnostic_generation_safety_contract.md`
- `docs/ai/lesson_generation_safety_contract.md`
- `docs/ai/remediation_safety_contract.md`

## Provider and Output Contracts

- `docs/ai/llm_provider_fallback_contract.md`
- `docs/ai/ai_output_schema_contract.md`
- `docs/ai/ai_output_fixtures.md`
- `docs/ai/ai_refusal_regression_fixtures.md`
- `docs/ai/ai_fixture_coverage_matrix.md`

## Required Commands

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
