# Documentation Governance Skill

Use this skill whenever creating, editing, moving, or reviewing EduBoost documentation.

## Purpose

Prevent documentation drift, stale release claims, duplicate source-of-truth documents, and generated-evidence sprawl.

## Rules

1. Read `docs/documentation/source_of_truth.yml` before creating or updating a document.
2. Decide whether the document is active, generated, evidence, draft, superseded, or archived.
3. Add YAML front matter with owner, audience, status, source-of-truth flag, review date, review interval, evidence command, and code anchors.
4. Do not create a second canonical document for an existing topic.
5. Use bounded evidence language for readiness, security, compliance, or release claims.
6. Archive old material with a manifest instead of silently deleting it.
7. Run `make docs-housekeeping-check` before committing documentation changes.

## Good output pattern

- Current status in one canonical document.
- Generated detail in `docs/generated/`.
- Evidence in `docs/release-evidence/` or `artifacts/evidence/`.
- Historical material in `docs/archive/`.
- A link from canonical docs to evidence, not copied evidence prose everywhere.
