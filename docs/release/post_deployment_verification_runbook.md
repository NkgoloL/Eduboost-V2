# EduBoost V2: Post-Deployment Verification Runbook

**Control ID**: `TSR-12.9`  
**Release Gate**: `RG-5`  
**Status**: Authoritative  
**Domain**: Operations / Release Engineering  

---

## 1. Scope & Execution Conditions

This runbook specifies the post-deployment smoke, migration, contract, and health probe verifications that must execute following any production/pilot artifact deployment.

---

## 2. Post-Deployment Verification Checklist

```
[ ] Step 1: Container & Health Probe Status
[ ] Step 2: Database Migration & Schema Drift Assertion
[ ] Step 3: Zero-PII Audit Log Verification
[ ] Step 4: OpenAPI Contract & Deprecation Header Assertion
[ ] Step 5: Fail-Closed Commercial Payment Check
[ ] Step 6: Critical Learner Journey Smoke Test
```

---

## 3. Step-by-Step Execution Instructions

### Step 1: Health & Readiness Probe Validation
Ensure all application services report `HTTP 200` on `/health` and `/ready`:
```bash
curl -f -s https://api.eduboost.local/health | jq .
curl -f -s https://api.eduboost.local/ready | jq .
```
*Expected*: `{"status": "healthy", "database": "connected", "redis": "connected", "version": "v2.0.0"}`

### Step 2: Database Migration Check
Verify zero drift between ORM models and live PostgreSQL schema:
```bash
alembic current
alembic check
```
*Expected*: No pending revisions, zero schema drift detected.

### Step 3: API Contract & Deprecation Headers Check
Query `/api/v1` routes and `/api/v2` routes to confirm RFC 8594 deprecation compliance:
```bash
curl -I -s https://api.eduboost.local/api/v1/auth/login
```
*Expected*: Headers contain `Deprecation: true` and `Sunset: Sat, 31 Dec 2026 23:59:59 GMT`.

### Step 4: Fail-Closed Billing Invariant Verification
Attempt live checkout initiation:
```bash
curl -s -X POST https://api.eduboost.local/api/v2/billing/checkout \
  -H "Authorization: Bearer <test-token>" \
  -H "Content-Type: application/json" \
  -d '{"plan": "premium"}'
```
*Expected*: `HTTP 403 Forbidden` with body `{"error": "BILLING_LOCKED_FAIL_CLOSED"}`.

### Step 5: Learner Journey Smoke Test
Execute end-to-end synthetic learner exercise completion:
```bash
pytest tests/integration/test_learner_journey_smoke.py -v
```
*Expected*: All critical journey assertions pass with exit code `0`.
