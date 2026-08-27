# Architectural Debt Register (TSR-6.1)

## Overview
This document records all architectural debt, oversized modules, legacy boundaries, import exceptions, and complexity hotspots tracked across EduBoost V2.

## Remediated Debt Items in Bundle B04
1. **Router-to-Repository Separation (`DEBT-001` / TSR-6.7):**
   - Eliminated all direct repository imports from `app/api_v2_routers` and module routers.
   - Enforced zero exceptions in `.importlinter` and verified with `scripts/true_state_remediation/check_router_repo_isolation.py`.
2. **Legacy Quarantine Boundary (`DEBT-003` / TSR-6.12):**
   - Enforced import linter contract preventing any imports from `app.legacy` into `app.core` or `app.domain`.
3. **Content Factory Decomposition (`DEBT-002` / TSR-6.2):**
   - Established capability boundaries across generation, staging verification, review, and promotion.
4. **ETL Interface Consolidation (`DEBT-004` / TSR-6.3):**
   - Consolidated ETL entrypoints and documented migration interfaces.
5. **Exception Taxonomy & Dispositions (`DEBT-005` / TSR-6.8, TSR-6.15):**
   - Established typed error taxonomy preventing silent degraded 200 responses.
