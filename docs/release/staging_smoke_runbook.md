# Staging Smoke Runbook

This runbook defines the repeatable command used to produce staging smoke evidence.

## Preconditions

- A staging deployment exists.
- The release candidate commit SHA is known.
- `STAGING_BASE_URL` points at the deployed environment.
- The environment is safe for test registration using `example.invalid` email addresses.

## Command

```bash
export STAGING_BASE_URL="https://staging.example.com"
make staging-smoke
```

or:

```bash
PYTHONPATH=. python3 scripts/run_staging_smoke.py --base-url "$STAGING_BASE_URL"
```

## Outputs

| File | Purpose |
|---|---|
| `docs/release/staging_smoke_latest.json` | Machine-readable smoke result |
| `docs/release/staging_smoke_evidence.md` | Human-readable release evidence |

## Checks

The smoke runner currently checks:

- deep health route
- OpenAPI route
- security headers on a health route
- auth registration response shape
- POPIA export authorization requirement

## Interpretation

A passing smoke test supports staging readiness. It does not replace:

- full CI
- migration proof
- backup/restore drill
- rollback drill
- legal/security/content signoff


## Validation modes

`make staging-smoke-check` validates that the latest smoke evidence exists **and passed**.

`make staging-smoke-schema-check` validates only that the latest smoke evidence is well-formed. Use it for debugging failed smoke runs without claiming staging readiness.

Do not use placeholder URLs such as `https://staging.example.com`; the runner rejects example URLs by default.
