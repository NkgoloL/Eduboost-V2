---
title: TA Phase 06 — E2E / Playwright Execution Authority
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

# TA Phase 06 — E2E / Playwright Execution Authority

**Status:** Implementation ready  
**Authority scope:** deterministic mocked frontend Playwright journeys  
**Remote CI success claimed:** No  
**Full backend-backed E2E readiness claimed:** No

## Purpose

Phase 06 re-establishes a controlled E2E/Playwright execution authority after the backend-fast, frontend-tooling, CI-workflow, and dependency-scan authority gates have been closed.

The gate proves that:

- root Playwright dependencies are owned by the root `pnpm-lock.yaml`;
- frontend dependencies are owned by `app/frontend/pnpm-lock.yaml`;
- Playwright runs from the repository root through `pnpm exec playwright`;
- the root Playwright config starts the Next.js frontend through pnpm on port `3050`;
- deterministic mocked learner and parent journeys can execute without requiring the full backend stack;
- CI/E2E workflows use pnpm, supported action pins, and stable artifact upload locations.

## Authority commands

```bash
python3 scripts/audit_remediation/verify_e2e_playwright_authority.py --json
python3 scripts/audit_remediation/run_e2e_playwright_authority.py \
  --output-dir docs/release-evidence/technical-audit/e2e-playwright-authority/raw \
  --json
```

The execution runner performs:

```text
pnpm --version
pnpm install --frozen-lockfile
pnpm --dir app/frontend install --frozen-lockfile
pnpm exec playwright --version
pnpm exec playwright install chromium
PLAYWRIGHT_MOCK_API=1 pnpm exec playwright test \
  tests/e2e/learner-mocked-api-journey.spec.ts \
  tests/e2e/parent-mocked-api-journey.spec.ts \
  --project=chromium --reporter=list
```

## Evidence command

```bash
bash scripts/audit_remediation/collect_e2e_playwright_authority_evidence.sh
python3 scripts/audit_remediation/verify_e2e_playwright_evidence.py \
  --evidence-dir docs/release-evidence/technical-audit/e2e-playwright-authority \
  --json
```

## Passing evidence policy

Passing evidence may be recorded only when:

1. the static authority verifier returns `valid: true`;
2. the Playwright authority runner returns `valid: true`;
3. every authority step has return code `0`;
4. the evidence verifier returns `valid: true`;
5. `raw/SHA256SUMS.txt` matches the final raw artifacts and does not self-hash the evidence checker.

## Boundary

This phase does not claim remote GitHub Actions success, full production E2E readiness, live backend-backed journey success, product release readiness, or runtime KG implementation.

KG remains a future architectural north star only.
