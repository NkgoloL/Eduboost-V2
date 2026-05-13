# Production Lesson Generation Validation Contract

## Purpose

This contract defines structured lesson output, content correctness validation, golden prompt coverage, and CAPS alignment evidence.

## Required lesson output fields

- topic
- grade
- subject
- CAPS reference
- objectives
- explanation
- worked examples
- practice questions
- answer key
- remediation hints
- difficulty
- language level
- safety classification
- alignment confidence
- quality score

## Required rejection paths

- reject generated lesson if schema invalid
- reject generated lesson if CAPS alignment invalid
- reject generated lesson if age-inappropriate
- reject generated lesson if unsafe
- reject generated lesson if PII detected
- reject generated lesson if answer key missing
- reject generated lesson if answer key inconsistent
- reject generated lesson if quality score is below threshold
- reject generated lesson if alignment confidence is below threshold

## Required validators

- arithmetic correctness validator
- answer-key consistency validator
- grade-level readability validator
- missing-explanation validator
- unsafe-content validator
- PII-leakage validator
- independent answer-key checking
- content quality score threshold
- low-confidence rejection path
- low-confidence human-review path

## Golden prompt coverage

- golden prompt test for each supported grade
- golden prompt test for each supported subject
- golden prompt test for each launch topic
- golden prompt test for English
- golden prompt test for isiZulu
- golden prompt test for Afrikaans
- golden prompt test for isiXhosa
- golden prompt test for standard lesson variant
- golden prompt test for visual variant
- golden prompt test for story-based variant
- golden prompt test for step-by-step variant
- golden prompt test for exam-style variant
- golden prompt test for real-world South African examples
- golden prompt report artifact is present

## Boundary

This repository-side lesson validation contract records deterministic schema, safety, and CAPS-alignment evidence only. It does not claim full CAPS coverage until curriculum coverage is independently reviewed.
