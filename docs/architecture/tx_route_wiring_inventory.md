# Transaction Route Wiring Inventory

Generated at: `2026-05-19T23:09:42Z`

**Status:** `production-route-transaction-wiring-not-proven`

| Domain | Route function | File | Line | Mutation candidate | Transaction marker | Status |
|---|---|---|---:|---:|---:|---|
| `auth` | `me` | `app/api_v2_routers/auth.py` | 83 | False | False | `read-or-nonmutation-route` |
| `auth` | `register` | `app/api_v2_routers/auth.py` | 89 | True | False | `route-transaction-wiring-not-proven` |
| `auth` | `login` | `app/api_v2_routers/auth.py` | 108 | False | False | `read-or-nonmutation-route` |
| `auth` | `create_dev_session` | `app/api_v2_routers/auth.py` | 126 | True | False | `route-transaction-wiring-not-proven` |
| `auth` | `refresh_token` | `app/api_v2_routers/auth.py` | 150 | False | False | `read-or-nonmutation-route` |
| `auth` | `list_sessions` | `app/api_v2_routers/auth.py` | 181 | False | False | `read-or-nonmutation-route` |
| `auth` | `logout` | `app/api_v2_routers/auth.py` | 189 | False | False | `read-or-nonmutation-route` |
| `auth` | `revoke_all_tokens` | `app/api_v2_routers/auth.py` | 218 | False | False | `read-or-nonmutation-route` |
| `popia` | `grant_consent` | `app/api_v2_routers/popia.py` | 102 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `deny_consent` | `app/api_v2_routers/popia.py` | 120 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `withdraw_consent` | `app/api_v2_routers/popia.py` | 138 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `renew_consent` | `app/api_v2_routers/popia.py` | 153 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `create_export_request` | `app/api_v2_routers/popia.py` | 173 | True | False | `route-transaction-wiring-not-proven` |
| `popia` | `create_erasure_request` | `app/api_v2_routers/popia.py` | 191 | False | False | `read-or-nonmutation-route` |
| `popia` | `cancel_erasure` | `app/api_v2_routers/popia.py` | 206 | False | False | `read-or-nonmutation-route` |
| `popia` | `create_correction_request` | `app/api_v2_routers/popia.py` | 223 | False | False | `read-or-nonmutation-route` |
| `popia` | `create_restriction_request` | `app/api_v2_routers/popia.py` | 238 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `get_diagnostic_items` | `app/api_v2_routers/diagnostics.py` | 45 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `submit_diagnostic` | `app/api_v2_routers/diagnostics.py` | 81 | True | False | `route-transaction-wiring-not-proven` |
| `diagnostics` | `get_item_bank_coverage` | `app/api_v2_routers/diagnostics.py` | 144 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `get_item_bank_item` | `app/api_v2_routers/diagnostics.py` | 156 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `review_item_bank_item` | `app/api_v2_routers/diagnostics.py` | 193 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `start_diagnostic_session` | `app/api_v2_routers/diagnostics.py` | 229 | True | False | `route-transaction-wiring-not-proven` |
| `diagnostics` | `recover_diagnostic_session` | `app/api_v2_routers/diagnostics.py` | 245 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `diagnostic_next_item` | `app/api_v2_routers/diagnostics.py` | 261 | False | False | `read-or-nonmutation-route` |
| `diagnostics` | `diagnostic_respond` | `app/api_v2_routers/diagnostics.py` | 293 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `generate_lesson` | `app/api_v2_routers/lessons.py` | 33 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `generate_lesson_stream` | `app/api_v2_routers/lessons.py` | 58 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `get_lesson` | `app/api_v2_routers/lessons.py` | 81 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `complete_lesson` | `app/api_v2_routers/lessons.py` | 102 | True | False | `route-transaction-wiring-not-proven` |
| `lessons` | `sync_lessons` | `app/api_v2_routers/lessons.py` | 119 | True | False | `route-transaction-wiring-not-proven` |

## Remaining boundaries

- route handlers must be wired through transactional application services
- live database transaction rollback behavior must be proven
- staging route smoke must be attached
- isolated rollback proof services do not prove production route wiring

## Interpretation

This inventory deliberately separates isolated rollback proof from production route wiring proof.
