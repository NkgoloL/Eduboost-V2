# PR Integration Summary

**Document status:** Restored  
**Restored on:** 2026-05-12  
**Restoring commit:** _(fill in after commit)_  
**Required by:**
- `tests/unit/test_pr002r_docs_contract.py`
- `tests/unit/test_pr002r_evidence_check.py`
- `scripts/check_pr002r_evidence.py`

## Verification References

- **Evidence document:** [docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md](file:///home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md)
- **Contract test:** [tests/unit/test_pr002r_docs_contract.py](file:///home/nkgolol/Dev/SandBox/dev/Eduboost-V2/tests/unit/test_pr002r_docs_contract.py)

---

## Purpose

This document records the integration outcome for **PR-002R** (the V2
runtime and API contract baseline merge).  It exists so that automated
evidence scripts can verify that the PR was integrated, reviewed, and
that its documented state matches the repository's current posture.

If the PR is no longer relevant or has been superseded, retire this file
by replacing its content with the retirement notice at the bottom of this
template (do not simply delete it – the evidence scripts check for the
file's existence).

---

## PR Reference

| Field | Value |
|---|---|
| PR identifier | PR-002R |
| Branch merged | `feature/v2-runtime-baseline` → `master` |
| Merge commit | _(fill in)_ |
| Merged by | _(fill in)_ |
| Merge date | _(fill in)_ |
| Reviewed by | _(fill in)_ |

---

## Integration Scope

PR-002R established:

1. **Canonical V2 runtime entrypoint** – `app.api_v2:app` replacing the
   legacy `app.legacy.api.main:app` as the primary development surface.
2. **OpenAPI contract baseline** – `docs/openapi.json` generated and
   committed; drift check added to CI (`make openapi-check`).
3. **Route inventory baseline** – `docs/route_inventory.md` generated and
   committed; inventory check added to CI (`make route-inventory-check`).
4. **Compatibility shim preserved** – `app/legacy/api/main.py` retained as
   an import shim for controlled migration; marked `DEPRECATED.md`.
5. **143 V2 routes / 144 legacy routes** verified at merge time via
   `make runtime-check`.

---

## Evidence Checklist

The following evidence items were present and passing at merge time.
Update each row when re-verified after subsequent changes.

| Evidence item | Status at merge | Re-verified date |
|---|---|---|
| `make runtime-check` passed | ✅ | _(fill in)_ |
| `make openapi-check` passed | ✅ | _(fill in)_ |
| `make route-inventory-check` passed | ✅ | _(fill in)_ |
| Import smoke: `app.api_v2` | ✅ | _(fill in)_ |
| Import smoke: `app.repositories.lesson_repository` | ✅ | _(fill in)_ |
| Import smoke: `app.repositories.diagnostic_repository` | ✅ | _(fill in)_ |
| Import smoke: `app.repositories.assessment_repository` | ✅ | _(fill in)_ |
| Unit gate (`pytest tests/unit -m "not llm and not e2e"`) | ⚠️ 18 failures at assessment | _(fill in after Rec 1 & 2 applied)_ |
| Frontend lint/type/test loop | ✅ | _(fill in)_ |

---

## Known Issues At Merge

The following issues were present at merge time and are tracked separately:

- 18 unit test failures (post-merge contract regressions) – see
  Recommendation 1 & 2 from `docs/technical_state_report_2026-05-12.md`.
- 16 unit setup errors from DB-dependent item-bank tests – resolved by
  Recommendation 1 (skip-on-unavailable fixture).
- `PR_INTEGRATION_SUMMARY.md` was absent from the initial merge – this
  file is the corrective artifact.

---

## Post-Merge Actions Required

- [ ] Apply Recommendation 1: fix item-bank DB fixture (skip not error).
- [ ] Apply Recommendation 2: reconcile Cluster G E2E evidence checks.
- [ ] Apply Recommendation 4: remove duplicate Makefile targets.
- [ ] Sync local checkout to `origin/master` (4 commits behind at assessment).
- [ ] Re-run full local verification story and update evidence table above.
- [ ] Refresh `docs/current_state.md` once all regressions are resolved.

---

## Retirement Notice (use this block if PR-002R evidence is superseded)

<!--
## RETIRED

This PR integration summary has been retired as of YYYY-MM-DD.
Superseded by: [link to replacement evidence document]
The file is retained for historical audit trail purposes only.
Evidence scripts should be updated to reference the replacement document.
-->
