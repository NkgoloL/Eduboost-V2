---
title: Complexity Budgets and Dispositions
status: active
owner: architecture
reviewers: [engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-03
review_interval_days: 60
evidence_command: make docs-housekeeping-check
code_anchors: [docs/architecture/complexity_budgets_and_dispositions.md]
---

# Complexity Budgets and Dispositions (TSR-6.14, TSR-6.15, TSR-6.17)

## Budgets & Quality Gates
1. **Router Layer:** Maximum 150 lines per file; zero direct repository calls; zero raw SQL queries.
2. **Service Layer:** Single-responsibility; explicit typed parameters; explicit transaction management.
3. **Exception Taxonomy:**
   - Client errors: `HTTPException(400..404)` with standard envelope `{status, code, message}`.
   - Authorization errors: `HTTPException(401/403)`.
   - Domain errors: Typed custom exceptions inheriting from `EduBoostException`.
   - System/Unhandled errors: Logged with tracebacks; return `HTTPException(500)` fail-closed.
