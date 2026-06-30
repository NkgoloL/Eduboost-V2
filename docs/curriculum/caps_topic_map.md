# CAPS Topic Map MVP

EduBoost uses a versioned CAPS topic map as the canonical curriculum reference for AI generation, diagnostics, and coverage reporting.

## Version

`caps-mvp-2026.05`

## Canonical fields

Each topic record contains:

- phase
- grade
- subject
- term
- topic
- subtopic
- prerequisites
- assessment standards
- canonical reference

References use this form:

```text
CAPS:<version>:G<grade>:<subject>:T<term>:<topic>:<subtopic>
```

Example:

```text
CAPS:caps-mvp-2026.05:G4:mathematics:T1:fractions:equivalent-fractions
```

## Runtime enforcement

- `app/services/curriculum/caps_topic_map.py` owns the canonical map.
- `app/services/caps_validator.py` validates requested and generated lesson alignment.
- `app/core/llm_gateway.py` injects CAPS references into prompts and persists alignment metadata.
- `app/services/curriculum/coverage.py` detects topics without lessons, diagnostic items, or quality-reviewed content.

The MVP map is intentionally narrow. Do not claim full CAPS coverage until the map, lesson bank, diagnostic item bank, answer keys, and review status are complete for the advertised scope.
