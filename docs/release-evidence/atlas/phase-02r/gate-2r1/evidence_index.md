# Phase 2R Gate 2R.1 Evidence Index

**Generated:** 2026-06-18T11:00:00Z
**Status:** Candidate — Implementation Complete, Pending Independent Approvals

## Implementation

| Artifact | Path | Description |
|---|---|---|
| Implementation commit | `e832302f7c40cd2d3125b56b9e14fda3f6f5b281` | Source authority model, rights policy, migration, verification scripts, test suites |
| Evidence commit | `05bf52c31160f5a99420b4a0fdb8a12b8b970cae` | Source completeness register, evidence index, approvals manifest |
| Migration graph | `alembic/versions/20260616_1200_phase02r_authority_controls.py` | Phase 2R authority, rights, inventory, and review ledger tables |
| Authority model | `app/models/curriculum_authority.py` | 12 ORM classes: AuthorityTier, RightsDecisionStatus, InventoryStatus, CurriculumSource, CurriculumSourceVersion, CurriculumRightsDecision, CurriculumInventoryVersion, CurriculumInventoryItem, CurriculumReviewDecision |
| Rights policy | `app/services/curriculum/rights_policy.py` | Fail-closed RightsPolicyEngine with 14 use-type permissions and structured conditions |

## Source Completeness

| Artifact | Path | Status |
|---|---|---|
| Register (version 2) | `data/curriculum/registries/grade4_mathematics_caps_source_completeness.json` | Draft — 8 items (6 located, 2 absence_approved) |
| Validator | `scripts/curriculum/validate_source_completeness_register.py` | PASS |
| Unit tests | `tests/unit/phase02r/` | 15/15 PASS |

## Verification

| Check | Result |
|---|---|
| `verify_phase02r.sh --gate 2R.1 --mode implementation` | PASS (8/8) |
| `verify_phase02r_gate2r1.py --mode implementation` | PASS |
| `phase02r_gate_control.py --expected-authorised-gate 2R.1` | valid: true |
| `verify_phase02r_postgres.sh` | PASS (3/3 tests, migration graph OK, schema integrity OK) |
| Target SHA256 hashes | 38/38 OK |
| `git diff --check` | exit: 0 |
| `git diff --cached --check` | exit: 0 |

## Approval

| Role | Domain | Decision |
|---|---|---|
| Engineering Approver | Implementation | Pending |
| Rights Reviewer | Rights | Pending |
| Curriculum Reviewer | Inventory Completeness | Pending |
| Evidence Custodian | Evidence Integrity | Pending |
| Release Manager | Gate Transition | Pending |

*See `docs/roadmap/execution/atlas/phase_02r_gate_2r1_approvals.json` for the signed record.*
