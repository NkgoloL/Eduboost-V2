# Beta Evidence Integrity Repair Report

Generated at: `2026-05-17T12:12:51Z`

## Summary

This repair quarantines placeholder/manual-bypass/local-mock/synthetic evidence and restores truthful beta readiness semantics.

| Gate | Previous status | Repaired status | Source type | Integrity |
|---|---|---|---|---|
| remote_ci | pending_remote_ci_evidence | pending_remote_ci_evidence | unknown | pending_real_evidence |
| branch_protection | pending_branch_protection_evidence | pending_branch_protection_evidence | unknown | synthetic_invalid |
| content_gate | blocked | blocked | unknown | pending_real_evidence |
| staging_smoke | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| backup_drill | pending_backup_evidence | pending_backup_evidence | unknown | pending_real_evidence |
| restore_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| rollback_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| alertmanager_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |

## Release rule

Beta readiness is blocked unless every required gate has trusted real evidence or an explicit approved waiver for the content gate only.
