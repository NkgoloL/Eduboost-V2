# Archive

This directory holds code and tests that are no longer wired into the running
application but are preserved for git history and possible future reference.

## Contents

### `api_v2_routers/`
Dormant FastAPI routers that were never registered in `app/api_v2.py`:

- `ether.py` — onboarding "Ether" archetype prototype.
- `judiciary.py` — content moderation router.

These were archived in Phase 11 (Technical Debt Burn-Down, 2026-06-12) as part of
removing dead code from the working tree. They are NOT imported, NOT routed, and
NOT exposed publicly. If reintroduced, they must go through Phase 0 audit again.

### `tests/api/`
Tests that exclusively exercise the archived routers above:

- `test_ether_routes.py`
- `test_judiciary_routes.py`

These are kept here so the git history and original test intent remain
recoverable, but they are excluded from the active test suite.

## Restoration

To restore an archived file:

```bash
git mv archive/api_v2_routers/<file>.py app/api_v2_routers/<file>.py
```

Then re-register the router in `app/api_v2.py` and re-add any required
test fixtures.
