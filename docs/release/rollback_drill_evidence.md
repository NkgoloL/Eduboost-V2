# Rollback Drill Evidence

**Status:** pending runtime execution

This file records proof that the release can be rolled back or safely halted.

## Required environment

| Field | Value |
|---|---|
| Environment | TODO |
| Release candidate SHA | TODO |
| Previous stable SHA/tag | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required checks

| Check | Expected result | Evidence |
|---|---|---|
| Application rollback command | succeeds | TODO |
| Database rollback/downgrade decision | succeeds or non-downgrade rationale documented | TODO |
| Config rollback | previous config restored or not required | TODO |
| Post-rollback health | health endpoint passes | TODO |
| User-impact note | documented | TODO |

## Command log

```bash
# paste commands and output here
```

## Decision

- [ ] Rollback drill passed.
- [ ] Rollback drill failed and release is blocked.
