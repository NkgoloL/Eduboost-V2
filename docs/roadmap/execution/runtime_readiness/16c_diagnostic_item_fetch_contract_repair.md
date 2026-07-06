---
title: Phase 16C — Diagnostic Item Fetch Runtime Contract Repair
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

# Phase 16C — Diagnostic Item Fetch Runtime Contract Repair

**Status:** repair harness only  
**Scope:** backend-backed seeded diagnostic item fetch and answer submission contract  
**Boundary:** no Phase 16 seeded E2E evidence is claimed by this repair.

## Purpose

Phase 16B repaired hydration and route identity. The diagnostic Playwright path
then reached the real backend-backed diagnostic item fetch and exposed a backend
runtime contract failure. Phase 16C repairs that next layer without broadening
into study-plan, lesson, parent portal, production release, deployment, live
learner traffic, or runtime KG implementation.

## Changes

- Dev-session bootstrap now ensures deterministic, non-production IRT diagnostic
  items exist for the seeded learner grade.
- `/api/v2/diagnostics/items/{learner_id}` now serialises both canonical item-bank
  rows and legacy IRT rows into the frontend diagnostic contract.
- Diagnostic item options are normalised from dictionary/list/object shapes into
  display labels.
- Subject labels are normalised to frontend subject codes such as `MATH` and
  `ENG`.
- The frontend diagnostic service accepts both record-shaped and list-shaped
  option payloads.
- The interactive diagnostic UI displays option labels while submitting answer
  keys (`A`, `B`, `C`, `D`) so backend IRT scoring receives the expected answer
  contract.

## Required verification

```bash
python3 -m pytest -q \
  tests/unit/runtime_readiness/test_phase16c_diagnostic_item_fetch_contract.py \
  --no-cov

python3 -m py_compile \
  app/services/dev_diagnostic_seed.py \
  app/services/auth_lifecycle_impl.py \
  app/api_v2_routers/diagnostics.py

pnpm --dir app/frontend run type-check
pnpm --dir app/frontend run lint
pnpm --dir app/frontend run test

pnpm exec playwright test tests/e2e/diagnostic.spec.ts \
  --project=chromium \
  --workers=1 \
  --trace=on

git diff --check
```

## Exit criteria

Phase 16C closes when the focused diagnostic Playwright spec is green against
live Postgres, Redis, API, and frontend, and no Phase 16 evidence payload is
committed.

## Explicit non-claims

- Phase 16 seeded E2E evidence is not claimed.
- Full seeded study-plan/lesson journey readiness is not claimed.
- Full parent-portal/consent/export/erasure readiness is not claimed.
- Production release is not authorised.
- Deployment is not authorised.
- Release tagging is not authorised.
- Live learner traffic is not authorised.
- Runtime KG implementation is not claimed.
