---
title: "RR-007 Product Quality Gate Policy"
status: active
owner: engineering
audience: developer
source_of_truth: false
last_reviewed: 2026-07-02
review_interval_days: 60
---


# RR-007 Product Quality Gate Policy

**RR item:** RR-007  
**Purpose:** bind product-completeness claims to explicit quality evidence.

## Required gates

| Gate | Evidence anchor | Required state |
|---|---|---|
| Playwright in CI | `.github/workflows/e2e.yml` and `.github/workflows/rr007-product-quality-gates.yml` | CI-visible journey checks |
| Content expansion roadmap | `docs/curriculum/rr007_content_expansion_roadmap.md` | roadmap only; no expanded production scope |
| Load testing | `docs/performance/rr007_load_testing_plan.md` | learner journey scenarios recorded |
| Accessibility audit | `docs/product_quality/rr007_accessibility_audit_plan.md` | audit scope recorded |
| PWA offline verification | `docs/product_quality/rr007_pwa_offline_verification_plan.md` | offline scope recorded |
| Multilingual proof | `docs/product_quality/rr007_multilingual_lesson_proof_plan.md` | proof expectations recorded |
| Supabase/raw Postgres ADR | `docs/adr/ADR-035-supabase-vs-raw-postgres-product-quality-gate.md` | decision record exists |

## Carried residual caveats

- RR-003 remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.

## Boundary

RR-007 is a product quality-gate authority slice only. Production release, deployment, release tagging, public beta, and Runtime KG implementation are not authorised.
