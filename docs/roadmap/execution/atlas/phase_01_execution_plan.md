# Phase 1 Corrective Execution Plan — Grounded LLM Generation

**Plan type:** Corrective remediation plan following implementation review  
**Date:** 2026-06-14  
**Status:** Executed; corrective verification complete; canonical merge pending  
**Phase status:** Verified Complete on feature branch; canonical merge pending  
**Sprint codename:** atlas  
**Source package:** `files.zip` SHA-256 `6b27b9259e2f8786fa533c3420e10210996fb2a91dba59fae201352e9062e7a3`

> This corrective plan does not retroactively cure the original start-gate breach. The supplied implementation began without an approved, complete four-artifact control set. This plan records and governs the remediation performed after review.

## Objective

Deliver a secure, grounded, durable batch-generation implementation in which:

1. only authenticated administrators may create, inspect, or cancel runs;
2. the server resolves approved source records rather than trusting caller-supplied text or provenance;
3. every provider call is bounded by timeout, normalized failure handling, fallback, and circuit breaking;
4. PII, unsafe content, malformed JSON, unknown fields, and schema drift fail closed;
5. every valid artifact has source, prompt, schema, provider, model, token, cost, and validation provenance;
6. pre-artifact validation failures can be persisted without violating database foreign keys;
7. generation executes through a registered durable ARQ job without silent inline fallback;
8. repeated runs do not collide on globally unique task idempotency keys; and
9. completion claims are supported by plan, report, evidence, and audit artifacts.

## Scope

### In scope

- `app/services/llm_provider.py`
- `app/services/content_schemas.py`
- `app/services/content_validator.py`
- `app/services/safety_filter.py`
- `app/services/batch_generation.py`
- `app/services/content_generation/source_context.py`
- `app/jobs/batch_generation_job.py`
- `app/api_v2_routers/generation.py`
- `app/models/content_factory.py`
- `app/modules/jobs.py`
- `app/api_v2.py`
- Alembic migration for task-linked validation reports
- Phase 1 unit, hardening, router, worker, migration, and optional PostgreSQL tests
- Phase 1 implementation report, evidence pack, and independent audit report

### Out of scope

- Live calls to commercial LLM providers
- Production deployment
- Changes to the repository-wide `/api/v2` and `/v2` dual-prefix policy
- Creation of a disposable PostgreSQL service in this execution environment

## Findings-to-work mapping

| ID | Review concern | Corrective work | Mandatory verification |
|---|---|---|---|
| P1-01 | Logging crashes failure paths | Use Structlog consistently | Malformed, safety, fallback and circuit tests pass |
| P1-02 | Caller-controlled source provenance | Remove source text from request; server resolves approved rows | Strict request-schema and source-resolution tests |
| P1-03 | Missing admin authorization / spoofable actor | Require `AuthContext` admin and derive actor from token | Router dependency inspection and route tests |
| P1-04 | Router import/registration failure | Use `get_db`; register router in canonical runtime | Module and full-app import evidence |
| P1-05 | Invalid validation-report FK | Add nullable `task_id`, nullable `artifact_id`, one-subject check | Migration graph and PostgreSQL constraint tests |
| P1-06 | Red Phase 1 suite | Fix implementation and expand regressions | All non-environment-gated tests pass |
| P1-07 | ARQ job unregistered / silent inline fallback | Register job; queue fail returns 503; worker resolves sources | Worker registry and fail-closed queue test |
| P1-08 | Mock-only persistence proof | Add disposable PostgreSQL integration tests | Run under `PHASE1_TEST_DATABASE_URL` before closure |
| P1-09 | Provider timeout/fallback incomplete | Router timeout and generic exception normalization | Timeout, generic failure, and chain-order tests |
| P1-10 | Global task idempotency collision | Scope key by unique run and source snapshot | Repeated-run key test |
| P1-11 | Incorrect run state and stale locks | Reclaim expired running tasks; terminal status reflects blocks/skips | Engine status tests |
| P1-12 | Schema silently ignores extra fields | Strict Pydantic models; schema version is `ClassVar` | Strict-schema regression tests |
| P1-13 | Unsafe keyword inflection gap | Expand child-safety patterns | Violence-inflection test |
| P1-14 | Incomplete control set | Produce report/evidence/audit | Four-artifact closure check |

## Work packages

### WP1 — Provider and logging hardening

- Normalize all logging to structured logger calls.
- Add router-level timeout enforcement.
- Convert unexpected provider exceptions to retryable `ProviderError` behavior.
- Keep configured secondary providers as fallbacks.
- Restrict deterministic provider to test environments.
- Fail closed when no provider is configured.

### WP2 — Strict schemas and safety

- Set `extra="forbid"` and `strict=True` on generated payload models.
- Make schema versions class metadata.
- Reject duplicate options and out-of-range answer indices.
- Expand violence inflection patterns.
- Preserve redacted-only safety evidence.

### WP3 — Grounded source control and admin API

- Remove raw source text and `requested_by` from the request contract.
- Resolve source rows by scope, CAPS reference, and optional chunk IDs.
- Require admin authentication on every generation endpoint.
- Enforce provenance again inside the engine.
- Register the router in `app.api_v2`.

### WP4 — Durable execution and state correctness

- Register `generate_content_batch` in `WorkerSettings.functions`.
- Pass only run identity through the queue.
- Resolve persisted source references in the worker.
- Return HTTP 503 and mark `enqueue_failed` when ARQ is unavailable.
- Reclaim expired running locks within maximum-attempt bounds.
- Distinguish `completed`, `completed_with_errors`, and `no_work`.

### WP5 — Persistence and transaction integrity

- Support task-linked validation reports before artifact creation.
- Add database check constraint requiring an artifact or task subject.
- Persist valid artifact, sources, validation report, and task completion in one transaction.
- Roll back before recording unexpected failure state.
- Store source snapshot hash and complete provenance fields.

### WP6 — Verification and controls

- Retain and repair original tests.
- Add hardening regressions.
- Add disposable-PostgreSQL constraint tests plus a self-contained PostgreSQL 16 Compose verification command.
- Verify migration graph.
- Verify router and worker registration.
- Generate implementation report, evidence pack, and audit report.

## Start and closure gates

### Corrective start gate

- [x] Review findings documented.
- [x] Scope and affected paths identified.
- [x] No live learner or production data used.
- [x] Deterministic provider used for tests.
- [x] Original source archives hashed.

### Closure gate

- [x] Phase 1 unit/hardening suite passes in available environment.
- [x] Release-blocking Ruff subset passes.
- [x] Migration graph is linear with the new head.
- [x] Generation router imports and is registered in the full FastAPI runtime.
- [x] ARQ generation job is registered.
- [x] Implementation report completed.
- [x] Evidence pack completed for available checks.
- [x] Corrective audit completed.
- [x] Disposable PostgreSQL tests pass against migrated PostgreSQL.
- [ ] Canonical Python 3.12.3 CI run passes on the merge commit.
- [ ] Changes are merged into the canonical branch.

**Completion rule:** Phase 1 corrective verification is complete. Canonical merge and merge-commit CI remain pending until the phase lands on the canonical branch and is re-audited there.
