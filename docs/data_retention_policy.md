# Data retention policy

| Data category | Retention | Deletion/anonymisation trigger | Notes |
|---|---:|---|---|
| Guardian account | Account lifetime + legal/billing retention | Account closure or verified erasure request | Billing records may require statutory retention. |
| Learner profile | Account lifetime | Guardian erasure request | Display name is soft-deleted immediately before purge. |
| Diagnostic sessions | Account lifetime | Learner erasure execution | Educational progress data; not retained after learner erasure except audit tombstone. |
| Lessons and feedback | Account lifetime | Learner erasure execution | LLM prompts must use pseudonymous learner context only. |
| Consent records | Consent lifetime + audit retention | Superseded, withdrawn, or erased | Consent lifecycle remains auditable. |
| Audit events | Immutable operational/legal retention | Not erased by learner erasure | Payloads must not contain raw PII. |
| Analytics events | Aggregated/pseudonymous only | Retention window set by analytics processor | No raw learner names, emails, or identifiers. |
| Backups | 30 days by default | Backup expiry | Encrypted; restores must re-validate erasure and consent state. |

Retention parameters are configured operationally via environment and infrastructure settings. Production changes require compliance review and ADR update.
