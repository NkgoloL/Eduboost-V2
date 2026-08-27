# CI Auth Refresh DB Proof Workflow Status

Generated at: `2026-08-27T16:20:39Z`
Commit: `96a44fcb30032631891f43b86faab0e8f45288a3`

**Status:** `ci-auth-refresh-db-proof-workflow-not-proven`

| Check | Passed | Detail |
|---|---:|---|
| `workflow exists` | False | .github/workflows/auth-refresh-db-proof.yml |
| `workflow_dispatch enabled` | False | manual run supported |
| `postgres service configured` | False | disposable Postgres service |
| `proof DSN configured` | False | local service DSN |
| `integration proof test executed` | False | DB proof test path |
| `evidence attach executed` | False | evidence attach target |
| `evidence release check executed` | False | release evidence target |
| `concrete run URL uses github.run_id` | False | numeric run id at runtime |
| `commit SHA uses github.sha` | False | concrete commit SHA |
| `artifact upload configured` | False | proof artifacts uploaded |
| `no placeholder REAL_RUN_ID` | True | placeholder rejected |
| `no symbolic REAL_DSN` | True | no REAL_* evidence placeholder |

## Blockers

- workflow exists
- workflow_dispatch enabled
- postgres service configured
- proof DSN configured
- integration proof test executed
- evidence attach executed
- evidence release check executed
- concrete run URL uses github.run_id
- commit SHA uses github.sha
- artifact upload configured

## No false-closure rules

- Workflow configuration does not prove the workflow has run.
- Release evidence still requires a concrete GitHub Actions run URL.
- This workflow does not approve beta release.
