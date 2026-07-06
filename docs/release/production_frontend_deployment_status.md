---
title: Production Frontend Deployment Status
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Production Frontend Deployment Status

Generated at: `2026-06-27T02:19:21Z`
Commit: `88840fc52a05c694c6d313e57bc8cba4bcda4c63`

**Status:** `production-frontend-configured`

| Check | Passed | Detail |
|---|---:|---|
| `docker-compose.prod.yml exists` | True | docker-compose.prod.yml |
| `production frontend service exists` | True | service key `frontend` |
| `frontend uses production Docker target` | True | target: production + Dockerfile.frontend |
| `nginx depends on frontend` | True | nginx depends_on includes frontend |
| `nginx cert mount aligned to /etc/letsencrypt` | True | nginx reads same cert path certbot writes |
| `certbot writes to /etc/letsencrypt` | True | certbot volume target |
| `playwright defaults to Next.js port 3050` | True | baseURL fallback |
| `playwright timeout hardened` | True | timeout >= 60s |

## Blockers

- None

## Interpretation

This validates production deployment configuration only. It does not prove a successful deployment or live browser run.
