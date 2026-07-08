# PRD-1 CI and Release Gate Convergence

PRD-1 exists to make CI production-reliable after PRD-0 closed the current-state authority refresh.

## Carried-in facts from PRD-0

- Canonical trunk: `master`.
- Legacy `main` references are compatibility/historical unless explicitly reconciled.
- `release/**` branches are reserved naming patterns, not release authority.
- Generated/local artifact cleanup remains audit-only unless explicitly authorised.
- Production release, deployment, beta, live learner traffic, billing, live payment processing, and new KG scope remain blocked.

## PRD-1 implementation boundary

PRD-1 may only converge CI and release-gate authority. Runtime KG implementation is reserved for PRD-2. Learner/parent journey hardening is reserved for PRD-3. Content quality readiness is reserved for PRD-4. POPIA live data operations are reserved for PRD-5. Security assurance is reserved for PRD-6. SRE readiness is reserved for PRD-7. Scale/cost execution is reserved for PRD-8. Billing is reserved for PRD-9. Controlled beta is reserved for PRD-10. Production release/deployment is reserved for PRD-11.
