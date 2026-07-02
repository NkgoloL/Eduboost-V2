# TA Phase 05 — Dependency Scan Enforcement

## Status

Implementation-ready. Evidence may be recorded only after the static dependency-scan enforcement verifier and evidence verifier are green.

## Purpose

Close the technical-audit dependency-scan blocker by making the dependency-scan workflow fail closed on configured vulnerability severity and publish stable evidence artifacts.

The original audit finding was that dependency scan failures could be suppressed and reporting/upload wiring was not reliable. This slice converts that concern into a checked workflow contract.

## Authority

```bash
python3 scripts/audit_remediation/verify_dependency_scan_enforcement.py --json
```

Evidence verifier:

```bash
python3 scripts/audit_remediation/verify_dependency_scan_evidence.py \
  --evidence-dir docs/release-evidence/technical-audit/dependency-scan-enforcement \
  --json
```

## Scope

In scope:

- `.github/workflows/dependency-scan.yml` static enforcement contract.
- Python `pip-audit` fail-closed shell behavior.
- Frontend `pnpm audit --audit-level=critical` fail-closed behavior.
- Dependency Review `fail-on-severity: critical` contract.
- Stable audit report artifact uploads with `actions/upload-artifact@v4`.
- Evidence collection and SHA256 integrity verification.

Out of scope:

- Claiming remote GitHub Actions dependency scans have run.
- Closing all vulnerabilities found by scans.
- Release readiness.
- Runtime knowledge-graph implementation.

## Evidence policy

Passing evidence must prove the dependency-scan verifier and evidence verifier both return `valid: true`, the SHA manifest is stable, and remote hosted scan success is not claimed.

## KG boundary

No runtime knowledge-graph implementation is included. KG remains a future architectural north star only.
