# FE-PR-013 Parent Review and Retention

## Purpose

Document the parent-review and retention requirements for FE-PR-013 tutor-related features. This file clarifies what can be stored, how long it is retained, and how guardians can review tutor interactions.

## Parent review requirements

- Tutor interactions must be available for guardian review when enabled.
- Review data is limited to pseudonymous session metadata and safe utterance summaries.
- Guardian access is authenticated and scoped to their learner.
- No raw tutor transcript or PII is exposed in the parent review view.

## Retention policy requirements

- Tutor session metadata retention must be explicitly defined before any history is persisted.
- Minimum acceptable approach for planning:
  - Retain tutor session summaries for 30 days.
  - Store only what is required for review and safety.
  - Delete or anonymize data after the retention window ends.

## Allowed storage model

- Store structured session records such as:
  - lesson identifier
  - session start/end timestamps
  - high-level prompt categories (e.g. "word help", "math hint")
  - safe, non-PII response summaries
  - audit event markers for safety and consent

## Blocked storage model

- Raw tutor transcripts.
- Learner PII in stored tutor records.
- Persisted audio or voice recordings.
- Unapproved long-term history beyond documented retention.
- Any storage that enables unrestricted free chat analysis.

## Guardian UX expectations

- Guardians should be able to see whether tutor help was used in the lesson.
- Guardians should be able to review flagged safety cases and consent status.
- Guardians should see a clear retention window and deletion policy.

## Audit and retention tests

- Test that stored records exclude raw transcripts and PII.
- Test that retention metadata is present on saved tutor sessions.
- Test that guardian review data is accessible only to authenticated guardians.
- Test that no tutor history is saved before the parent-review schema is approved.

## Rollback plan

- If the retention policy is not accepted, disable tutor history persistence.
- Keep only ephemeral tutor session metadata for the current UX, not long-term storage.
- Remove guardian review controls until the approved review schema is implemented.
