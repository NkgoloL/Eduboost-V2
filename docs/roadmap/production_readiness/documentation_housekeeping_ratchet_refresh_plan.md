# Documentation Housekeeping Ratchet Refresh Plan

**Owner:** Nkgolo Lebelo  
**Stream:** PRD-PRODUCTION-READINESS  
**Slice:** PRD-0.3

## Refresh sequence

1. Regenerate deterministic documentation inventory outputs.
2. Refresh the housekeeping ratchet baseline from the regenerated inventory.
3. Run the housekeeping ratchet check against the refreshed baseline.
4. Capture inventory summary and baseline snapshots in PRD-0.3 evidence.
5. Advance the production-readiness register to PRD-0.4.

## Commands used by evidence capture

```bash
PYTHONPATH=. python3 scripts/maintenance/check_doc_inventory_reproducible.py --root . --update
PYTHONPATH=. python3 scripts/maintenance/update_doc_housekeeping_baseline.py --root . --note "PRD-0.3 baseline captured after post-closure documentation authority refresh."
PYTHONPATH=. python3 scripts/maintenance/check_doc_housekeeping_ratchet.py --root .
```

## Non-goals

This plan does not claim that documentation debt is eliminated. It records the current post-closure ratchet baseline so later cleanup work can prevent regression and reduce debt deliberately.
