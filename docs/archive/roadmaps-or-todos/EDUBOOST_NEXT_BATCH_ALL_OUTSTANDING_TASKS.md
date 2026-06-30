# EduBoost V2 — Next Batch: All Outstanding Tasks

**Branch:** `remediation/phase0-phase1`  
**Batch name:** `phase1-plus-all-outstanding`  
**Purpose:** Collapse all known remaining work into one execution batch, grouped by dependency and risk.

> This is intentionally large. It includes all remaining known tasks from the remediation track,
> but separates automatable engineering work from human-review/compliance work and later-phase
> product/scale work.

---

## 0. Current Accepted State

Completed / accepted:

- Phase 0 validation unblock: complete.
- T001–T005: pytest collection clean.
- T010: health contract aligned.
- T020–T023: Alembic head/forward upgrade baseline, with downgrade caveat.
- T030–T032: Alertmanager/promtool validation and observability CI.
- T040–T071: hardening intake triage, Python runtime ADR/alignment, docs freeze.
- T100–T105/T120–T122 security + debt baseline: complete, except runtime content filter remains gated by T050.
- T130–T131: authoritative coverage baseline.
- T130C/T130D: failures and xfails cleared.
- T133A/T135A/T136A: 60% coverage floor restored.
- T110C: POPIA export payload completeness.
- T112B: POPIA consent versioning.
- T111C: POPIA erasure workflow.
- T113: guardian consent withdrawal.
- T114–T116: POPIA compliance documentation.
- ADR-004: POPIADataRightsService authority documented.

Known current metrics:

- Coverage: 64.26%.
- Full collection: 2,834 tests collected.
- POPIA tests: 38 passed, 5 skipped.
- Xfails: 0.

---

# Batch Execution Order

## Batch 4A — Close Immediate P1 Residuals

### T111D — Deprecate or reconcile legacy `DataSubjectRightsService` erasure path

**Priority:** P1  
**Reason:** Two erasure paths exist. FastAPI v2 must have only one authoritative data-rights execution path.

**Scope:**

- Add explicit deprecation notice to `app/services/data_subject_rights_service.py`.
- Add module-level docstring stating:
  - `POPIADataRightsService` is authoritative for FastAPI v2.
  - `DataSubjectRightsService` is legacy/compatibility only.
  - No new v2 routes may call it.
- Add test proving v2 routers/services do not import `DataSubjectRightsService`.
- Optionally add runtime warning if the legacy service is instantiated.

**Acceptance criteria:**

```bash
.venv/bin/python -m pytest tests/unit/test_popia_service_authority.py --no-cov -v
.venv/bin/python -m pytest tests/popia --no-cov -v
```

---

### T022A — Validate Alembic upgrade against disposable PostgreSQL

**Priority:** P1  
**Reason:** `alembic upgrade head` previously required `DATABASE_URL`. New migrations were added for consent versioning and erasure request state.

**Scope:**

- Start disposable Postgres.
- Run `alembic upgrade head`.
- Confirm current revision equals latest head.
- Record evidence.
- Keep known downgrade-to-base enum issue tracked separately.

**Acceptance criteria:**

```bash
docker rm -f eduboost-migration-test || true
docker run -d --name eduboost-migration-test \
  -e POSTGRES_USER=eduboost_user \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=eduboost_test \
  -p 55433:5432 \
  postgres:16-alpine

export DATABASE_URL="postgresql+asyncpg://eduboost_user:devpassword@localhost:55433/eduboost_test"

.venv/bin/alembic heads
.venv/bin/alembic upgrade head
.venv/bin/alembic current
```

**Evidence file:**

```text
audits/migration/alembic_upgrade_postgres_20260528.md
```

---

### T022B — Decide rollback policy for Alembic downgrade limitation

**Priority:** P1, or P0 if downgrade is required for production rollback  
**Reason:** `alembic downgrade base` fails on PostgreSQL enum dependency cycles.

**Scope:**

- Document whether production rollback uses:
  1. Alembic downgrade, or
  2. restore-from-backup / forward-fix rollback.
- If Alembic downgrade is required: fix enum drop order / CASCADE handling.
- If not required: document backup-restore rollback as authoritative.

**Acceptance criteria:**

```text
docs/adr/ADR-005-database-rollback-policy.md
```

must state the supported rollback model.

---

## Batch 4B — Content Filter Decision and Runtime Enforcement

### T050 — Sign content filter decision

**Priority:** P0/P1 gate  
**Status:** Blocked on human reviewers.

**Required signers:**

- Security/Safety owner.
- POPIA/Privacy owner.
- Product owner.

**Options:**

- A: Implement runtime content filter now.
- B: Defer with signed risk acceptance and launch restriction.
- C: Remove from release scope with explicit rationale.

**Acceptance criteria:**

```text
audits/risk_acceptances/content_filter_deferral.md
```

or equivalent decision memo is signed/approved.

---

### T100 — Wire content filter middleware if T050 chooses implementation

**Priority:** P1  
**Depends on:** T050 Option A.

**Scope:**

- Implement or restore `app/core/content_filter.py` if absent.
- Register middleware in `app/api_v2.py`.
- Ensure middleware order is documented.
- Add tests proving blocked content returns safe 4xx.
- Add negative tests proving ordinary educational content passes.

**Acceptance criteria:**

```bash
.venv/bin/python -m pytest tests/security/test_content_filter.py --no-cov -v
.venv/bin/python -m pytest tests/smoke --no-cov -v
```

---

## Batch 4C — Coverage Recovery Beyond 64.26%

### T132 — Raise `app/core/` coverage

**Current:** approximately 75%.  
**Target:** greater than or equal to 90%.

**Scope:**

- Config validation tests.
- Middleware/error-envelope tests.
- Safety/content-policy utilities.
- Request ID/timing/header behavior tests.
- Runtime settings edge cases.

### T133 — Continue router coverage recovery

**Current:** approximately 61%.  
**Target:** greater than or equal to 80%.

**Scope:**

- Add contract tests for remaining low-coverage routers.
- Cover 401/403, 422, success response shape, OpenAPI inclusion, and dependency overrides.

### T134 — Raise services/domain coverage

**Targets:**

- `app.domain`: maintain greater than or equal to 85%.
- `app.services`: raise from about 54% to greater than or equal to 80%.

### T135 — Continue repository coverage

**Target:** greater than or equal to 75%.

### T136 — Restore long-term coverage gate

**Current floor:** 60%, currently satisfied at 64.26%.  
**Phase 1 target:** 80%.

**Scope:**

- Keep 60% enforced now.
- Add ratchet plan: 65%, 70%, then 80%.
- CI must fail below the current ratchet threshold.

---

## Batch 4D — Phase 1 Production Baseline Closure

### T114–T116 reviewer approval

**Status:** docs complete, human review pending.

**Scope:**

- Information Officer contact must be replaced with real approved contact before launch.
- Privacy Notice must be reviewed by Privacy/Legal/Information Officer.
- Breach Response Procedure must be reviewed by operations/security/privacy.

### Branch protection enforcement

**Related:** T141.

**Scope:**

- Apply branch protection in GitHub UI.
- Required checks:
  - collection-check,
  - migration-check,
  - observability-check,
  - security-scans,
  - openapi-contract,
  - coverage-gate.

---

# Phase 2 Outstanding Tasks — Operational Excellence

## T200–T205 — E2E suite

- Playwright setup.
- Isolated DB.
- Deterministic AI mocks.
- Learner onboarding E2E.
- Diagnostic E2E.
- Guardian/consent E2E.
- Data export/deletion E2E.
- CI reports.

## T210–T212 — Observability semantic validation

- Validate Prometheus rules against actual `/metrics` names.
- Validate Grafana dashboards in staging.
- Synthetic alert test through Alertmanager.

## T220–T221 — Disaster Recovery

- Full staging restore drill.
- RTO/RPO measured.
- Backup integrity verified.
- DR procedure published.

## T230–T233 — Performance and AI budget guardrails

- Load test baseline.
- Top 3 slow endpoints.
- Performance regression gate.
- Per-learner AI inference budget.

## T240 — Security posture focused review

- JWT.
- audit chain.
- rate limiting.
- circuit breakers.
- content filter.
- dependency failure paths.
- Zero unresolved High/Critical findings before Phase 3.

---

# Phase 3 Outstanding Tasks — Pedagogical Depth

## T300–T302 — CAPS alignment

- Implement CAPS alignment checker.
- Integrate into content ingestion.
- Audit existing catalogue.
- Quarantine misaligned content.

## T310–T312 — Diagnostic engine calibration

- Structured diagnostic logs.
- Calibration report.
- Theta instability detection.

## T320 — Plain-language progress reports

- Guardian/teacher readable.
- At least 70% comprehension in test group.

## T330–T331 — Accessibility and localisation

- WCAG 2.1 AA audit.
- Initial localisation: English, isiZulu, Sesotho, Afrikaans.

## T340–T342 — AI governance

- AI Learner Interaction Policy.
- Model update protocol.
- PII retention limit for LLM interactions.

---

# Phase 4 Outstanding Tasks — Equity and Scale

## T400–T406

- PWA/offline.
- IndexedDB answer queue.
- Data-saving mode.
- Low-end Android compatibility.
- Bulk learner provisioning.
- LTI 1.3.
- Zero-rating API documentation.

## T410

- AI bias audit by language, province, and school quintile.

---

# Phase 5 Outstanding Tasks — Impact and Governance

## T500–T502

- Transparency report template.
- Academic learning outcomes research partnership.
- Open-source adaptive engine and CAPS taxonomy, excluding learner data.

---

# Recommended Immediate Next Commit

Start with Batch 4A:

```text
phase1: close POPIA service authority and migration validation gaps
```

Then Batch 4B or 4C depending on whether content-filter sign-off is available.

---

# Stop Conditions

Stop and ask for human decision if:

- T050 content filter sign-off is unavailable.
- Information Officer contact is unknown.
- Privacy/Legal rejects Privacy Notice assumptions.
- Alembic downgrade is required as production rollback.
- Any erasure test suggests PII remains accessible after deletion.
- Any coverage improvement requires weakening assertions or adding broad skips.
