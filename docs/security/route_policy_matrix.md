---
title: "Route Policy Matrix"
status: current-evidence
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# Route Policy Matrix

**Status:** ✅ Current  
**Date:** 2026-06-12  
**Phase:** 8 (A.6)  
**Source:** Generated from `app/api_v2.py` router registry + `app/core/authorization.py` + `app/domain/roles.py`

This matrix documents every registered API route, its authentication requirement, required role, consent requirement, and the object-level authorization helper it calls. It is the machine-readable source for authorization boundary CI checks.

---

## Legend

| Symbol | Meaning |
|---|---|
| ✅ | Required / enforced |
| ❌ | Not required / not applicable |
| `guardian+` | guardian, admin |
| `teacher+` | teacher, admin |
| `any_auth` | any authenticated role |
| `admin` | admin only |
| `support+` | support_operator, admin |
| `auditor+` | compliance_auditor, admin |

---

## Operational Routes

| Route | Method | Auth | Role | Consent | Object-Auth Helper | Notes |
|---|---|---|---|---|---|---|
| `/health` | GET | ❌ | — | ❌ | — | Public health check |
| `/ready` | GET | ❌ | — | ❌ | — | Deep health probe |
| `/api/v2/health/deep` | GET | ❌ | — | ❌ | — | Alias for /ready |
| `/metrics` | GET | ❌ | — | ❌ | — | IP-restricted in prod (ADR-027) |
| `/__dev/slow_query` | GET | ❌ | — | ❌ | — | Dev only; returns 404 in production |
| `/docs` | GET | ❌ | — | ❌ | — | OpenAPI docs |
| `/redoc` | GET | ❌ | — | ❌ | — | ReDoc |
| `/` | GET | ❌ | — | ❌ | — | Root welcome |

---

## Authentication Routes (`/api/v2/auth/`)

| Route | Method | Auth | Role | Consent | Notes |
|---|---|---|---|---|---|
| `/auth/signup` | POST | ❌ | — | ❌ | Public signup |
| `/auth/login` | POST | ❌ | — | ❌ | Public login; rate-limited |
| `/auth/logout` | POST | ✅ | `any_auth` | ❌ | Revokes access + refresh token |
| `/auth/refresh` | POST | ❌ | — | ❌ | Refresh token in cookie; rate-limited |
| `/auth/me` | GET | ✅ | `any_auth` | ❌ | Returns current user claims |
| `/auth/forgot-password` | POST | ❌ | — | ❌ | Rate-limited (5 req/15 min/IP) |
| `/auth/reset-password` | POST | ❌ | — | ❌ | Token-based; rate-limited |
| `/auth/send-verification` | POST | ✅ | `any_auth` | ❌ | Resend email verification |
| `/auth/verify-email` | GET | ❌ | — | ❌ | Token-based email verification |
| `/auth/onboarding` | GET | ✅ | `any_auth` | ❌ | Read onboarding state |
| `/auth/onboarding/step` | PATCH | ✅ | `any_auth` | ❌ | Update onboarding step |
| `/auth/onboarding/profile` | PATCH | ✅ | `any_auth` | ❌ | Update learner profile |
| `/auth/privacy` | GET | ✅ | `any_auth` | ❌ | Read privacy settings |
| `/auth/privacy` | PATCH | ✅ | `any_auth` | ❌ | Update privacy settings |
| `/auth/privacy/request-export` | POST | ✅ | `any_auth` | ❌ | POPIA export request |
| `/auth/privacy/request-deletion` | POST | ✅ | `any_auth` | ❌ | POPIA erasure request |

---

## Learner Routes (`/api/v2/learners/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/learners/{learner_id}` | GET | ✅ | `guardian+`, `teacher+` | ✅ (active) | `can_view_learner` |
| `/learners/{learner_id}` | PUT | ✅ | `guardian+` | ✅ (active) | `can_update_learner` |
| `/learners/{learner_id}/profile` | GET | ✅ | `guardian+`, `teacher+` | ✅ (active) | `can_view_learner` |
| `/learners/{learner_id}/progress` | GET | ✅ | `guardian+`, `teacher+` | ✅ (active) | `can_view_learner` |

---

## Lesson Routes (`/api/v2/lessons/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/lessons/generate` | POST | ✅ | `guardian+` | ✅ (active) | `can_generate_lesson_for_learner` |
| `/lessons/{lesson_id}` | GET | ✅ | `guardian+`, `learner` | ✅ (active) | `can_view_learner` |
| `/lessons/{lesson_id}/stream` | GET | ✅ | `guardian+`, `learner` | ✅ (active) | `can_view_learner` |

---

## Diagnostic Routes (`/api/v2/diagnostics/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/diagnostics/start` | POST | ✅ | `guardian+`, `teacher+` | ✅ (active) | `can_start_diagnostic_for_learner` |
| `/diagnostics/submit` | POST | ✅ | `guardian+`, `teacher+` | ✅ (active) | `can_start_diagnostic_for_learner` |
| `/diagnostics/{session_id}` | GET | ✅ | `guardian+`, `teacher+` | ✅ (active) | `can_view_learner` |

---

## Study Plan Routes (`/api/v2/study_plans/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/study_plans/{learner_id}` | GET | ✅ | `guardian+`, `teacher+`, `learner` | ✅ (active) | `can_view_study_plan` |
| `/study_plans/{learner_id}` | POST | ✅ | `guardian+` | ✅ (active) | `can_update_learner` |

---

## Practice Routes (`/api/v2/practice/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/practice/session` | POST | ✅ | `guardian+`, `learner` | ✅ (active) | `require_active_consent` + learner write |
| `/practice/session/{id}/next-item` | GET | ✅ | `guardian+`, `learner` | ✅ (active) | Session ownership |
| `/practice/session/{id}/respond` | POST | ✅ | `guardian+`, `learner` | ✅ (active) | Session ownership |

---

## Gamification Routes (`/api/v2/gamification/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/gamification/profile/{learner_id}` | GET | ✅ | `guardian+`, `learner` | ✅ (active) | `can_view_learner` |
| `/gamification/award-xp` | POST | ✅ | `admin` | ❌ | Admin only |

---

## Parent Report Routes (`/api/v2/parents/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/parents/{learner_id}/report` | GET | ✅ | `guardian+` | ✅ (active) | `can_view_parent_report` |
| `/parents/{learner_id}/progress` | GET | ✅ | `guardian+` | ✅ (active) | `can_view_parent_report` |

---

## Billing Routes (`/api/v2/billing/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/billing/checkout` | POST | ✅ | `guardian+` | ❌ | `can_view_billing` |
| `/billing/webhook` | POST | ❌ | — | ❌ | Stripe signature verification |
| `/billing/status` | GET | ✅ | `guardian+`, `support+` | ❌ | `can_view_billing` |

---

## Consent / POPIA Routes (`/api/v2/popia/`)

| Route | Method | Auth | Role | Consent | Object-Auth Helper |
|---|---|---|---|---|---|
| `/popia/consent/grant` | POST | ✅ | `guardian+` | ❌ | `_enforce_popia_learner_write` |
| `/popia/consent/deny` | POST | ✅ | `guardian+` | ❌ | `_enforce_popia_learner_write` |
| `/popia/consent/withdraw` | POST | ✅ | `guardian+` | ❌ | `_enforce_popia_learner_write` |
| `/popia/consent/renew` | POST | ✅ | `guardian+` | ❌ | `_enforce_popia_learner_write` |
| `/popia/exports` | POST | ✅ | `guardian+` | ✅ (active) | `can_export_learner_data` |
| `/popia/erasure` | POST | ✅ | `guardian+` | ❌ | Guardian + admin only |
| `/popia/erasure/{id}/cancel` | POST | ✅ | `guardian+` | ❌ | Requester or admin only |
| `/popia/correction` | POST | ✅ | `guardian+` | ❌ | Learner write |
| `/popia/restriction` | POST | ✅ | `guardian+` | ❌ | Learner write |

---

## Onboarding Routes (`/api/v2/onboarding/`)

| Route | Method | Auth | Role | Consent | Notes |
|---|---|---|---|---|---|
| `/onboarding/status` | GET | ✅ | `any_auth` | ❌ | Returns onboarding step status |

---

## Admin / Content Factory Routes (`/api/v2/admin-content-factory/`)

| Route | Method | Auth | Role | Consent | Notes |
|---|---|---|---|---|---|
| `/admin-content-factory/*` | ALL | ✅ | `admin`, `content_reviewer` | ❌ | Admin/reviewer only |
| `/admin-etl/*` | ALL | ✅ | `admin` | ❌ | Admin only |

---

## Learner Content Routes (`/api/v2/learner-content/`)

| Route | Method | Auth | Role | Consent | Notes |
|---|---|---|---|---|---|
| `/learner-content/*` | GET | ✅ | `guardian+`, `learner` | ✅ (active) | Production content read |

---

## Audit Routes (`/api/v2/audit/`)

| Route | Method | Auth | Role | Consent | Notes |
|---|---|---|---|---|---|
| `/audit/events` | GET | ✅ | `admin`, `auditor+` | ❌ | Read-only audit log access |

---

## Public Routes Summary

Routes accessible without authentication (must have no learner data):

| Route | Justification |
|---|---|
| `/health` | Standard liveness probe |
| `/ready` | Readiness probe (no PII returned) |
| `/docs`, `/redoc` | OpenAPI documentation |
| `/auth/signup` | New user registration |
| `/auth/login` | Entry point |
| `/auth/forgot-password` | Password recovery (rate-limited) |
| `/auth/reset-password` | Token-based, no session required |
| `/auth/verify-email` | Token-based, no session required |
| `/auth/refresh` | Cookie-based; no bearer token required |
| `/billing/webhook` | Stripe webhook (HMAC verified) |

---

## CI Staleness Check

This file should be regenerated when new routers are added. To verify coverage:

```bash
python scripts/generate_route_inventory.py | diff - docs/security/route_policy_matrix_routes.txt
```

A CI gate in `.github/workflows/auth-boundary.yml` checks that every route in the OpenAPI spec has a corresponding entry in this matrix.

---

## References

- `app/core/authorization.py` — policy helper implementations
- `app/domain/roles.py` — role definitions and permissions
- `app/api_v2.py` — router registry
- Phase 8 execution plan §A.6
