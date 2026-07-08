# PRD-1.0 — CI/Release-Gate Stream Authority and Register

**Stream:** PRD-1 — Required CI and Release Gate Convergence  
**Status:** Authority slice; evidence capture required for closure  
**Owner:** Nkgolo Lebelo  
**Canonical trunk:** `master`

---

## Purpose

PRD-1.0 establishes the authority layer for PRD-1 after the PRD-0.10 handoff.

It creates the PRD-1 sub-slice register, records the PRD-1 execution sequence, and confirms that PRD-1 is limited to CI and release-gate convergence until later PRDs authorise product runtime, beta, billing, or production release work.

---

## PRD-1 goal

Make CI production-reliable by converging required checks, release workflow semantics, branch protection evidence, and release-gate authority.

---

## PRD-1 controlled sequence

1. PRD-1.0 — CI/release-gate stream authority and register.
2. PRD-1.1 — CI inventory authority.
3. PRD-1.2 — Required check classification.
4. PRD-1.3 — Workflow canonicalisation.
5. PRD-1.4 — Release gate definition.
6. PRD-1.5 — CI convergence evidence.
7. PRD-1.6 — Release readiness register.
8. PRD-1.7 — Authority reconciliation.
9. PRD-1.8 — Final evidence capture.
10. PRD-1.9 — Controlled handoff to PRD-2 Runtime KG Integration and Persistence.

---

## Explicit boundary

PRD-1.0 does not modify CI workflows, enforce branch protection, standardise pytest calls, remove stale workflows, reconcile OpenAPI files, define release gates, capture CI convergence, create release tags, deploy, open beta/live learner traffic, launch billing, process live payments, or implement runtime KG work.

Those actions are reserved for later PRD-1.x slices or later major PRDs.

---

## Closure condition

Before evidence capture, the verifier must report `authority_valid: true` and `valid: false`.

After evidence capture, the verifier must report `authority_valid: true`, `valid: true`, and `next_authorised_item: PRD-1.1`.
