---
title: "EduBoost V2 Comprehensive Documentation Staleness Remediation Plan"
status: active
owner: documentation-governance
reviewers: [engineering, architecture, release-management, product]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-22
review_interval_days: 30
evidence_command: "make docs-housekeeping-check"
code_anchors: [docs/current_state.md, docs/documentation/source_of_truth.yml, scripts/generate_route_inventory.py, scripts/maintenance/audit_documentation_inventory.py]
---

# EduBoost V2 Comprehensive Documentation Staleness Remediation Plan

## Executive Summary & Baseline Metrics

On **2026-09-22**, a comprehensive empirical audit of the entire `docs/*` directory in **Eduboost-V2** was conducted against the active repository baseline at `master` (`ff0e09bc7`).

### 1. Quantitative Inventory
- **Total Files under `docs/`**: **3,827 files** (Total size: ~40 MB after 122MB runaway file cleanup).
- **Markdown Files (`.md`)**: **2,335 files** (1,745 with YAML front matter, 590 untracked without front matter).
- **JSON Files (`.json`)**: **1,277 files** (contracts, machine inventories, schemas, test logs).
- **Text Files (`.txt`)**: **261 files** (raw CLI and pytest run captures).
- **Top Directories by Markdown Count**:
  - `docs/roadmap/`: 474 MD, 432 JSON
  - `docs/release/`: 429 MD, 66 JSON
  - `docs/operations/`: 187 MD
  - `docs/release-evidence/`: 147 MD, 694 JSON, 248 TXT
  - `docs/security/`: 107 MD
  - `docs/archive/`: 96 MD
  - `docs/frontend/`: 65 MD
  - `docs/knowledge_graph/`: 62 MD
  - `docs/adr/`: 58 MD
  - `docs/engineering/`: 56 MD
  - `docs/architecture/`: 35 MD

---

## The 6 Identified Dimensions of Documentation Staleness

### Dimension 1: Mathematical Review Interval Expiry (Stale by Contract)
- **489 Markdown documents** have exceeded their designated `review_interval_days` (up to 69 days overdue).
- Example: [`docs/architecture/architecture_diagram.md`](../architecture/architecture_diagram.md) was last reviewed on `2026-06-23` with a 60-day interval (`days_since = 91`), rendering it 31 days overdue.
- **590 Markdown documents** have no front matter whatsoever, escaping automated governance.
- **142 Markdown documents** claim `source_of_truth: true`, conflicting directly with the 24 canonical sections registered in [`docs/documentation/source_of_truth.yml`](source_of_truth.yml).

### Dimension 2: API & Route Inventory Divergence (100% Drift)
- **Committed**: [`docs/route_inventory.md`](../route_inventory.md) records **459 route entries** (and older documents state 355).
- **Active Code**: Running `.venv/bin/python scripts/generate_route_inventory.py --check` against `app.api_v2:app` yields **915 route entries** (456 undocumented or unreflected dual-prefix routes).

### Dimension 3: Technical Stack & Architectural Drift
1. **Background Worker Engine**:
   - *Stale Docs*: Reference Celery or incomplete Celery-to-ARQ migration.
   - *Active Truth*: Code uses **Redis 7 + ARQ workers** exclusively (`app/jobs/`).
2. **Frontend Tooling & Framework**:
   - *Stale Docs*: Cite Next.js 14 / React 18 or Next.js 15.
   - *Active Truth*: Tranche 6 aligned the stack to **Next.js 16.3.3** (`@next/swc`, React 19) with hermetic offline builds.
3. **Test Suite & Coverage Floor**:
   - *Stale Docs*: Reference 70% or 80% coverage floors.
   - *Active Truth*: Enforces a **90%** minimum floor in `coverage_contract.json` and `.github/workflows/pr-core.yml` (validated via `evaluate_coverage_contract()` across 4 coverage classes), with **95.7%** statement coverage documented as a milestone achievement from branch `feature/coverage-target-90` (active CI enforces the contract floor fails-closed).
4. **Database Consolidation & Migrations**:
   - *Stale Docs*: Propose table-splitting for audit logs and parental consents.
   - *Active Truth*: Consolidated schema with append-only immutable triggers is fully implemented (Tranche 7: DEF-12).
5. **Educational Validity & LEV**:
   - *Stale Docs*: Lack longitudinal educational validation references.
   - *Active Truth*: Fast-track PRD-4A Longitudinal Educational Validation is implemented (`ff0e09bc7`).

### Dimension 4: Runaway Generator Artifacts (Remediated)
- [`docs/release/backend_deletion_candidate_inventory.md`](../release/backend_deletion_candidate_inventory.md) had reached **122 MB (385,069 lines)** due to a bug in [`scripts/generate_backend_deletion_candidate_inventory.py`](../../scripts/generate_backend_deletion_candidate_inventory.py) where `docs/release` was included in `SCAN_ROOTS`, causing the generator to recursively scan its own previous markdown table output.
- **Remediation Implemented**: `SCAN_ROOTS` was restricted to `("app", "tests", "scripts", "alembic")` with directory pruning for `frontend` and `node_modules`, shrinking the file from 122MB to **197 KB (1,350 lines)** and reducing test suite execution from 92 seconds to 15 seconds.

### Dimension 5: Broken Local Markdown Links (Remediated)
- [`docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_todo.md`](../roadmap/production_readiness/prd_4a_longitudinal_educational_validation_todo.md) contained 15 broken links to `lev/workstreams/LEV-WS*.md` because links were mistakenly prepended with `docs/roadmap/production_readiness/`.
- **Remediation Implemented**: Relative targets were updated, restoring 0 broken links.

### Dimension 6: Claim Discipline Violations
- Historical audit documents in `docs/archive/legacy-doc-framework/` and `audits/reports/` contain unhedged phrases like "production-ready", "100% complete", and "launch approved" without the mandatory boundary phrase:
  `"This repository-side evidence does not authorize production launch."`

---

## 4-Tier Documentation Taxonomy

To eliminate perpetual drift, all files in `docs/` are categorized into four distinct tiers with explicit governance contracts:

```
+-----------------------------------------------------------------------------------+
| Tier 1: Canonical Sources of Truth (SSOT)                                         |
| - Strictly the 24 files listed in docs/documentation/source_of_truth.yml         |
| - Mandatory YAML front matter; review_interval_days <= 60                        |
| - source_of_truth: true                                                           |
+-----------------------------------------------------------------------------------+
                                      |
+-----------------------------------------------------------------------------------+
| Tier 2: Active Supporting Engineering Documentation                               |
| - Architecture, ADRs, active Runbooks, Schema contracts                          |
| - Mandatory YAML front matter; review_interval_days <= 90                        |
| - source_of_truth: false                                                          |
+-----------------------------------------------------------------------------------+
                                      |
+-----------------------------------------------------------------------------------+
| Tier 3: Immutable Historical Evidence & Audit Logs                                |
| - docs/release-evidence/, docs/archive/, audits/                                 |
| - status: archived; banner indicating historical non-authoritative status        |
| - Relaxed metadata validation; immutable                                         |
+-----------------------------------------------------------------------------------+
                                      |
+-----------------------------------------------------------------------------------+
| Tier 4: Machine-Generated Artifacts                                               |
| - docs/generated/, docs/route_inventory.md, docs/openapi.json                     |
| - Fully automated regeneration via Makefile; never hand-edited                   |
+-----------------------------------------------------------------------------------+
```

---

## Phased Remediation Execution Roadmap

### Phase 1: Tooling Hardening & Working-Tree Anomaly Elimination (Status: COMPLETED)
- [x] Fix self-referential recursion in `scripts/generate_backend_deletion_candidate_inventory.py` by excluding `docs/` and pruning `frontend`/`node_modules`.
- [x] Regenerate `docs/release/backend_deletion_candidate_inventory.md` (working-tree file shrunk from 122MB to 197KB).
- [x] Repair 15 broken workstream links in `docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_todo.md`.
- [x] Verify `tests/unit/test_docs_intelligence.py` runtime reduction from 92.3s to 15.8s.

> [!IMPORTANT]
> **Git History Packfile Scope Boundary (Historical Blob Purge)**:
> - **In Scope (Current PR)**: Working-tree remediation (shrunk to 197KB, unblocks local checkouts, fixes test timeouts, stops exponential re-generation).
> - **Explicitly Out of Scope (Current PR)**: Historical git object database rewrite (`git filter-repo` / BFG). Rewriting git history modifies all downstream commit SHAs, invalidates existing developer checkouts and open pull requests, and requires a synchronized force-push to `origin/master`. This repository maintenance action is scoped to a dedicated, human-authorized maintenance window rather than a documentation branch.

### Phase 2: Authority Reconciliation & Single-Source-of-Truth Affirmation
- [ ] Affirm [`docs/roadmap/production_readiness/prd11_production_release_register.json`](../roadmap/production_readiness/prd11_production_release_register.json) as the active canonical PRD authority.
- [ ] Update [`docs/current_state.md`](../current_state.md) to incorporate verified technical achievements (Tranches 5–8, PRD-4A LEV) while preserving all fail-closed release boundaries.

### Phase 3: Machine Artifact Regeneration & Synchronisation
- [ ] Regenerate [`docs/route_inventory.md`](../route_inventory.md) using `.venv/bin/python scripts/generate_route_inventory.py --output docs/route_inventory.md` to reflect all 915 routes.
- [ ] Regenerate documentation inventory tables using `check_doc_inventory_reproducible.py --root . --update`.
- [ ] Validate route and OpenAPI integrity with `make route-inventory-check` and `make openapi-check`.

### Phase 4: Taxonomy Reorganization & Front-Matter Alignment
- [ ] Demote the 118 non-canonical documents claiming `source_of_truth: true` to `source_of_truth: false`.
- [ ] Add standard YAML front matter to priority untracked documents in active domains (`docs/architecture/`, `docs/security/`, `docs/database/`).
- [ ] Apply the historical disclaimer banner to all archived documents in `docs/archive/legacy-doc-framework/`.

### Phase 5: Technical Domain Content Rewrites & Review-Date Integrity
- [ ] **Architecture**: Update `docs/architecture/architecture_diagram.md` and `docs/architecture/README.md` with Redis 7 / ARQ workers and the 915-route modular topology.
- [ ] **Frontend**: Update `docs/frontend/README.md` and `docs/adr/ADR-023` to record Next.js 16.3.3 and React 19.
- [ ] **Database**: Update `docs/database/schema_integrity.md` with consolidated Alembic lineage and immutable audit trigger details.
- [ ] **Review Interval Anti-Theatre Rule**:
  - **No Blanket Date Resets**: Batch-updating `last_reviewed` without inspecting file contents is strictly prohibited.
  - Review dates are updated **strictly and only** on files whose content and code anchors have been actively rewritten and verified in this pass.
  - All other expired documents remain honestly marked as overdue and cataloged in [`docs/documentation/stale_documentation_review_register.md`](stale_documentation_review_register.md) with their true `days_stale` preserved.

### Phase 6: Automated CI Anti-Drift Governance
- [ ] Implement `scripts/maintenance/check_doc_review_dates.py` to automatically report documents that exceed their review interval.
- [ ] Add a file size guard (< 1 MB) in `scripts/maintenance/check_repo_hygiene.py` to prevent future generator runaways.
- [ ] Ensure `make docs-housekeeping-check` runs in CI via `.github/workflows/pr-core.yml` with zero warnings.

---

## Deterministic Claim-to-Code Verification Matrix

Every factual statement written into active documentation must trace to an executable automated check:

| Documented Claim | Target Documentation | Verification Command (Fails Closed) | Expected Output / Assertion |
|---|---|---|---|
| Next.js Tooling 16.3.3 | `docs/frontend/README.md` | `jq -e '.dependencies.next == "16.3.3"' app/frontend/package.json` | Exit `0` |
| No Celery, Redis 7 + ARQ only | `docs/architecture/architecture_diagram.md` | `test $(git grep -rlE "^\s*(import\|from)\s+celery\b" app/ \| wc -l) -eq 0` | Exit `0` (0 matching files) |
| ARQ Worker Configured | `docs/architecture/architecture_diagram.md` | `git grep -l "from arq" app/core/arq_worker.py` | Matches `app/core/arq_worker.py` |
| 90% Minimum Coverage Floor | `docs/testing/README.md` | `jq -e '.coverage_thresholds.minimum_line_coverage_percent == 90' docs/roadmap/production_readiness/coverage_contract.json` | Exit `0` |
| Coverage Contract & Taxonomy Validated | `docs/testing/README.md`, `docs/current_state.md` | `.venv/bin/python -m pytest tests/unit/coverage_suites/test_coverage_contract.py -q --no-cov` | Exit `0` (Contract valid across all 4 classes) |
| Consolidated Database Schema | `docs/database/schema_integrity.md` | `.venv/bin/python scripts/verify_migration_graph.py` | Exit `0` (Graph valid) |
| 915 Live Route Entries | `docs/route_inventory.md` | `.venv/bin/python scripts/generate_route_inventory.py --check` | Exit `0` |
| Fail-Closed Launch Boundaries | `docs/current_state.md` | `jq -e '.production_release_authorised == false and .billing_launch_authorised == false' docs/roadmap/production_readiness/prd11_production_release_register.json` | Exit `0` |
| PRD-4A LEV Task Register Integrity | `docs/roadmap/production_readiness/lev/` | `.venv/bin/python scripts/educational_validation/verify_lev_task_register.py --repo-root .` | Exit `0` (`VALID`, 222 tasks, 0 errors) |
| PRD-4A LEV Governance Cross-Linking | `docs/current_state.md`, `docs/learning_science/` | `test $(git grep -rlE "(PRD-4A\|longitudinal_educational_validation)" docs/current_state.md docs/learning_science/ docs/research/ 2>/dev/null \| wc -l) -ge 1` | Exit `0` (Cross-references active) |

---

## Independent Headline Claim Verification (Single-Line Commands)

Run these commands in your shell to independently verify all headline audit claims:

```bash
# 1. Verify working-tree file size reduction (122MB -> 197KB)
ls -lh docs/release/backend_deletion_candidate_inventory.md

# 2. Verify 915 live routes vs 459 documented routes
.venv/bin/python scripts/generate_route_inventory.py --check

# 3. Verify zero broken links in PRD-4A LEV Todo
python3 -c "
from pathlib import Path; import re
p = Path('docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_todo.md')
broken = [m.group(1) for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', p.read_text()) if not (p.parent / m.group(2).split('#')[0]).exists() and not m.group(2).startswith('http')]
print('Broken links in LEV todo:', len(broken))
"

# 4. Verify test suite speedup (92s -> 15s)
pytest -c pytest.ini tests/unit/test_docs_intelligence.py -q --no-cov --tb=short

# 5. Verify diff-stat hygiene
git diff --check
```

| Check | Tool / Command | Acceptance Gate |
|---|---|---|
| Runaway File Bloat | `ls -lh docs/release/backend_deletion_candidate_inventory.md` | Size < 500 KB (currently 197 KB) |
| Link Integrity | `python3 scripts/maintenance/check_doc_links.py --root . --changed-only` | 0 broken links |
| Route Inventory | `.venv/bin/python scripts/generate_route_inventory.py --check` | 0 route drift |
| OpenAPI Spec | `.venv/bin/python scripts/generate_openapi.py --check` | 0 openapi drift |
| Inventory Reproducibility | `python3 scripts/maintenance/check_doc_inventory_reproducible.py --root .` | Clean exit (0 drift) |
| Source of Truth | `python3 scripts/maintenance/check_doc_source_of_truth.py --root .` | Exactly 24 canonical sections |
| Test Suite Speed | `pytest tests/unit/test_docs_intelligence.py` | Total runtime < 20 seconds |
