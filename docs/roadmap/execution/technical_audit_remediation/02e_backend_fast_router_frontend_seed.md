---
title: Technical Audit Remediation Phase 02E — Backend Fast Router, Frontend, MCP and Seed Contracts
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Technical Audit Remediation Phase 02E — Backend Fast Router, Frontend, MCP and Seed Contracts

**Status:** Implementation ready  
**Authority gate:** `make test-fast`  
**Evidence policy:** This slice may record focused remediation evidence only. Passing backend-fast candidate evidence is still forbidden until `make test-fast` exits 0.

## Targeted failure clusters

Phase 02E targets the next high-yield backend-fast clusters after Phase 02D:

1. **MCP authority import** — `tools/etl/etl_mcp_server_v2.py` imports `mcp.server.fastmcp.FastMCP`; the dependency must be installed and proven in `.venv`.
2. **Frontend deployment / Playwright port contract** — Playwright must default to the Next.js production/dev port `3050` using the checker-recognised `http://127.0.0.1:3050` fallback.
3. **Router/auth-boundary contracts** — keep `curriculum_expansion` declared in the v2 router contract and restore the historical `ether.py` authenticated boundary file.
4. **Staging seed executor result handling** — mocked and real seed results must safely expose a result identity and not fail when test doubles lack ORM-only attributes.

## Non-scope

- No passing backend-fast evidence is created by this slice.
- No Phase 02R governance is changed.
- No product release-readiness claim is made.
- No live DB migration is executed.
- No runtime knowledge-graph implementation is introduced; KG remains a future architectural north star.

## Expected verification

```bash
python3 scripts/audit_remediation/verify_backend_fast_phase02e.py --json
python3 -m compileall -q app/api_v2_routers/ether.py app/services/content_staging_seed_executor.py scripts/curriculum/seed_staging_review_scopes.py scripts/audit_remediation
python3 -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02e.py --no-cov
```

After evidence is recorded, retry the real authority gate:

```bash
bash scripts/audit_remediation/collect_backend_fast_evidence.sh
```
