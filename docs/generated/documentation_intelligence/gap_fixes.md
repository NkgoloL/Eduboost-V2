# Gap Fixes & Proposed Evidence Links

Generated: 2026-05-19T08:40:00Z

This file maps high-priority gaps from `docs_gap_report.md` to candidate source artifacts (from the inventory and sanity checks) that can serve as evidence or content to close the gap.

## System Overview

Missing/needs refinement:
- Deployment diagram
- ADR links for some major decisions
- Production-readiness evidence links

Candidate evidence to attach or embed:

- Inventory / synthesis: `docs_inventory.md`, `docs/generated/documentation_intelligence/docs_inventory.md`
- Deployment infra: `bicep/main.bicep`, `bicep/container_apps.bicep`, `k8s/`, `docker-compose.yml`, `nginx/`
- Privacy / consent: `docs/adr/0002-popia-first-design.md`
- Observability & backup: `docs/adr/ADR-011-observability-stack.md`, `docs/adr/ADR-013-backup-restore-disaster-recovery.md`
- Release readiness: `docs/adr/ADR-014-testing-release-evidence-quality-gates.md`, `docs/adr/ADR-020-final-release-blocker-checklist.md`
- Task matrices: `docs/backlog/task_matrix_pr004.csv`, `docs/compliance/task_matrix.csv`

## Suggested next actions (automation-friendly)

1. For each Production Readiness checklist item in `docs_gap_report.md`, attach the best matching evidence file listed above.
2. Create ADRs for any major decisions missing ADRs (put under `docs/adr/` and link from `system_overview.md`).
3. Iterate the Mermaid diagrams using the infra sources (Bicep, k8s) and commit updated diagrams under `docs/generated/documentation_intelligence/diagrams/`.
4. Re-run `scripts/docs_inventory.py` after ADR additions to pick up new ADRs and regenerate the sanity checks.

If you want, I can open a PR with these edits and the new files, and tag the reviewers. Reply with "Create PR" to proceed.
