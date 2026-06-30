# Cluster D Closure Check

## Purpose

`make cluster-d-closure-check` is the aggregate command for CI, deployment, and
environment-gate evidence.

## Included Checks

- environment security contract
- production placeholder-secret guard
- production Key Vault behavior tests
- dev-only endpoint exposure guard
- deployment readiness documentation
- Cluster D CI evidence

## Command

```bash
make cluster-d-closure-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_cluster_d_closure_check.py -q --no-cov
```
