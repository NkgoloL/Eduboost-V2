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
