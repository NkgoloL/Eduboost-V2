# Full Generation Runner

## Overview

The Full Generation Runner is an overnight-safe batch generation system that fills all configured Content Factory gaps across all scopes and layers without promoting anything to production or bypassing review.

## Core Rule

Overnight automation may:

- Generate and validate
- Submit valid artifacts to pending_review
- Seed only already-approved artifacts to staging


## Local setup (Supabase) and execution

This section documents how to run the full-generation runner locally against Supabase (dev Postgres).

### 1) Start local Supabase database

```bash
supabase db start
```

The Postgres URL is typically:

```text
postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

For async SQLAlchemy (app runtime):

```text
postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres
```

### 2) Apply Alembic migrations

```bash
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres \
  alembic upgrade head
```

Note: Migration 20260526_0300 references `content_promotion_events.promotion_event_id` as the FK.

### 3) Seed scopes, coverage targets, and minimal source context

The planner requires:

- `content_scopes` and `content_coverage_targets` populated for all layers
- Minimal approved/indexed ETL source rows per CAPS ref to avoid source-blocked planning

Run the local seeding script:

```bash
PYTHONPATH=. DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres \
  python3 scripts/content_factory/seed_local_sources.py
```

This loads from:
- `data/content_factory/scopes.json`
- `data/content_factory/coverage_targets.json`

and inserts minimal `content_generation_artifacts` and `content_artifact_sources` to satisfy source gates.

### 4) Run: plan-only quick check

```bash
APP_ENV=staging \
CONTENT_STARTUP_SEED_ENABLED=false \
CONTENT_FACTORY_GENERATION_ENABLED=true \
CONTENT_FACTORY_PROVIDER=deterministic \
CONTENT_LEARNER_READ_MODE=production_only \
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres \
python3 scripts/content_factory/run_full_generation.py \
  --all-scopes \
  --layers diagnostic_items,lessons,assessment_blueprints,study_plan_templates \
  --plan-only \
  --write-report
```

### 5) Run: overnight-safe full job (nohup)

```bash
mkdir -p reports/content_factory

nohup python3 scripts/content_factory/run_full_generation.py \
  --all-scopes \
  --layers diagnostic_items,lessons,assessment_blueprints,study_plan_templates \
  --max-concurrency 2 \
  --max-artifacts 2000 \
  --budget-cap 50 \
  --resume \
  --seed-approved-to-staging \
  --verify-staging \
  --write-report \
  > reports/content_factory/full_generation_overnight.log 2>&1 &

echo $! > reports/content_factory/full_generation_overnight.pid
```

Tail progress:

```bash
tail -f reports/content_factory/full_generation_overnight.log
```

### 6) Troubleshooting

- `UndefinedColumnError` on promotion events FK:
  - Ensure migration `20260526_0300_content_factory_production_promotion_artifacts.py` references
    `content_promotion_events.promotion_event_id`.
- FK on `content_generation_runs.scope_id` for `all_scopes`:
  - The runner auto-creates a placeholder ContentScope `all_scopes` before acquiring the lock.
- Planned 0 / Skipped many targets:
  - Ensure coverage targets exist (step 3) and source context is present (the seed script adds minimal sources).

- Verify staging/readiness

Overnight automation must not:
- Approve, bulk approve, or promote production

Human review stays manual.

## Supported Layers

- diagnostic_items
- lessons
- assessment_blueprints
- study_plan_templates

## Usage

### Plan Only

```bash
python3 scripts/content_factory/run_full_generation.py \
  --all-scopes \
  --layers diagnostic_items,lessons,assessment_blueprints,study_plan_templates \
  --plan-only \
  --write-report
```

### Full Overnight Run

```bash
nohup python3 scripts/content_factory/run_full_generation.py \
  --all-scopes \
  --layers diagnostic_items,lessons,assessment_blueprints,study_plan_templates \
  --max-concurrency 2 \
  --max-artifacts 2000 \
  --budget-cap 50 \
  --resume \
  --seed-approved-to-staging \
  --verify-staging \
  --write-report \
  > reports/content_factory/full_generation_overnight.log 2>&1 &
```

## Configuration

Required environment variables:

```bash
CONTENT_FACTORY_GENERATION_ENABLED=true
CONTENT_FACTORY_PROVIDER=deterministic  # or llm
CONTENT_LEARNER_READ_MODE=production_only
```

Optional configuration:

```bash
CONTENT_FACTORY_MAX_ARTIFACTS_PER_TASK=10
CONTENT_FACTORY_MAX_SCOPE_RUN_ARTIFACTS=250
CONTENT_FACTORY_MAX_FULL_RUN_ARTIFACTS=2000
CONTENT_FACTORY_MAX_CONCURRENCY=2
CONTENT_FACTORY_BUDGET_CAP=50
CONTENT_FACTORY_RETRY_LIMIT=2
CONTENT_FACTORY_FULL_RUN_LOCK_TTL_MINUTES=180
```

## Reports

Reports are written to:

```
reports/content_factory/full_generation/<timestamp>/
```

Artifacts:
- summary.md
- summary.json
- scope_readiness_before.json
- scope_readiness_after.json
- planned_tasks.csv
- executed_tasks.csv
- generated_artifacts.csv
- pending_review.csv
- validation_failed.csv
- source_blockers.csv
- staging_seed_results.csv
- staging_verification.json
- errors.log

## Safety Guarantees

- No learner-visible content is generated or promoted
- No production promotion occurs
- No automatic approval
- Staging preview never exposes learner content
- Lock prevents concurrent full runs
- Budget and artifact caps prevent runaway generation
- Resumable execution handles interruptions
