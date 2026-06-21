# Phase 2R Implementation Report

**Report status:** In Progress
**Current gate:** 2R.1
**Next gate:** Blocked
**Plan version:** 1.5

**Update:** The Phase 2R Gates 2R.2-2R.8 implementation patch has now been applied on the current worktree. It adds the later-gate grounding models, services, verifier scripts, and migration scaffolding, but it does not change the Gate 2R.1 control posture.

**2026-06-21 remediation update:** Gate 2R.1 now has implementation-level PostgreSQL proof for the authority migration, append-only triggers, frozen source-completeness register, and real first-slice source authority/per-use rights load. This is not closure evidence yet because the clean-worktree candidate evidence pack, separate evidence commit, independent approvals, and separate Gate 2R.2 authorisation commit are still pending.

## Gate 2R.1 implementation reconciliation

| Work item | Actual implementation | Current disposition |
|---|---|---|
| P02R-0101 | Added `curriculum_sources`, `curriculum_source_versions`, `curriculum_rights_decisions`, `curriculum_inventory_versions`, `curriculum_inventory_items`, and `curriculum_review_decisions`; added Alembic revision `20260616_1200_phase02r_authority` and append-only triggers. | Implemented; disposable PostgreSQL upgrade/downgrade, schema, and append-only update/delete proof passed on 2026-06-21. Clean candidate evidence pending. |
| P02R-0102 | Added explicit per-use rights fields, separate translation/publication permissions, structured conditions, expiry checks, and a default-deny policy engine. Added `scripts/curriculum/load_phase02r_authority_records.py` to load the verified first-slice source version and per-use rights decision. | Implemented; real first-slice source-version rights decision loaded in disposable PostgreSQL proof. Independent rights approval pending. |
| P02R-0103 | Added the bounded Grade 4 Mathematics CAPS source-completeness register and deterministic structural/freeze validator. | Implemented; register frozen on 2026-06-21 with manifest SHA-256 `5618eee3dddae46ae4543eab45b5b4df2b560ba2bd430d1f076462d3c250e3e0`. Clean candidate evidence pending. |
| P02R-0104 | Added an independent append-only review-domain ledger and policy checks preventing one review domain from satisfying another. | Implemented; independent Gate 2R.1 approvals remain pending. |

## Governance corrections

- Reverted the premature control transition to `approved_gate=2R.0` and `authorised_next_gate=2R.1`.
- Marked the earlier dirty-worktree Gate 2R.1 evidence as superseded.
- Changed the collector to require a clean Git worktree and to emit candidate evidence only.
- Added separate implementation and closure verification modes.
- Added gate-state validation that prevents a transition to unsupported automation or a contradictory plan/evidence state.
- Added a pending Gate 2R.1 approval record; no reviewer decision is fabricated by this patch.
- Applied the later-gate implementation bundle for Gates 2R.2-2R.8 while keeping Gate 2R.1 as the only authorised gate.

## Files added

- `app/models/curriculum_authority.py`
- `app/services/curriculum/rights_policy.py`
- `alembic/versions/20260616_1200_phase02r_authority_controls.py`
- `data/curriculum/registries/grade4_mathematics_caps_source_completeness.json`
- `scripts/phase02r_gate_control.py`
- `scripts/validate_phase02r_authority_schema.py`
- `scripts/curriculum/load_phase02r_authority_records.py`
- `scripts/curriculum/validate_source_completeness_register.py`
- `tests/unit/phase02r/`
- `alembic/versions/20260618_1200_phase02r_grounding_controls.py`
- `app/models/curriculum_grounding.py`
- `app/services/curriculum/acquisition.py`
- `app/services/curriculum/answer_verification.py`
- `app/services/curriculum/claim_validation.py`
- `app/services/curriculum/corpus.py`
- `app/services/curriculum/evaluation.py`
- `app/services/curriculum/extraction.py`
- `app/services/curriculum/graph.py`
- `app/services/curriculum/grounding.py`
- `app/services/curriculum/legacy.py`
- `app/services/curriculum/phase02r_verification.py`
- `app/services/curriculum/tutor_grounding.py`
- `scripts/verify_phase02r_gate2r2_to_2r8.py`
- `tests/unit/phase02r/test_gate2r2_to_2r8_services.py`
- `tests/unit/phase02r/test_grounding_models.py`

## Remaining Gate 2R.1 closure work

1. Commit the implementation proof changes so the worktree is clean.
2. Collect candidate evidence from the clean committed source state.
3. Commit evidence separately.
4. Record independent rights, source-authority, inventory-completeness, evidence, and release approvals.
5. Only after approvals pass, issue a separate gate-transition commit that authorises Gate 2R.2.

Gate 2R.2 remains blocked until all items above pass.
