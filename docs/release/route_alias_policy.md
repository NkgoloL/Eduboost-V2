# EduBoost V2 Route Alias Policy

`/api/v2` is the canonical API prefix.

`/v2` is a compatibility alias for clients and tests that still use the shorter historical prefix.

## Enforcement

Every canonical `/api/v2/...` route must either:

1. have a matching `/v2/...` route for the same HTTP method, or
2. be listed in `docs/release/route_alias_exceptions.txt` with an explicit reason.

## Commands

Generate the matrix:

```bash
make route-alias-matrix
```

Check the policy:

```bash
make route-alias-policy-check
```

Write the current baseline of known exceptions:

```bash
python3 scripts/check_route_alias_matrix.py --write-baseline
```

## Review rule

New missing aliases are release-impacting unless the reviewer accepts an explicit exception.
