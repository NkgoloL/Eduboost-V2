---
title: "Database Repository Evidence"
status: "current-evidence"
owner: "database"
reviewers: ["backend", "database", "release-management"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[alembic, app/repositories, scripts/validate_schema_integrity.py]"
---

# Database Repository Evidence

This index links migration graph, schema integrity, transaction/repository, and
repository-pattern evidence.

- Migration graph: `scripts/verify_migration_graph.py`
- Schema integrity: `scripts/validate_schema_integrity.py`
- Migration smoke command: `scripts/smoke_test_migrations.sh`
- Repository docs: `docs/reference/repositories.md`
- Repository tests: `tests/unit/test_v2_repository_patterns.py` and
  `tests/unit/test_v2_repositories_full.py`

Run:

```bash
make db-repository-check
```

Verification gaps: disposable PostgreSQL migration smoke, transaction rollback
tests for every high-risk workflow, and production-like data volume tests.
