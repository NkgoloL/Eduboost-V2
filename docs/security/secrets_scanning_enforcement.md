# Secrets Scanning Enforcement

**Status:** RR-006 control policy

## Required controls

Secrets scanning must be visible in two places:

1. local pre-commit via `.pre-commit-config.yaml`; and
2. CI via GitHub Actions.

## Required tool baseline

The current baseline tool is `detect-secrets`. Equivalent tools may be added later, but removal of `detect-secrets` requires a signed security-control replacement note.

## Enforcement rule

New secrets findings must block release claims unless reviewed and allowlisted as false positives in a committed baseline.

## Boundary

This policy does not authorise production release, deployment, public beta, or runtime KG implementation.
