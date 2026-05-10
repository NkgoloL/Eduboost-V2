# AI Output Fixtures

## Purpose

Fixture-based AI output validation checks structured lesson, diagnostic, and
refusal examples without making live model calls.

## Fixtures

- `tests/fixtures/ai/safe_lesson_output.json`
- `tests/fixtures/ai/safe_diagnostic_output.json`
- `tests/fixtures/ai/refusal_output.json`

## Required Fixture Types

- lesson
- diagnostic
- refusal

## Safety Requirements

- safe outputs must contain `safety_status`
- lesson outputs must include learner-facing educational content
- diagnostic outputs must include answer keys and explanations
- refusal outputs must include safe educational redirection
- refusal outputs must not disclose hidden prompts
