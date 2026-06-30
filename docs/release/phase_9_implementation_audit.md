# Phase 9 Implementation Audit - Release-Blocker Checklist

**Audit date:** 2026-06-14
**Auditor:** Codex
**Status:** Supported after remediation; original completion claim was overstated

## Artifact Check

| Artifact | Status |
|---|---|
| `docs/roadmap/execution/phase_9_execution_plan.md` | Present; refreshed 2026-06-14 |
| `docs/roadmap/execution/phase_9_implementation_report.md` | Present; refreshed 2026-06-14 |
| `docs/release/phase_9_evidence.md` | Present; refreshed 2026-06-14 |
| `docs/release/phase_9_implementation_audit.md` | Present |

## Acceptance Criteria Audit

| Criterion | Evidence | Verdict |
|---|---|---|
| OpenAPI schema generated and drift check passes | `scripts/generate_openapi.py --check` passed after regenerating `docs/openapi.json` | Pass |
| CI fails on agreed release-blocking checks | Duplicate `schema-drift` id fixed; pnpm workflow drift fixed; workflow YAML parses | Pass |
| Release documentation references current evidence | Phase docs now reference `docs/openapi.json`, not missing `docs/reference/openapi.json` | Pass |
| Route aliases are governed | `scripts/check_route_alias_matrix.py` passed; `/api/v2` canonical with `/v2` compatibility aliases | Pass with accepted debt |
| AI/LLM validation commands exist and pass | Answer-key checker, item-bank count, IRT tests, and POPIA sweep now pass | Pass |
| API envelope runtime tests prove live behavior | 8 DB-backed tests skipped locally because PostgreSQL was unavailable | Partial |

## Discrepancies Found and Corrected

- `docs/openapi.json` drifted from the generated app schema.
- The implementation report referenced missing `docs/reference/openapi.json`; the actual committed schema is `docs/openapi.json`.
- `.github/workflows/ci-cd.yml` defined `schema-drift` twice.
- Several frontend workflow steps still used `npm ci` or `package-lock.json` despite the frontend using pnpm.
- The answer-key checker scanned the whole repo by default and did not understand the current generated lesson schema.
- The documented item-bank count script was missing.
- The route-alias policy script could not be executed directly because its path bootstrap ran after imports.

## Verification Run

See `docs/release/phase_9_evidence.md` for the command log. Current local verification includes:

- OpenAPI drift check: passed.
- OpenAPI/unit envelope evidence: 4 passed, 8 skipped due missing PostgreSQL.
- Answer-key independence: 24 launch lesson payloads passed.
- Item-bank count: 120 approved Grade 4 Mathematics items, above the 50-item minimum.
- IRT tests: 11 passed.
- POPIA sweep: passed with only informational PII pattern sightings.
- Route alias policy: 173 canonical rows, 0 missing aliases.
- Workflow YAML parse: passed for touched workflows.

## Result

Phase 9 is now supported for the implemented release-blocker checklist scope after remediation. Remaining proof gaps are environmental: live API health and DB-backed API-envelope behavior need a running stack/PostgreSQL environment.
