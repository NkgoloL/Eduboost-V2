# CAPS And AI Safety Evidence

Date: 2026-05-11
Branch: `codex/pr21-caps-ai-safety-evidence`
Base: `codex/pr20-privacy-legal-evidence`

## Purpose

This document records the local CAPS, learning-science, lesson-bank, diagnostics,
and AI-safety evidence available for the production-readiness PR series. It
separates static/local contract evidence from live provider and full curriculum
approval gates that remain open.

## Local Green Checks

The following command passed:

```bash
make caps-ai-safety-release-evidence-check caps-learning-proof-check caps-alignment-contract-check learning-evidence-check ai-safety-release-check ai-safety-boundary-check cluster-f-ai-safety-check ai-refusal-fixture-check ai-prompt-secret-leakage-check ai-fixture-coverage-check ai-prompt-input-contract-check diagnostic-generation-safety-check llm-provider-fallback-contract-check ai-output-schema-contract-check lesson-generation-safety-check remediation-safety-contract-check ai-output-fixture-validation-check ai-prompt-surface-inventory-check diagnostics-assessment-check
```

Observed result:

- CAPS learning proof check passed.
- CAPS alignment contract check passed.
- Learning evidence check passed.
- AI safety release evidence check passed.
- AI safety boundary and Cluster F evidence checks passed.
- AI refusal fixtures, prompt secret leakage guard, and fixture coverage checks passed.
- Prompt input, diagnostic generation, provider fallback, output schema, lesson generation, and remediation safety checks passed.
- AI output fixture validation and prompt surface inventory checks passed.
- Diagnostics assessment check and its focused unit tests passed.

The following command was attempted and remains an environment/curriculum gate:

```bash
make lesson-bank-check
```

Observed result:

- The nested `scripts/ci` import path is now repo-root aware.
- The check now uses the async lesson repository and current validator result fields.
- The local run did not complete because PostgreSQL authentication failed for user `postgres`.
- The static Grade 4 Mathematics item bank still has fewer than 8 approved items per launch CAPS reference.

## Grade 4 Mathematics Scope

The current item bank contains 121 Grade 4 Mathematics items across the launch
CAPS references. Review status is:

- 14 `approved` items.
- 1 `human_reviewed` item.
- 106 `ai_generated` items.

This matches the CAPS learning proof and coverage matrix language that the
project has 14 approved starter items and the approval gate remains open.

## AI Safety Scope

The local AI safety evidence covers:

- Prompt input constraints and prompt surface inventory.
- Refusal fixtures for unsafe instruction, privacy leakage, and hidden prompt disclosure.
- PII and secret leakage guard documentation.
- Output schema validation contracts and fixture validation.
- LLM provider fallback contract evidence.
- Diagnostic, lesson generation, and remediation safety contracts.

## Release Blockers

- No live external LLM provider staging run was executed in this PR.
- No educator content-review sign-off was completed for the generated item backlog.
- Full Grade 4 Mathematics CAPS production coverage is not complete until the remaining generated items are reviewed and approved.
- DB-backed `lesson-bank-check` remains blocked until a valid staging/test database is available and the approval threshold is met.
- Safety checks remain local contract and fixture evidence, not production abuse testing.

## Release Claim

This PR establishes local CAPS, learning-science, diagnostics, lesson-bank, and
AI-safety contract evidence. It does not claim full CAPS coverage, live-provider AI readiness, educator sign-off, or production AI safety certification.
