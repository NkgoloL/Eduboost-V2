# Cluster E Closure Check

## Purpose

`make cluster-e-closure-check` is the aggregate command for data-resilience
backup/restore evidence.

## Included Checks

- database backup contract
- database restore drill documentation
- backup dry-run command scaffold
- restore dry-run command scaffold
- backup manifest generation
- restore evidence generation
- backup integrity verification
- restore integrity verification
- Cluster E evidence aggregation

## Command

```bash
make cluster-e-closure-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_cluster_e_closure_check.py -q --no-cov
```
