# Diagnostics and Jobs Integrity Introspection

Generated at: `2026-05-17T22:05:40Z`

| Check | Value |
|---|---|
| Diagnostics router exists | True |
| Jobs module exists | True |
| Diagnostic integrity imported | False |
| Diagnostic submission validation calls | 0 |
| Mastery validation calls | 0 |
| ConsentService() empty constructor count in jobs | 1 |
| AsyncSessionLocal in jobs | True |

## Diagnostics functions

- `_require_item_bank_admin`
- `diagnostic_next_item`
- `diagnostic_respond`
- `get_diagnostic_items`
- `get_item_bank_coverage`
- `get_item_bank_item`
- `recover_diagnostic_session`
- `review_item_bank_item`
- `start_diagnostic_session`
- `submit_diagnostic`

## Job functions

- `_send_renewal_email`
- `expire_stale_diagnostic_sessions`
- `process_rlhf_feedback_batch`
- `redis_settings`
- `run_database_backup`
- `send_consent_renewal_reminders`
- `shutdown`
- `startup`
