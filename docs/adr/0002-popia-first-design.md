# ADR 0002: POPIA-First Design

## Status
Accepted

## Context
EduBoost handles learner-related personal information, educational diagnostics, generated learning plans, guardian/teacher relationships, and audit-sensitive operations. The architecture must minimise privacy risk before production data is introduced.

## Decision
EduBoost will treat POPIA compliance as a first-class architectural constraint rather than a post-processing concern.

- Consent state must be explicit and enforceable by backend dependencies or services.
- Learner-data access must be auditable.
- Data minimisation and purpose limitation must be considered for new schemas, logs, analytics events, prompts, and exports.
- Erasure, correction, restriction, and export workflows must remain compatible with schema evolution.
- AI prompts and telemetry must avoid unnecessary personal information.

## Consequences

- **Pros**: Lower compliance risk, clearer data ownership, safer AI workflows, stronger audit posture.
- **Cons**: More design ceremony for features that touch learner data, additional tests, and stricter release gates.
