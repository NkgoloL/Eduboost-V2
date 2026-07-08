# PRD-1.2-1.4 Required Checks, Workflow Canonicalisation, and Release Gate Definition

**Status:** authority prepared; evidence capture records completion.  
**Merged slices:** PRD-1.2 Required Check Classification; PRD-1.3 Workflow Canonicalisation; PRD-1.4 Release Gate Definition.  
**Next authorised item after evidence:** PRD-1.5 — CI Convergence Evidence.

This consolidated slice reduces PRD-1 process overhead. It replaces three tiny governance slices with one implementation-focused slice that records the required-check classification, performs safe workflow command canonicalisation, reconciles the OpenAPI authority path, and defines the release gate baseline.

## Implementation performed

- Standardise workflow/Makefile pytest invocations from `python -m pytest` to `python3 -m pytest`.
- Classify required, advisory, and release-candidate-blocking checks.
- Confirm `docs/openapi.json` remains the canonical OpenAPI artifact and `openapi.json` remains a compatibility mirror.
- Define the master/release gate baseline without modifying hosted branch protection.

## Boundary

This slice does **not** enforce GitHub branch protection, does **not** create release tags, does **not** deploy, does **not** authorise public beta or live learner traffic, and does **not** start PRD-2 runtime KG implementation.

PRD-1.5 must capture convergence evidence before required checks can be treated as production-reliable.
