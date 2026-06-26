# Production Frontend Deployment Status

Generated at: `2026-06-24T11:30:38Z`
Commit: `f5d72b8380da6403371ea91f6c8298626ba07aa1`

**Status:** `deployment-config-not-proven`

| Check | Passed | Detail |
|---|---:|---|
| `docker-compose.prod.yml exists` | True | docker-compose.prod.yml |
| `production frontend service exists` | True | service key `frontend` |
| `frontend uses production Docker target` | True | target: production + Dockerfile.frontend |
| `nginx depends on frontend` | True | nginx depends_on includes frontend |
| `nginx cert mount aligned to /etc/letsencrypt` | True | nginx reads same cert path certbot writes |
| `certbot writes to /etc/letsencrypt` | True | certbot volume target |
| `playwright defaults to Next.js port 3050` | False | baseURL fallback |
| `playwright timeout hardened` | True | timeout >= 60s |

## Blockers

- playwright defaults to Next.js port 3050

## Interpretation

This validates production deployment configuration only. It does not prove a successful deployment or live browser run.
