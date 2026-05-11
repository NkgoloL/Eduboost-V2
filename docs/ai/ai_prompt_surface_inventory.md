# AI Prompt Surface Inventory

## Purpose

This inventory records likely prompt construction or AI generation surfaces.

## Required Safety Markers

- CAPS alignment
- learner grade and subject
- consent-authorized learner context
- AI safety boundary instructions
- no cross-learner data leakage

## Discovered Surfaces

| Path | Markers |
| --- | --- |
| `app/api_v2.py` | `diagnostic` |
| `app/api_v2_routers/api_v2.py` | `diagnostic` |
| `app/api_v2_routers/diagnostics.py` | `diagnostic` |
| `app/api_v2_routers/lessons.py` | `generate_lesson` |
| `app/api_v2_routers/popia.py` | `anthropic` |
| `app/api_v2_routers/test_services.py` | `prompt, diagnostic` |
| `app/core/analytics.py` | `diagnostic` |
| `app/core/config.py` | `llm, anthropic, groq` |
| `app/core/degraded_mode.py` | `llm, anthropic, groq` |
| `app/core/exceptions.py` | `llm, remediation` |
| `app/core/health.py` | `llm, anthropic, groq, diagnostic` |
| `app/core/judiciary.py` | `llm, diagnostic` |
| `app/core/llm_gateway.py` | `prompt, llm, anthropic, groq, generate_lesson` |
| `app/core/metrics.py` | `llm, anthropic, groq, diagnostic` |
| `app/core/rate_limit.py` | `llm, diagnostic` |
| `app/domain/api_v2_models.py` | `remediation` |
| `app/domain/llm_schemas.py` | `diagnostic` |
| `app/domain/schemas.py` | `diagnostic` |
| `app/models/__init__.py` | `prompt, llm, groq, diagnostic` |
| `app/modules/diagnostics/__init__.py` | `diagnostic` |
| `app/modules/diagnostics/irt_engine.py` | `diagnostic` |
| `app/modules/diagnostics/service.py` | `diagnostic` |
| `app/modules/jobs.py` | `diagnostic` |
| `app/modules/learners/__init__.py` | `prompt, llm, diagnostic` |
| `app/modules/learners/ether_service.py` | `prompt, llm, diagnostic` |
| `app/modules/lessons/__init__.py` | `llm, anthropic, groq` |
| `app/modules/lessons/llm_gateway.py` | `prompt, llm, anthropic, groq` |
| `app/modules/lessons/service.py` | `llm, groq, generate_lesson` |
| `app/repositories/__init__.py` | `diagnostic` |
| `app/repositories/diagnostic_repository.py` | `diagnostic` |
| `app/repositories/repositories.py` | `diagnostic` |
| `app/services/curriculum/coverage.py` | `diagnostic` |
| `app/services/diagnostic.py` | `diagnostic` |
| `app/services/diagnostic_safety.py` | `llm, diagnostic` |
| `app/services/diagnostic_service_v2.py` | `diagnostic` |
| `app/services/executive.py` | `llm` |
| `app/services/lesson_service_v2.py` | `llm, generate_lesson` |
| `app/services/pii_sweep.py` | `anthropic` |
| `app/services/popia_service.py` | `diagnostic` |
| `app/services/quota_service.py` | `llm` |
| `app/services/rlhf_service.py` | `anthropic` |
| `app/services/system_service_v2.py` | `diagnostic` |
| `scripts/build_corrective_caps_v2.py` | `prompt, llm, remediation` |
| `scripts/build_focused_caps_dataset.py` | `remediation` |
| `scripts/build_guardrails_dataset.py` | `remediation` |
| `scripts/check_ai_fixture_coverage_matrix.py` | `prompt, diagnostic` |
| `scripts/check_ai_output_schema_contract.py` | `prompt, diagnostic` |
| `scripts/check_ai_prompt_input_contract.py` | `prompt, diagnostic` |
| `scripts/check_ai_prompt_secret_leakage.py` | `prompt, system_message, user_message, anthropic, groq, generate_lesson, diagnostic, remediation` |
| `scripts/check_ai_prompt_surface_inventory.py` | `prompt` |
| `scripts/check_ai_refusal_fixtures.py` | `prompt` |
| `scripts/check_ai_safety_boundary_contract.py` | `prompt` |
| `scripts/check_caps_alignment_contract.py` | `prompt, diagnostic, remediation` |
| `scripts/check_cluster_f_ai_safety_evidence.py` | `prompt, llm, anthropic, diagnostic, remediation` |
| `scripts/check_cluster_f_closure.py` | `prompt, llm, diagnostic, remediation` |
| `scripts/check_diagnostic_generation_safety_contract.py` | `diagnostic` |
| `scripts/check_environment_security_contract.py` | `anthropic, groq` |
| `scripts/check_llm_provider_fallback_contract.py` | `prompt, llm, anthropic` |
| `scripts/check_phase2_authorization_evidence.py` | `diagnostic` |
| `scripts/check_popia_consent_audit_evidence.py` | `diagnostic` |
| `scripts/check_popia_consent_boundary_matrix.py` | `generate_lesson, diagnostic` |
| `scripts/check_remediation_safety_contract.py` | `remediation` |
| `scripts/evaluate_pedagogy.py` | `prompt, llm` |
| `scripts/generate_ai_prompt_surface_inventory.py` | `prompt, system_message, user_message, llm, anthropic, groq, generate_lesson, diagnostic, remediation` |
| `scripts/generate_consent_gate_inventory.py` | `diagnostic` |
| `scripts/generate_learner_authz_matrix.py` | `diagnostic` |
| `scripts/generate_popia_consent_boundary_matrix.py` | `generate_lesson, diagnostic` |
| `scripts/generate_route_inventory.py` | `diagnostic` |
| `scripts/maintenance/audit_todo_backlog.py` | `prompt, llm, diagnostic, remediation` |
| `scripts/merge_lora.py` | `llm` |
| `scripts/popia_sweep.py` | `prompt, llm, anthropic, groq, diagnostic` |
| `scripts/prepare_training_data.py` | `llm` |
| `scripts/seed_irt_items.py` | `diagnostic` |
| `scripts/sync_git_to_redmine.py` | `diagnostic` |
| `scripts/train_qlora.py` | `prompt, llm` |
| `scripts/validate_ai_output_fixtures.py` | `prompt, diagnostic, remediation` |
| `scripts/validate_focused_adapter.py` | `llm` |
| `scripts/validate_ops_assets.py` | `llm` |
| `scripts/validate_runtime_env.py` | `anthropic, groq` |
| `scripts/validate_schema_integrity.py` | `diagnostic` |

## Command

```bash
python scripts/generate_ai_prompt_surface_inventory.py
```
