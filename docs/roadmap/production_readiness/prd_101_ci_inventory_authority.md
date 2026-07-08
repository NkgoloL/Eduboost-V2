# PRD-1.1 — CI Inventory Authority

**Stream:** PRD-1 — Required CI and Release Gate Convergence  
**Status:** Inventory authority slice; evidence capture required for closure  
**Owner:** Nkgolo Lebelo  
**Canonical trunk:** `master`

---

## Purpose

PRD-1.1 creates the authoritative CI inventory baseline for PRD-1.

It inventories workflow files, workflow trigger references, pytest command forms, branch-name references, release/deployment references, OpenAPI artifact references, Makefile CI targets, and branch-protection/required-check documentation references.

---

## Boundary

PRD-1.1 is inventory-only.

It does not classify required checks, canonicalise workflows, modify CI commands, edit branch protection, enforce release gates, reconcile OpenAPI artifacts, create release tags, deploy, open public beta, permit live learner traffic, launch billing, process live payments, or implement PRD-2 runtime KG work.

---

## Next slice

The next authorised slice after PRD-1.1 evidence capture is:

`PRD-1.2 — Required Check Classification`

PRD-1.2 will use this inventory to classify checks as required, advisory, stale, legacy, release-only, blocked, or deferred.

---

## Closure condition

Before evidence capture, the verifier must report `authority_valid: true` and `valid: false`.

After evidence capture, the verifier must report `authority_valid: true`, `valid: true`, and `next_authorised_item: PRD-1.2`.
