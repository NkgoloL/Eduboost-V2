# Database Restore Drill

## Purpose

Restore drills prove that backup artifacts can recover learner data, consent
records, audit records, and operational state into a controlled environment.

## Drill Preconditions

- backup artifact is encrypted
- restore target is non-production unless explicitly approved
- production secrets are loaded from Key Vault
- restore operator records source backup ID and target environment

## Required Drill Steps

1. Capture source backup metadata.
2. Restore into an isolated database.
3. Run schema migrations.
4. Verify learner record counts.
5. Verify consent record counts.
6. Verify audit event counts.
7. Run runtime and consent closure checks.
8. Record restore duration, checksum/integrity status, and operator.

## Required Verification Commands

```bash
make runtime-check
make route-inventory-check
make popia-consent-closure-check
make cluster-d-closure-check
```

## Evidence Record

Each restore drill must attach:

- backup artifact ID
- restore target
- command output
- integrity status
- operator and timestamp
