# Diagnostic Generation Safety Contract

## Purpose

Diagnostic generation must produce curriculum-bounded, age-appropriate,
non-harmful items that measure a specific learner objective.

## Required Diagnostic Inputs

- learner grade
- subject
- topic
- CAPS strand or skill
- diagnostic objective
- difficulty band
- item count
- consent-authorized learner identifier

## Item Safety Rules

- questions must be age-appropriate
- questions must avoid unsafe instructions
- questions must not include sexual content
- questions must not include self-harm content
- questions must not include dangerous activity instructions
- questions must not expose another learner's data
- explanations must remain educational and non-sensitive

## Quality Rules

- every item must map to the diagnostic objective
- answer keys must be present
- distractors must be plausible but not misleading beyond the assessed skill
- remediation hints must map to observed learner gaps

## Command

```bash
make diagnostic-generation-safety-check
```
