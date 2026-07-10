# PRD-11.0R.RUNTIME-RESTORE-4 — Product Gate Execution and Critical Flow Repair

## Purpose

RESTORE-4 defines the critical product flows that must be executed before EduBoost can claim restored runtime/product readiness.

## Scope

- Product critical-flow execution matrix.
- Positive and negative evidence requirements.
- Independent command output requirements.
- Explicit blocker state for product gates that are not yet green.
- Handoff to RESTORE-5 for coverage execution/security/advisory gate repair.

## Boundary

This slice does not claim product readiness.  It records the execution contract and evidence capture shape while keeping `product_gate_green=false`, `runtime_baseline_green=false`, and `controlled_beta_activation_operational_hold=true`.
