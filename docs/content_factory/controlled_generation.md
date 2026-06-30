# Content Factory Controlled Generation

PR-CF-008 adds controlled gap-filling generation for configured Content Factory scopes.

## Safety Policy

Generation may create artifacts and submit valid artifacts to `pending_review`. It must not auto-approve, seed production, promote production, or make generated content learner-visible.

Generation execution is disabled by default:

```bash
CONTENT_FACTORY_GENERATION_ENABLED=false
CONTENT_FACTORY_PROVIDER=deterministic
CONTENT_FACTORY_MAX_ARTIFACTS_PER_TASK=10
CONTENT_FACTORY_MAX_SCOPE_RUN_ARTIFACTS=250
```

When generation is disabled, planning can still run but execution endpoints fail closed with `409 Conflict`.

## Provider Modes

- `deterministic`: local/test provider that creates schema-valid deterministic artifacts.
- `llm`: reserved for a reviewed provider adapter and blocked unless generation is explicitly enabled.
- `disabled`: fails closed.

## Planning

The planner uses staging readiness reports and configured coverage targets to create generation tasks only for missing `diagnostic_items` and `lessons`. It skips assessment blueprints, study plan templates, fully green targets, missing source context, incompatible licenses, low-quality source chunks, and duplicate idempotency keys.

Task idempotency uses:

```text
scope_id:caps_ref:layer:target_version:prompt_version
```

## Execution

The executor locks a queued task, builds grounded source context, calls the provider only when the feature flag is enabled, writes generated artifacts, attaches provenance rows, writes validation reports, and routes valid artifacts to `pending_review`. Invalid artifacts are marked `validation_failed`.

## Admin Endpoints

- `POST /api/v2/admin/content-factory/runs/{run_id}/plan-missing`
- `POST /api/v2/admin/content-factory/runs/{run_id}/execute`
- `POST /api/v2/admin/content-factory/tasks/{task_id}/execute`
- `GET /api/v2/admin/content-factory/tasks/{task_id}`
- `GET /api/v2/admin/content-factory/runs/{run_id}/execution-report`

All routes are admin-only. No public generation route is exposed.
