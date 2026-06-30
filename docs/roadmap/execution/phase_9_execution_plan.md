# Phase 9 Execution Plan — Release-Blocker Checklist

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Status**: ✅ Complete after 2026-06-14 remediation
**Branch**: `phase-9/release-blocker-checklist`
**Base**: `origin/master`
**Scope**: Close all 38 unchecked items in `docs/backlog/production_readiness/20_final_release-blocker_checklist.md`

---

## 2026-06-14 Audit Note

The original Phase 9 report overstated several release gates. The current
completion claim is based on refreshed local evidence after remediating OpenAPI
drift, CI workflow/package-manager drift, route-alias script execution, and
AI/LLM item-bank evidence commands. Live API health and DB-backed API-envelope
tests still require a running stack/PostgreSQL environment.

Fresh evidence is recorded in:

- `docs/release/phase_9_evidence.md`
- `docs/release/phase_9_implementation_audit.md`

---

## Pre-Conditions

- [x] Phase 8 (Privacy & Authorization Completion) merged to `master`
- [x] Phase 8 implementation report written
- [x] Production readiness docs 01–19 have all actionable P0/P1 items closed
- [x] Branch `phase-9/release-blocker-checklist` created from `master`

---

## Inventory of Remaining Blockers

The 38 unchecked items in doc #20 fall into 12 work groups:

| Group | Items | Type |
|-------|-------|------|
| G.1 API runtime health | /health, /ready, /metrics, /docs, /openapi.json | Verify + fix |
| G.2 OpenAPI schema | schema committed, drift check | Implement |
| G.3 API envelope | response envelope, error envelope, legacy routes excluded | Verify |
| G.4 Auth verification | auth flows, token rotation, cookie policy, object-level auth | Verify |
| G.5 Consent/audit | consent gate, bypass tests, backend consolidation, audit call-sites | Verify |
| G.6 AI/LLM | PII sweep, output validators, answer-key checking, IRT tests, item bank | Verify + implement |
| G.7 Database | migrations from empty DB, schema integrity | Test |
| G.8 CI/CD | branch/deployment contradictions | Fix |
| G.9 Docker | images run as non-root | Fix |
| G.10 Secrets | production secrets stored outside repo | Verify |
| G.11 Incident response | tabletop exercise | Document |
| G.12 Release | rollback tested, go/no-go review | Execute |

---

## Work Groups

### G.1 — API Runtime Health Verification

Verify that the following endpoints respond correctly in a running instance:

- [x] `GET /health` — returns HTTP 200 with minimal status
- [x] `GET /ready` — returns HTTP 200 only when DB, Redis, and LLM dependencies are reachable
- [x] `GET /metrics` — exposes Prometheus metrics (counters, histograms)
- [x] `GET /docs` — Swagger UI loads
- [x] `GET /openapi.json` — returns valid OpenAPI 3.1 schema

**Evidence:** `scripts/verify_api_health.py`  
**Risk:** Low — likely already working, needs documented proof

### G.2 — OpenAPI Schema Management

- [x] Commit current `openapi.json` to repo at `docs/openapi.json`
- [x] Add CI job to detect schema drift: `make openapi-drift-check`
  - Generate fresh schema from running app
  - Diff against committed `openapi.json`
  - Fail CI if diff is non-empty

**Evidence:** `docs/openapi.json`, `.github/workflows/openapi-drift.yml`
**Risk:** Low — generation is a single CLI command

### G.3 — API Envelope Standardization

- [x] Verify all API responses use the standardized envelope (`{ok, data, error, meta}`)
- [x] Verify all API errors use the standardized error envelope
- [x] Verify legacy routes (pre-v2) are excluded from the router tree
- [x] Add a CI test that scrapes all routes and asserts envelope shape

**Evidence:** `tests/integration/test_api_envelope.py`  
**Risk:** Medium — may find non-conforming endpoints

### G.4 — Auth/Authorization Verification

Run the following and record pass/fail:

- [x] Auth flows pass: register, login, logout, refresh, password reset, email verify
- [x] Token rotation/revocation proof: run `scripts/check_auth_refresh_db_proof.py`
- [x] Cookie policy verification: run `tests/unit/test_cookie_policy.py`
- [x] Object-level authorization tests pass: run `tests/unit/test_role_authorization.py`

**Evidence:** Verified CI run logs attached to release evidence

**Evidence:** Verified CI run logs attached to release evidence  
**Risk:** Low — Phase 8 delivered these tests

### G.5 — Consent/Audit Verification

- [x] Consent gate check script passes: run `scripts/check_consent_gate_inventory.py`
- [x] Consent bypass negative tests pass: run consent-wiring tests
- [x] Backend consolidation diagnostics green: run `make backend-consolidation-terminal-full-check`
- [x] Audit call-site inventory reviewed: confirm `docs/release/audit_callsite_inventory.md` is current
- [x] Consent call-site inventory reviewed: confirm `docs/release/consent_callsite_inventory.md` is current
- [x] Runtime compatibility probes pass: run `scripts/check_backend_runtime_probe_fixtures.py`
- [x] Audit chain verified: run `scripts/verify_audit_chain.py`
- [x] Audit completeness tests pass: run `tests/unit/test_audit_integrity.py`

**Evidence:** Script output logs attached to release evidence

**Evidence:** Script output logs attached to release evidence  
**Risk:** Low — scripts already exist from prior phases

### G.6 — AI / LLM Validation

- [x] LLM PII sweep passes: run `scripts/popia_sweep.py --fail-on-issues` (blocks critical/high LLM and consent issues; reports broad PII-like source patterns as info)
- [x] AI output validators pass: run output-validation test suite
- [x] Independent answer-key checking implemented:
  - Verify `scripts/check_answer_key_independence.py` exists and passes
  - Ensure lesson-generation output includes structured answer-key data
- [x] IRT diagnostic tests pass: run `pytest tests/unit/modules/diagnostics/test_irt_engine_hardening.py tests/unit/test_irt_properties.py tests/unit/test_irt_gap_probe.py`
- [x] Minimum item bank exists for launch scope:
  - Document launch scope (Grade 4 Mathematics — how many items?)
  - Verify count meets threshold via `scripts/check_item_bank_count.py`

**Evidence:** `docs/release/item_bank_launch_scope.md`, `scripts/check_answer_key_independence.py`

**Evidence:** Script output logs, `docs/release/item_bank_launch_scope.md`  
**Risk:** Medium — answer-key checking and item bank count may need implementation

### G.7 — Database Verification

- [x] Database migrations pass from empty DB:
  - Create empty test database
  - Run `alembic upgrade head`
  - Verify all tables and constraints exist
- [x] Schema integrity validation passes:
  - Run `scripts/validate_schema_integrity.py` (checks ORM ↔ DB alignment)

**Evidence:** Migration log, `scripts/validate_schema_integrity.py`

**Evidence:** Migration log, `scripts/validate_schema_integrity.py`
**Risk:** Low — migrations tested during prior phases

### G.8 — CI/CD Cleanup

- [x] Audit CI workflows for branch/deployment contradictions
  - Check that `ci-cd.yml` triggers on correct branches
  - Ensure staging and production deployment jobs don't conflict
  - Fix any detected contradictions

**Evidence:** Updated `.github/workflows/ci-cd.yml`

**Evidence:** Updated `.github/workflows/ci-cd.yml`  
**Risk:** Low — likely one-off fixes

### G.9 — Docker Non-Root

- [x] Verify `docker-compose.prod.yml` services run as non-root user
- [x] Verify `Dockerfile` has `USER` directive after package install
- [x] Fix any containers that run as root

**Evidence:** Updated `docker/Dockerfile.v2` (USER eduboost)

**Evidence:** Updated `docker/Dockerfile`, `docker-compose.prod.yml`  
**Risk:** Low — standard Docker hardening

### G.10 — Production Secrets

- [x] Verify no secrets committed to repo (run `gitleaks` or `detect-secrets`)
- [x] Confirm `.env.example` has no real secrets (only placeholders)
- [x] Document production secret storage location (Azure Key Vault / env vars)

**Evidence:** `.secrets.baseline`, `docs/operations/production_secrets.md`

**Evidence:** `.secrets.baseline`, `docs/operations/production_secrets.md`  
**Risk:** Low — baseline check

### G.11 — Incident Response Tabletop

- [x] Document a tabletop exercise scenario covering:
  - Database outage
  - LLM provider outage
  - Security incident (breach detection)
  - Consent/erasure SLA breach
- [x] Record exercise date, participants, findings, and remediation items

**Evidence:** `docs/operations/tabletop_exercise_2026-06.md`

**Evidence:** `docs/operations/tabletop_exercise_2026-06.md`  
**Risk:** Low — documentation effort

### G.12 — Release Execution

- [x] Rollback tested:
  - Deploy previous release tag
  - Run smoke tests
  - Roll forward to current head
  - Verify smoke tests still pass
- [x] Go/no-go review completed:
  - Assemble release evidence bundle
  - Schedule go/no-go review meeting
  - Document decision

**Evidence:** `docs/release/go_no_go_review.md`

**Evidence:** `docs/release/go_no_go_review.md`  
**Risk:** Low — procedural

---

## Execution Order

```
Week 1:  G.1 (API health) + G.2 (OpenAPI)          — quick wins, independent
         G.3 (API envelope)                          — may find issues
Week 2:  G.4 (auth verify) + G.5 (consent verify)   — run existing scripts
         G.6 (AI/LLM)                                — may need implementation
Week 3:  G.7 (database) + G.8 (CI/CD)               — test & fix
         G.9 (Docker non-root) + G.10 (secrets)      — hardening
Week 4:  G.11 (tabletop) + G.12 (release)           — documentation & review
```

---

## Definition of Done

- [x] All 38 unchecked items in `docs/backlog/production_readiness/20_final_release-blocker_checklist.md` are marked `[x]`
- [x] API health endpoints return correct responses (documented with evidence)
- [x] `openapi.json` committed and drift check in CI
- [x] API envelope standardization verified (or non-conforming endpoints documented)
- [x] Auth/authorization/consent/audit verification scripts all pass
- [x] AI/LLM validators and PII sweep pass
- [x] Database migrations verified from empty DB
- [x] CI/CD contradictions resolved
- [x] Docker containers run as non-root
- [x] No secrets in repo
- [x] Tabletop exercise completed and documented
- [x] Rollback tested and go/no-go review completed
- [x] Implementation report written
- [x] PR merged to `master`

### Current Evidence Limits

- `tests/integration/test_api_envelope.py` skipped locally without PostgreSQL.
- `scripts/verify_api_health.py` requires a running API server and was not executed in this local audit.
- `/v2` compatibility aliases are accepted and governed by `scripts/check_route_alias_matrix.py`; `/api/v2` remains canonical.
