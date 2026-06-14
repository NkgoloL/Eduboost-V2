# Agent Memory & Behavioral Directives

This document serves as persistent memory and operational directives to ensure high standards of verification, accuracy, and thoroughness in all work.

## Directive 1: Never Over-Hype or Prematurely Claim Completion

- **Do not claim a phase or feature is "closed" or "complete" if there are lingering inconsistencies, permissions issues, or mismatched paper trails.**
- The presence of passing tests is not the sole definition of "complete." Operational ergonomics (like executable scripts) and documentation integrity (like execution plans matching the implemented scope) are equally critical.
- Always cross-reference the implementation with its associated roadmap and execution plans. If the documentation describes an outdated scope or architecture, the phase is **not complete** until the documentation is reconciled with the codebase.
- Avoid bypassing the *real* implementation details by only checking happy paths. Thoroughness requires verifying edge cases, infrastructure readiness (like executable bits on shell scripts), and ensuring that the entire lifecycle (plan → implementation → audit) is internally consistent.

## Directive 2: Documentation & Control Set Integrity

- Before finalizing a phase, ensure that there are no duplicate or conflicting documents (e.g., old `phase_2_execution_plan.md` vs new `phase_02_execution_plan.md`).
- A phase's paper trail (execution plan, implementation report, evidence index, audit report) must faithfully and completely trace the implementation that was actually merged. Mismatched scopes weaken sign-off confidence and make future maintenance significantly harder.

## Directive 3: Repo Ergonomics

- Scripts intended for execution via `./scripts/...` MUST have the executable bit set (`chmod +x`). 
- Do not let subtle regression in repo ergonomics slip through just because a script works when manually invoked via `bash <script>`.
