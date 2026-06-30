# Auth Token Claims Repair Report

Generated at: `2026-05-17T20:36:18Z`

**Status:** implemented

| Item | Value |
|---|---|
| Auth router | `app/api_v2_routers/auth.py` |
| Canonical helper import inserted | True |
| Obvious raw email_encrypted writes patched | 0 |
| Inline create_access_token claim calls patched | 0 |

## Boundary

This batch centralizes token-claim semantics and blocks obvious raw email_encrypted persistence. Full AuthService extraction is a later boundary-consolidation batch.
