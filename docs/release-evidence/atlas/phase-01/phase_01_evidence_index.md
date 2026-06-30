# Phase 1 Corrective Evidence Pack

**Evidence date:** 2026-06-14  
**Evidence status:** Complete and verified on PostgreSQL and Python 3.12.3  
**Sprint codename:** atlas  
**Base source archive SHA-256:** `255b2f5a57445207bd4e70d69055742dbfb2fa806f807b2ed5974e6cf0fd3630`  

## 1. Environment identity

| Field | Value |
|---|---|
| Operating environment | Local development / test environment |
| Python | 3.12.3 (venv) |
| pytest | 8.2.1 |
| Ruff | 0.4.4 |
| Database | PostgreSQL 16 (disposable Docker container) |
| Live LLM providers | Not invoked (DeterministicProvider used) |

## 2. Criterion-to-evidence traceability

| Criterion | Evidence | Result |
|---|---|---|
| EC-01 strict typed content | `test_content_validator.py`, `test_phase1_hardening.py` | Pass |
| EC-02 invalid/unsafe output rejected | validator, safety, batch tests | Pass |
| EC-03 source/prompt/schema attribution | engine code, strict request test, source tests | Pass |
| EC-04 timeout and fallback | provider and hardening tests | Pass |
| EC-05 PII/child-safety fail closed | safety and engine tests | Pass |
| EC-06 privacy-safe token/cost telemetry | batch telemetry test and telemetry dict | Pass |
| EC-07 complete deterministic run | batch engine tests, verify_phase1_postgres.sh | Pass |
| Admin-only generation API | route dependency and request tests | Pass |
| Durable execution | worker registry and queue-failure tests | Pass |
| Validation-report FK design | model/migration tests, postgres integration tests | Pass |
| Migration graph | `scripts/verify_migration_graph.py` | Pass |

## 3. Commands and results

### 3.1 Test suite

```text
$ PATH=".venv/bin:$PATH" ./scripts/verify_phase1_postgres.sh
...
97 passed in 0.98s
20260614_0900_p1_validation (head)
```

### 3.2 Full Phase 1 Ruff check

```text
$ ruff check <all Phase 1 Python files and tests>
All checks passed!
```

### 3.3 Migration graph

```text
$ python scripts/verify_migration_graph.py
Migration graph OK: 35 revisions, head=20260614_0900_p1_validation
```

### 3.4 Router and worker module verification

```text
generation_router_prefix=/admin/generation
generation_route_count=4
generation_job_registered=True
```

### 3.5 Full FastAPI runtime registration

```text
router_registered=True
generation_paths=['/api/v2/admin/generation/runs',
'/api/v2/admin/generation/runs/{run_id}',
'/api/v2/admin/generation/runs/{run_id}/cancel',
'/api/v2/admin/generation/runs/{run_id}/tasks',
'/v2/admin/generation/runs',
'/v2/admin/generation/runs/{run_id}',
'/v2/admin/generation/runs/{run_id}/cancel',
'/v2/admin/generation/runs/{run_id}/tasks']
```

## 4. Test-accounting declaration

| Result type | Count |
|---|---:|
| Passed | 97 |
| Failed | 0 |
| Skipped | 0 |
| Xfailed | 0 |
| Collection errors | 0 |

## 5. Security and privacy evidence

- Raw source text is not accepted from the API caller.
- Actor identity is derived from authenticated admin context.
- Queue payload does not contain source text.
- Telemetry does not include prompts or generated content.
- PII and unsafe-content evidence stores categories and redacted excerpts, not full matches.
- Invalid generated content is not stored as a learner-facing artifact.
- Source and generated-output checks occur before provider and persistence boundaries respectively.

## 6. Evidence custodian declaration

The evidence above accurately represents commands executed and verified in the local target environment.
