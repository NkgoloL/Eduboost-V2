# Phase 14 — Live-Stack Readiness Authority

Status: authority harness only; evidence is unclaimed until captured from a controlled runtime stack.

## Purpose

Phase 14 proves that the application is healthy against a real running stack with
Postgres and Redis available. It follows the true-state audit finding that shallow
imports and frontend/mocked E2E were green, but `/ready` and deep-health endpoints
were not proven without Postgres and Redis.

## Required preconditions

- Phase 13B post-merge protected-branch baseline verifier is valid.
- The command is run from clean `master` after the Phase 13B evidence PR lands.
- API server is running and reachable at the selected `--base-url`.
- Postgres and Redis are running and configured for the API process.
- Migrations are applied.
- Audit repository table is readable.

## Authority command

```bash
python3 scripts/runtime_readiness/capture_live_stack_readiness_evidence.py \
  --base-url http://127.0.0.1:8000 \
  --claim-live-stack-readiness \
  --readiness-owner "Nkgolo Lebelo" \
  --require-valid \
  --json

python3 scripts/runtime_readiness/verify_live_stack_readiness.py --json
```

## Required endpoints

- `/health`
- `/ready`
- `/v2/health/deep`
- `/api/v2/health/deep`
- `/openapi.json`

## Required critical components

- `secrets`
- `postgres`
- `redis`
- `migrations`
- `audit_repository`

All critical components must report `status: ok` on the deep-health responses.
Optional components must be `ok` or `skipped` unless the operator explicitly uses
`--allow-optional-degraded` and records that exception in evidence.

## Boundary

This phase records controlled live-stack readiness only. It does not authorise:

- production release;
- deployment;
- release tagging;
- live learner traffic;
- full backend-backed E2E readiness;
- runtime knowledge-graph implementation.
