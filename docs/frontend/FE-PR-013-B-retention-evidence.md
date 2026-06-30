# FE-PR-013-B Retention Evidence

This document summarizes the retention policy evidence for parent-review records.

- Default retention window: 90 days (`DEFAULT_RETENTION_DAYS` in `retention.ts`).
- API-level storage is redacted via `redaction.ts` before persistence.
- Repository abstraction (`ParentReviewRepository`) is provided to avoid leaking implementation details.
- Tests cover redaction of email, phone, and child-name-like fields.
