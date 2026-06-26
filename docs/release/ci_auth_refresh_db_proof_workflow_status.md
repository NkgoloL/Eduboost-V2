# CI Auth Refresh DB Proof Workflow Status

Generated at: `2026-06-24T11:30:11Z`
Commit: `f5d72b8380da6403371ea91f6c8298626ba07aa1`

**Status:** `ci-auth-refresh-db-proof-workflow-not-proven`

| Check | Passed | Detail |
|---|---:|---|
| `workflow exists` | True | .github/workflows/auth-refresh-db-proof.yml |
| `workflow_dispatch enabled` | True | manual run supported |
| `postgres service configured` | True | disposable Postgres service |
| `proof DSN configured` | True | local service DSN |
| `integration proof test executed` | True | DB proof test path |
| `evidence attach executed` | True | evidence attach target |
| `evidence release check executed` | True | release evidence target |
| `concrete run URL uses github.run_id` | True | numeric run id at runtime |
| `commit SHA uses github.sha` | True | concrete commit SHA |
| `artifact upload configured` | False | proof artifacts uploaded |
| `no placeholder REAL_RUN_ID` | True | placeholder rejected |
| `no symbolic REAL_DSN` | True | no REAL_* evidence placeholder |

## Blockers

- artifact upload configured

## No false-closure rules

- Workflow configuration does not prove the workflow has run.
- Release evidence still requires a concrete GitHub Actions run URL.
- This workflow does not approve beta release.
