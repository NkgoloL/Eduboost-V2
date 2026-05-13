# Production AI PII Safety Contract

## Purpose

This contract defines POPIA-safe prompt and feedback handling for LLM calls.

## Required prompt-safety controls

- no raw learner name enters prompts
- no guardian name enters prompts
- no email enters prompts
- no phone number enters prompts
- no address enters prompts
- no raw learner UUID enters external prompts if pseudonym is available
- pseudonym_id is used for LLM context
- PII seeded tests cover lesson generation context
- PII seeded tests cover parent summaries context
- PII seeded tests cover RLHF feedback context
- PII seeded tests cover log-style text redaction
- CI fails if PII is detected in prompt paths

## RLHF controls

- RLHF feedback capture is consent-gated
- PII is scrubbed before RLHF storage
- PII is scrubbed before RLHF export
- retained RLHF records include schema version metadata

## Boundary

This repository-side PII safety contract records deterministic redaction and consent-gating evidence only. It does not replace legal review or live audit monitoring.
