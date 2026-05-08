# Diagnostic Item Contract

Diagnostic items must carry enough metadata to support IRT, review workflows, CAPS alignment, and learner-safe explanations.

## Required fields

- item ID
- subject
- grade
- topic
- skill
- difficulty
- discrimination
- correct answer
- four distractors/options
- explanation
- CAPS reference
- review status
- optional misconception tag

## Review lifecycle

Allowed review states:

- `draft`
- `ai_generated`
- `human_reviewed`
- `approved`
- `retired`

Only approved items should be used for high-stakes claims. AI-generated items may be used in internal testing or explicitly labelled beta flows.

## Validation

`app/services/diagnostic_safety.py` validates:

- finite IRT difficulty/discrimination bounds;
- canonical CAPS references;
- complete A/B/C/D option sets;
- distinct distractors;
- explanation presence;
- valid review state.
