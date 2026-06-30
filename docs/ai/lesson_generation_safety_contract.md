# Lesson Generation Safety Contract

## Purpose

Lesson generation must produce CAPS-aligned, age-appropriate, learner-safe
content that is bounded by grade, subject, topic, learner mastery state, and
active consent.

## Required Lesson Inputs

- learner grade
- learner subject
- topic
- CAPS strand or skill
- learner mastery state
- lesson objective
- consent-authorized learner identifier
- safety boundary instructions

## Lesson Safety Rules

- lesson content must be age-appropriate
- lesson content must avoid unsafe instructions
- lesson content must not include sexual content
- lesson content must not include self-harm content
- lesson content must not include dangerous activity instructions
- lesson content must not expose another learner's data
- lesson examples must remain educational and non-sensitive

## Lesson Quality Rules

- every lesson must map to a lesson objective
- explanations must reference the CAPS-aligned topic
- worked examples must match the grade and subject
- practice activities must map to the learner gap
- remediation links must map to observed learner mastery state

## Command

```bash
make lesson-generation-safety-check
```
