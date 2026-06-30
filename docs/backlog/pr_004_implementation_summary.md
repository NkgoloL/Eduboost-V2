# PR-004 POPIA consent/data-rights/audit implementation summary

## Scope

This patch hardens POPIA consent semantics, learner data-rights workflows, and audit integrity without changing the canonical `app.api_v2:app` runtime entrypoint.

## Implemented

- Canonical consent-state policy in `app/core/consent_policy.py`.
- Persisted `parental_consents.status` migration for `pending`, `granted`, `denied`, `expired`, `withdrawn`, and `renewal_required`.
- Consent service now returns policy decisions and blocks pending/denied/expired/withdrawn states with audit evidence.
- POPIA data-rights service centralizes export, erasure, correction, and processing-restriction workflows.
- POPIA router now exposes correction and restriction endpoints and uses the centralized service.
- Export supports JSON and CSV formats with SLA/status metadata.
- Erasure preserves append-only audit records and returns review/SLA metadata.
- Audit repository now computes an event hash, previous-event hash, and HMAC signature for tamper evidence.
- Added data retention policy and subprocessor register.
- Added focused unit tests for consent policy, audit hashing, and erasure authorization.

## Not completed

- Guardian-friendly PDF export remains out of scope for this PR.
- School-mediated consent remains a product/legal decision.
- Full E2E browser flows remain for later QA PRs.
- Admin review queue UI remains for admin-console PR.
