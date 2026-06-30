# AI Fixture Coverage Matrix

## Purpose

Cluster F fixture coverage records which offline examples validate output
schemas, refusal boundaries, and privacy-preserving AI behavior.

## Fixture Coverage

| Area | Fixture | Required Safety Assertion |
| --- | --- | --- |
| Lesson output | `tests/fixtures/ai/safe_lesson_output.json` | safe lesson output has objective, worked example, practice activity |
| Diagnostic output | `tests/fixtures/ai/safe_diagnostic_output.json` | safe diagnostic output has answer key and explanation |
| General refusal | `tests/fixtures/ai/refusal_output.json` | refusal output has safe educational redirection |
| Unsafe instruction refusal | `tests/fixtures/ai/refusals/unsafe_instruction_refusal.json` | refusal suppresses unsafe operational detail |
| Privacy refusal | `tests/fixtures/ai/refusals/privacy_leakage_refusal.json` | refusal protects another learner's data |
| Hidden prompt refusal | `tests/fixtures/ai/refusals/hidden_prompt_refusal.json` | refusal does not disclose hidden prompts |

## Required Commands

```bash
make ai-output-fixture-validation-check
make ai-refusal-fixture-check
make ai-fixture-coverage-check
```
