# ADR 0009: CAPS Alignment

## Status
Proposed

## Context
EduBoost targets South African curriculum-aligned learning. Generated lessons, diagnostics, item banks, prerequisites, and progress models must map to recognised CAPS concepts and grade/term expectations.

## Decision
EduBoost will maintain a canonical CAPS topic map and require AI-generated or imported learning content to reference validated curriculum identifiers where applicable.

Expected properties:

- Grade, phase, subject, term, topic, subtopic, prerequisite, and assessment-standard metadata.
- Validation before content is treated as production-grade.
- Human curriculum review for high-impact or ambiguous mappings.
- Tests for invalid, missing, or inconsistent CAPS references.

## Consequences

- **Pros**: Stronger educational correctness, better diagnostics, safer personalisation, clearer educator review workflows.
- **Cons**: Requires maintained curriculum data and explicit handling of incomplete mappings.
