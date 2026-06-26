# Documentation Governance Skill

Use this skill whenever creating, moving, reviewing, or approving EduBoost documentation.

## Required behavior

1. Check `docs/documentation/source_of_truth.yml` before creating a new document.
2. Prefer updating the existing canonical document over adding a parallel one.
3. Add complete YAML front matter to active documents.
4. Keep generated and evidence documents out of canonical reading paths unless they are explicitly registered.
5. Avoid unbounded readiness claims such as `production-ready`, `release-ready`, `fully complete`, or `all tests pass` unless the claim is scoped to a date, command, and evidence artifact.
6. Run `make docs-housekeeping-check` before committing.
7. Use `make docs-housekeeping-strict-check` to plan cleanup, not to claim current release readiness.

## Inventory reproducibility

Markdown files tracked through Git LFS must be inventoried by stable LFS identity, not by expanded local content. This preserves identical outputs between a git-lfs clone and a GitHub source ZIP.

## Stage 4 strict tranche

When editing `docs/architecture/`, `docs/product/`, `docs/api/`, `docs/compliance/`, or current `docs/security/` documents, run `make docs-housekeeping-stage4-check` in addition to the default housekeeping gate.
