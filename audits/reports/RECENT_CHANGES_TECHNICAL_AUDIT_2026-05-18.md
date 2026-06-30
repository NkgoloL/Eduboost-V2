# EduBoost V2 Recent Changes Technical Audit

Date: 2026-05-18
Repository: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2`
Branch audited: `codex/production_readiness`
Audit focus: recent backend/core changes after the core technical audit, with emphasis on auth, POPIA consent, diagnostics, jobs, service boundaries, security, and runtime proof.

## Executive summary

The recent changes materially reduce several high-risk issues identified in the core technical audit. The strongest improvements are in auth router repository boundary enforcement, POPIA router dependency layering, lesson object authorization, and immediate runtime blocker repair checks. The branch is clean and synced with origin at the time of audit.

The work should not yet be treated as full audit closure. Several changes are structurally promising but are not runtime-proven. Some verification scripts and unit contracts are stale or contradictory, and at least two concrete runtime risks remain: the ARQ worker module cannot import in the current environment because `arq` is not pinned/installed, and the JWT keyring fallback can ignore the configured `settings.JWT_SECRET` and sign with a development fallback secret.

## Validation performed

Commands run from the repository root:

```bash
python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/modules app/services app/core scripts
python3 -m ruff check app/api_v2_routers/auth.py app/services/auth_application_service.py app/services/auth_lifecycle_impl.py app/services/jwt_keyring.py app/api_v2_routers/popia.py app/api_v2_routers/diagnostics.py app/modules/jobs.py --select F821,F401,F811,E402
PYTHONPATH=. python3 scripts/check_runtime_blockers_after_followup_audit.py
PYTHONPATH=. lint-imports --config .importlinter
pytest -c pytest.ini tests/unit/test_runtime_blockers_after_followup_audit.py -q --no-cov --tb=short
```

Results:

- Compileall passed.
- Focused Ruff passed.
- Runtime blocker repair check passed.
- Import-linter contracts passed: 3 kept, 0 broken.
- Runtime blocker unit slice passed: 6 passed.

Additional focused checks:

- `scripts/check_auth_service_ownership.py` passed.
- `scripts/check_auth_http_success_scope.py` passed, but integration tests were skipped.
- `scripts/check_popia_consent_lifecycle_repair.py` passed.
- `scripts/check_lesson_object_authorization_repair.py` passed.
- `scripts/check_auth_db_lifecycle_proof.py` passed, but transactional tests were skipped.

Failures and concerns:

- Focused audit unit slice had 2 failures:
  - `tests/unit/test_auth_router_boundary_contracts.py::test_auth_boundary_scripts_run`
  - `tests/unit/test_diagnostics_jobs_integrity_contracts.py::test_jobs_module_does_not_construct_consent_service_without_dependencies`
- `scripts/check_auth_lifecycle_method_extraction.py` failed because it expects preserved legacy helper names that were removed by later service extraction work.
- `scripts/check_diagnostics_jobs_integrity.py` failed because it still expects `AsyncSessionLocal` and `ConsentRepository` text inside `app/modules/jobs.py`, even though the implementation moved this work to `app/services/job_dependency_factory.py`.
- `python3 -c "import app.modules.jobs"` failed with `ModuleNotFoundError: No module named 'arq'`.
- JWT keyring proof showed `settings.JWT_SECRET` configured, while `current_jwt_signing_key()` returned `dev-insecure-secret-change-me` when keyring-specific environment variables were absent.

## Closure matrix

| Audit area | Current status | Assessment |
|---|---:|---|
| Auth router direct repository boundary | Mostly addressed | Main auth lifecycle routes now delegate through `AuthApplicationService`; import-linter keeps the router/repository boundary. |
| Auth lifecycle service ownership | Partially addressed | Router delegation exists, but lifecycle methods are monkey-patched onto `AuthApplicationService`; ownership is transitional rather than clean. |
| Auth refreshed token learner scope | Addressed structurally | Refresh reloads `guardian_learner_ids`; HTTP success and DB lifecycle proof scripts pass, but some integration tests were skipped. |
| Pydantic forward ref runtime blocker | Addressed | Removal of problematic future annotations and auth import checks pass. |
| JWT rotation | Partially addressed with new regression risk | Keyring helper exists and `kid` support is present, but fallback secret resolution is unsafe if only `JWT_SECRET` is configured. |
| POPIA router repository boundary | Mostly addressed | Router uses dependency layer and canonical consent adapter; import-linter contract passes. |
| POPIA lifecycle runtime shape | Not closed | Adapter may fall back to revoke methods that return `int` while routes declare `ConsentRecord`. Needs HTTP/runtime proof. |
| Lesson object authorization | Mostly addressed | Lesson read/write/sync paths invoke object authorization helpers and repair check passes. Broad dynamic fallbacks remain. |
| Diagnostics submission integrity | Partially addressed | Batch submit rejects empty/duplicate payloads, but adaptive session served-item binding is not wired into route handlers. |
| ARQ consent reminder job symbols | Partially addressed | Missing job symbols are repaired, but `app.modules.jobs` cannot import because `arq` is missing from pinned dependencies. |
| Architecture boundary policy | Improved | Import-linter contracts exist and pass. The ignore list is still broad and should be reduced over time. |
| Duplicate service/repository families | Not closed | Compatibility adapters remain; canonical ownership is still mixed across `app/services`, `app/modules`, and repository facades. |
| Evidence quality | Mixed | Many proof artifacts exist, but several scripts/tests encode stale or contradictory expectations. |

## Detailed findings

### 1. Auth router boundary improved, but the service is still transitional

Evidence:

- `app/api_v2_routers/auth.py` delegates register/login/dev-session/refresh to `AuthApplicationService`.
- `app/services/auth_application_service.py` defines a repository bundle and service facade.
- `app/services/auth_lifecycle_impl.py` contains the moved lifecycle implementations.

Risk:

- `AuthApplicationService` receives lifecycle methods through assignment at module bottom:
  - `AuthApplicationService.create_dev_session = _auth_service_create_dev_session`
  - `AuthApplicationService.login = _auth_service_login`
  - `AuthApplicationService.refresh = _auth_service_refresh`
  - `AuthApplicationService.register = _auth_service_register`
- The route still passes both `auth_service` and `auth_runtime`; the service is not fully owning its runtime dependencies.

Required closure:

- Move lifecycle methods into the class directly.
- Remove method monkey-patching.
- Make the service own or explicitly receive a typed dependency bundle.
- Convert stale helper-preservation checks into behavioral service/route tests.

### 2. JWT keyring introduces rotation support but has an unsafe fallback

Evidence:

- `app/services/jwt_keyring.py` parses keyring formats and supports current/previous keys.
- `app/core/security.py` signs and decodes through the keyring.

Risk:

- `_legacy_secret()` checks `JWT_SECRET_KEY`, `SECRET_KEY`, and `ACCESS_TOKEN_SECRET_KEY`, but not `settings.JWT_SECRET`.
- In the audited environment, `settings.JWT_SECRET` had a configured value while `current_jwt_signing_key()` returned `dev-insecure-secret-change-me`.

Required closure:

- Align fallback with `settings.JWT_SECRET` or require `JWT_KEYRING`/`JWT_SECRET_KEY` explicitly in production.
- Add a regression test for a `JWT_SECRET`-only environment.
- Add a production startup guard that refuses development fallback secrets.

### 3. POPIA lifecycle wiring is safer but not response-contract proven

Evidence:

- POPIA router now calls `get_canonical_consent_service`.
- `POPIAConsentLifecycleAdapter` bridges method names and argument names.
- Lifecycle functions enforce learner write access and derive actor id from authenticated user.

Risk:

- The canonical module consent service has `grant`, `revoke`, and `renew`; it does not expose all legacy domain lifecycle shapes.
- Adapter fallback from `deny`/`withdraw` to revoke can return `int`, while POPIA routes declare `response_model=ConsentRecord`.
- Static checks validate wiring presence, not actual HTTP response shape.

Required closure:

- Add canonical `deny` and `withdraw` behavior to the canonical consent service, or make the router response model match canonical outputs.
- Add integration tests for grant, deny, withdraw, and renew with real response validation.
- Verify audit events for each lifecycle transition.

### 4. Diagnostics integrity remains partial

Evidence:

- `submit_diagnostic` now calls `validate_diagnostic_submission_payload(body, require_items=True)`.
- `app/services/diagnostic_session_integrity.py` exists.

Risk:

- Adaptive session routes do not call `validate_session_served_item_binding`.
- `diagnostic_next_item` accepts arbitrary `caps_ref` from the query instead of binding it to recovered session state.
- `diagnostic_respond` accepts any item present in the item bank, not necessarily a served item for the session.

Required closure:

- Persist served item ids or reconstruct them from session state.
- Reject responses for items not served in the session.
- Reject mismatched `caps_ref` against session `caps_ref`.
- Add negative integration tests for cross-session and cross-caps item injection.

### 5. ARQ job repair is incomplete at dependency/runtime level

Evidence:

- `send_consent_reminders` and `send_consent_renewal_reminders` now exist in `app/modules/jobs.py`.
- Job dependency construction moved to `app/services/job_dependency_factory.py`.

Risk:

- `arq` is not pinned in `requirements/base.in` or `requirements/dev.in`.
- Importing `app.modules.jobs` fails in the current environment.
- Some checker/test contracts still expect old direct symbols in `jobs.py`, so the evidence suite is stale.

Required closure:

- Pin `arq`.
- Regenerate requirements lock files.
- Add import smoke tests for `app.modules.jobs`.
- Update job integrity checks to verify behavior through `job_dependency_factory`, not stale source text.

### 6. Lesson object authorization is materially improved but should be hardened

Evidence:

- Lesson routes call service-layer authorization helpers.
- Repair check passes.

Risk:

- `lesson_authorization.py` uses dynamic import fallbacks and catches broad exceptions before direct model fallback.
- Broad exception handling can hide repository/data failures and convert them into misleading authorization or not-found behavior.

Required closure:

- Replace dynamic import probes with typed dependency imports once canonical modules are settled.
- Narrow exception handling to expected constructor/signature failures.
- Add integration tests for forbidden lesson read, forbidden complete, and forbidden sync.

### 7. Evidence suite needs governance

Evidence:

- Some checks pass while related checks fail on stale expectations.
- Some scripts generate docs as side effects during tests.
- Several integration tests report skipped while their wrapper scripts mark the proof pass.

Risk:

- The project can accidentally claim closure based on static or skipped evidence.

Required closure:

- Adopt explicit proof statuses:
  - `static-passing`
  - `runtime-passing`
  - `integration-passing`
  - `production-ready`
- Treat skipped integration tests as not proven.
- Make generated evidence writes opt-in or isolate them from routine tests.

## Recommended lead-developer priorities

1. Close P0/P1 runtime risks first: JWT fallback, ARQ dependency/import, POPIA response contract.
2. Convert structural adapters into typed services and clear dependency contracts.
3. Wire diagnostics session integrity into live route behavior.
4. Clean stale tests and scripts so the evidence suite becomes trustworthy.
5. Reduce architecture boundary ignores and migrate remaining routers away from direct repositories.
6. Consolidate service/repository families into canonical module ownership.
7. Add end-to-end runtime proof for the learner/guardian lifecycle, POPIA lifecycle, diagnostic session flow, and background jobs.

## Final assessment

The recent changes are a strong repair pass, not a final closure pass. The codebase is moving in the right direction: critical route boundaries are tighter, several runtime blockers have been repaired, and architectural guardrails are starting to exist. The next engineering stage should be proof-driven consolidation: remove compatibility shims, prove behavior through HTTP/runtime tests, and turn the audit evidence suite into a reliable release gate.
