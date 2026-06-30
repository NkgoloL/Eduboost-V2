# EduBoost V2 — Post-Baseline Remediation and Execution Roadmap

**Purpose:** Address the technical assessment concerns and move EduBoost V2 from repository-side production-readiness evidence to staging validation, controlled beta readiness, and eventual production-launch eligibility.

**Current baseline:** Repository-side production-readiness evidence for backlog domains 00–20 is broadly complete.  
**Current launch classification:** Production launch remains **NO-GO** pending runtime, legal, security, deployment, and manual approval evidence.

## Roadmap principles

1. Do not add more paper evidence where execution evidence is required.
2. Preserve claim discipline: repository-side evidence is not launch approval.
3. Resolve repository hygiene issues before staging validation.
4. Convert every manual/external/runtime blocker into an owned checklist item.
5. Treat controlled staging as the next validation target, not production launch.

## Phase 0 — Repository hygiene and source-of-truth cleanup

**Goal:** Remove ambiguity and stale checks before any staging/beta decision.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P0-001 | Fix `TODO.md` link for domain 01 filename drift. | Release owner | P1 | Pending |
| P0-002 | Reclassify raw `[ ]` items in backlog docs 00–04 and 20 as `[manual]`, `[external]`, `[legal]`, `[runtime]`, `[deployment]`, or `[verify]`. | Release owner | P1 | Pending |
| P0-003 | Audit duplicate domain wrapper scripts for domains 09–14. | Engineering | P1 | Pending |
| P0-004 | Update or retire `scripts/check_domain_09_testing_quality_evidence.py`, which expects `.github/workflows/frontend-e2e-opt-in.yml`. | Engineering | P1 | Pending |
| P0-005 | Add a canonical `production-readiness-all` Makefile target. | Engineering | P1 | Pending |
| P0-006 | Add or document a one-command dev/test bootstrap path. | Engineering | P2 | Pending |
| P0-007 | Confirm root `TODO.md` is either an index or a completion ledger; update language accordingly. | Release owner | P2 | Pending |

### Acceptance criteria

- No stale readiness script fails when intentionally included in canonical validation.
- Root TODO links resolve.
- Remaining backlog unchecked items are semantically classified.
- Canonical all-readiness target exists and is documented.

## Phase 1 — Clean CI and local reproducibility

**Goal:** Produce reproducible automated evidence from a clean environment.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P1-001 | Create clean virtual environment and install `requirements-dev.txt`. | Engineering | P1 | Pending |
| P1-002 | Run full unit test suite: `pytest -c pytest.ini tests/unit -q --no-cov`. | Engineering | P1 | Pending |
| P1-003 | Run production-readiness subset tests. | Engineering | P1 | Pending |
| P1-004 | Run OpenAPI drift checks. | Engineering | P1 | Pending |
| P1-005 | Run import/architecture boundary checks. | Engineering | P1 | Pending |
| P1-006 | Run frontend build checks where supported. | Frontend owner | P2 | Pending |
| P1-007 | Run frontend E2E or mock E2E checks where supported. | Frontend owner | P2 | Pending |
| P1-008 | Store CI/test output as release evidence under controlled path. | Release owner | P2 | Pending |

### Acceptance criteria

- Full unit test suite passes in clean environment.
- Canonical readiness target passes.
- Test output artifact is retained.
- Any failures have linked remediation tasks.

## Phase 2 — Staging environment readiness

**Goal:** Validate that the repository evidence maps to a working staging runtime.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P2-001 | Provision/verify staging environment. | Platform/DevOps | P1 | Pending |
| P2-002 | Configure staging secrets: database, Redis, app secret, CORS, telemetry, provider placeholders. | Platform/DevOps | P1 | Pending |
| P2-003 | Deploy backend to staging. | Platform/DevOps | P1 | Pending |
| P2-004 | Deploy frontend to staging. | Platform/DevOps | P1 | Pending |
| P2-005 | Run migrations against staging database. | Engineering | P1 | Pending |
| P2-006 | Run backend staging smoke tests. | Engineering | P1 | Pending |
| P2-007 | Run frontend staging smoke/E2E tests. | Frontend owner | P1 | Pending |
| P2-008 | Verify CORS, TLS, security headers, and API health endpoints. | Security/Engineering | P1 | Pending |
| P2-009 | Verify staging environment logs do not expose PII/secrets. | Security/Privacy | P1 | Pending |
| P2-010 | Record staging acceptance evidence. | Release owner | P1 | Pending |

### Acceptance criteria

- Staging deploy is healthy.
- Migrations run cleanly.
- Backend and frontend smoke tests pass.
- Security headers and CORS are verified.
- Staging evidence is retained.

## Phase 3 — Observability and operational execution evidence

**Goal:** Convert observability and operations contracts into live staging evidence.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P3-001 | Configure telemetry backend or staging observability sink. | Operations | P1 | Pending |
| P3-002 | Verify API metrics are emitted and visible. | Operations | P1 | Pending |
| P3-003 | Verify structured logs include request IDs / trace IDs. | Operations | P1 | Pending |
| P3-004 | Verify trace propagation across representative request path. | Operations | P2 | Pending |
| P3-005 | Configure dashboard for staging API overview. | Operations | P2 | Pending |
| P3-006 | Verify alert routing in non-paging/staging mode. | Operations | P2 | Pending |
| P3-007 | Conduct incident escalation tabletop. | Support/Ops | P1 | Pending |
| P3-008 | Test support contact / triage path. | Support | P1 | Pending |

### Acceptance criteria

- Logs, metrics, and traces are visible.
- Alert routing works in staging/non-paging mode.
- Incident/support procedures are rehearsed.
- Evidence is captured.

## Phase 4 — Backup, restore, and disaster-recovery execution

**Goal:** Replace repository-only DR evidence with staging execution evidence.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P4-001 | Verify backup job configuration for staging database. | Platform/DB owner | P1 | Pending |
| P4-002 | Execute backup dry-run. | Platform/DB owner | P1 | Pending |
| P4-003 | Execute isolated restore drill. | Platform/DB owner | P1 | Pending |
| P4-004 | Verify restore checksum / integrity. | Platform/DB owner | P1 | Pending |
| P4-005 | Run application smoke tests against restored target. | Engineering | P1 | Pending |
| P4-006 | Document observed RPO/RTO. | Release owner | P1 | Pending |
| P4-007 | Review rollback procedure and evidence. | Release owner | P1 | Pending |

### Acceptance criteria

- Backup dry-run succeeds.
- Restore drill succeeds in isolated environment.
- Application smoke test passes against restored target.
- RPO/RTO evidence is recorded.

## Phase 5 — Security, privacy, and legal verification

**Goal:** Convert internal security/privacy evidence into formal review/signoff readiness.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P5-001 | Conduct security review of auth/session/RBAC/object authorization posture. | Security owner | P1 | Pending |
| P5-002 | Conduct POPIA/privacy review of consent/data-rights flows. | Privacy/legal owner | P1 | Pending |
| P5-003 | Review data retention and deletion workflows. | Privacy/legal owner | P1 | Pending |
| P5-004 | Run dependency/security scan in CI. | Security owner | P1 | Pending |
| P5-005 | Run secret scan and confirm no committed secrets. | Security owner | P1 | Pending |
| P5-006 | Verify staging security headers. | Security owner | P1 | Pending |
| P5-007 | Decide whether penetration testing is required before beta or before GA. | Security/release owner | P1 | Pending |
| P5-008 | Record signoff or explicit non-signoff. | Release owner | P1 | Pending |

### Acceptance criteria

- Security review completed.
- POPIA/privacy review completed.
- Security scan outputs retained.
- Legal/security conditions are documented.
- Any non-signoff is treated as blocker.

## Phase 6 — Provider and external dependency verification

**Goal:** Track all external/manual dependencies before controlled beta.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P6-001 | Verify GitHub branch protection settings. | Release owner | P1 | Pending |
| P6-002 | Verify required CI checks are enforced. | Release owner | P1 | Pending |
| P6-003 | Verify CODEOWNERS/review protections. | Release owner | P2 | Pending |
| P6-004 | Decide billing provider status for beta; keep disabled unless approved. | Commercial owner | P1 | Pending |
| P6-005 | Verify notification provider status for beta. | Operations/support | P2 | Pending |
| P6-006 | Verify telemetry provider status for staging/beta. | Operations | P1 | Pending |
| P6-007 | Document all external/manual dependencies in final blocker register. | Release owner | P1 | Pending |

### Acceptance criteria

- External dependencies are explicitly closed, deferred, or marked not applicable.
- No repository-only evidence is treated as external approval.
- Required external dependencies are not open for beta decision.

## Phase 7 — Controlled beta readiness

**Goal:** Decide whether controlled beta can begin.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P7-001 | Confirm controlled beta product scope. | Product owner | P1 | Pending |
| P7-002 | Confirm beta cohort size, grade range, subject range, and consent path. | Product/privacy | P1 | Pending |
| P7-003 | Confirm support SLA and feedback intake process. | Support owner | P1 | Pending |
| P7-004 | Review known issues register. | Release/product owner | P1 | Pending |
| P7-005 | Review rollback plan. | Release owner | P1 | Pending |
| P7-006 | Conduct final beta go/no-go meeting. | Release owner | P1 | Pending |
| P7-007 | Record beta decision and evidence. | Release owner | P1 | Pending |

### Acceptance criteria

- Staging acceptance has passed.
- Legal/security/privacy/support reviews are complete or explicitly deferred with approval.
- Known issues are reviewed.
- Controlled beta decision is recorded.

## Phase 8 — Controlled beta execution

**Goal:** Run beta safely and collect post-beta evidence.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P8-001 | Enroll limited, consented beta cohort. | Product/support | P1 | Pending |
| P8-002 | Monitor technical health metrics. | Operations | P1 | Pending |
| P8-003 | Monitor support and feedback. | Support | P1 | Pending |
| P8-004 | Monitor privacy/security incidents. | Privacy/security | P1 | Pending |
| P8-005 | Maintain known issues register. | Product/engineering | P1 | Pending |
| P8-006 | Produce beta outcome report. | Product/release owner | P1 | Pending |
| P8-007 | Conduct post-beta retrospective. | Release owner | P1 | Pending |

### Acceptance criteria

- Beta evidence is captured.
- Defects and feedback are triaged.
- Post-beta review is completed.
- GA decision is based on evidence, not assumption.

## Phase 9 — GA / production-launch eligibility

**Goal:** Determine whether EduBoost V2 can move beyond beta.

| ID | Task | Owner | Priority | Status |
|---|---|---|---:|---|
| P9-001 | Review beta exit criteria. | Release/product owner | P1 | Pending |
| P9-002 | Confirm critical defects are zero or formally blocked. | Engineering | P1 | Pending |
| P9-003 | Confirm legal/privacy production approval. | Legal/privacy | P1 | Pending |
| P9-004 | Confirm security production approval. | Security owner | P1 | Pending |
| P9-005 | Confirm production deployment plan and rollback path. | Platform/release owner | P1 | Pending |
| P9-006 | Confirm backup/restore readiness for production. | Platform/DB owner | P1 | Pending |
| P9-007 | Confirm final release-blocker checklist. | Release owner | P1 | Pending |
| P9-008 | Record final production go/no-go. | Release owner | P1 | Pending |

### Acceptance criteria

- All release blockers closed or explicitly non-applicable.
- Required external/manual approvals complete.
- Production launch decision is recorded.
- Evidence bundle is retained.

## Canonical near-term command targets to add

Recommended Makefile targets:

```makefile
production-readiness-all:
	$(PYTHON) scripts/check_domain_01_repository_governance_ci_evidence.py
	$(PYTHON) scripts/check_domain_02_backend_api_contract_evidence.py
	$(PYTHON) scripts/check_domain_03_authentication_security_evidence.py
	$(PYTHON) scripts/check_domain_04_popia_consent_compliance_evidence.py
	$(PYTHON) scripts/check_database_persistence_production_readiness.py
	$(PYTHON) scripts/check_ai_llm_safety_caps_production_readiness.py
	$(PYTHON) scripts/check_diagnostics_assessment_production_readiness.py
	$(PYTHON) scripts/check_frontend_production_readiness.py
	$(PYTHON) scripts/check_billing_monetization_production_readiness.py
	$(PYTHON) scripts/check_notifications_communication_production_readiness.py
	$(PYTHON) scripts/check_observability_production_readiness.py
	$(PYTHON) scripts/check_ci_cd_deployment_production_readiness.py
	$(PYTHON) scripts/check_backup_restore_disaster_recovery_production_readiness.py
	$(PYTHON) scripts/check_testing_release_quality_gates_production_readiness.py
	$(PYTHON) scripts/check_security_posture_threat_modeling_production_readiness.py
	$(PYTHON) scripts/check_incident_response_operations_support_production_readiness.py
	$(PYTHON) scripts/check_documentation_adrs_claim_discipline_production_readiness.py
	$(PYTHON) scripts/check_beta_launch_staging_acceptance_production_readiness.py
	$(PYTHON) scripts/check_roadmap_after_production_readiness_baseline.py
	$(PYTHON) scripts/check_final_release_blocker_checklist.py
```

## Roadmap decision gates

| Gate | Required before | Current classification |
|---|---|---|
| Repository cleanup gate | Staging validation | Pending |
| Clean CI gate | Staging validation | Pending |
| Staging acceptance gate | Controlled beta | Pending |
| Legal/privacy gate | Controlled beta / production | Pending |
| Security gate | Controlled beta / production | Pending |
| DR restore gate | Production | Pending |
| Final release-blocker gate | Production | Pending |

## Final roadmap status

| Target | Status |
|---|---|
| Repository-side production-readiness baseline | Complete / Go |
| Repository hygiene cleanup | Pending |
| Clean CI evidence | Pending |
| Staging validation | Pending |
| Controlled private beta | Conditional pending gates |
| Public beta | No-go |
| Production launch | No-go |
