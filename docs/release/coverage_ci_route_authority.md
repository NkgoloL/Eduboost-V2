# Coverage, CI, and Route Authority

**RR item:** RR-003  
**Status:** authority installed / evidence pending

## Coverage baseline required

A release or beta-readiness claim must not use stale coverage numbers. Current coverage must be regenerated from the target commit and recorded in RR-003 evidence.

The coverage threshold is established by the RR-003 evidence record. Once recorded, future release claims must not reduce the threshold without an explicit exception record.

## Release-blocking checks visible in CI

Release-authority checks must be visible as CI workflow steps. At minimum, the RR-003 workflow exposes:

- `make test-fast`
- `make route-alias-policy-check`
- `make openapi-check`
- `python3 scripts/roadmap_reconciliation/verify_rr003_coverage_ci_route_authority.py --json`

## Route-prefix authority

`/api/v2` is canonical.

`/v2` is compatibility-only.

The route alias matrix is the controlling artifact for compatibility aliases. New missing aliases require explicit route alias exceptions and reviewer approval.

## Dormant routers must be inventoried

Dormant or specialist routers must be inventoried before retirement or archival. Retirement is not performed by this slice.

## Boundary

This authority does not authorise production release, deployment, public beta, release tagging, runtime KG implementation, or expanded learner traffic.
