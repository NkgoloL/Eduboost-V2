---
title: TA Phase 08 — Remote CI / Branch Integration Authority
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# TA Phase 08 — Remote CI / Branch Integration Authority

**Status:** Ready for controlled execution  
**Scope:** Static branch-integration authority and optional hosted-CI status capture.  
**Boundary:** This slice does not claim release readiness, remote GitHub Actions success, full backend-backed E2E readiness, or runtime knowledge-graph implementation.

## Purpose

Phase 08 ties together the previously recorded technical-audit authority gates into a single branch-integration control point. It verifies that the remediation branch carries valid evidence for:

- backend-fast authority,
- frontend/tooling authority,
- CI workflow static authority,
- dependency-scan enforcement,
- E2E / Playwright execution authority,
- OpenAPI / frontend contract finalization.

It also records whether hosted remote CI success is being claimed. By default, the answer is **no** unless an explicit remote CI status artifact is supplied.

## Authority commands

```bash
python3 scripts/audit_remediation/verify_remote_ci_branch_integration_authority.py --json
bash scripts/audit_remediation/collect_remote_ci_branch_integration_evidence.sh
python3 scripts/audit_remediation/verify_remote_ci_branch_integration_evidence.py \
  --evidence-dir docs/release-evidence/technical-audit/remote-ci-branch-integration \
  --json
```

## Optional remote CI status artifact

To claim hosted CI success, provide a JSON file via `REMOTE_CI_STATUS_JSON` when collecting evidence:

```bash
REMOTE_CI_STATUS_JSON=var/audit-remediation/remote-ci-status.json \
  bash scripts/audit_remediation/collect_remote_ci_branch_integration_evidence.sh
```

The file must include at least:

```json
{
  "remote_ci_run_claimed": true,
  "conclusion": "success",
  "head_sha": "<commit sha>",
  "workflow": "<workflow name or id>"
}
```

If this file is not supplied, the evidence remains valid as static branch-integration authority but records `remote_ci_run_claimed: false`.

## Exit criteria

Phase 08 may be closed when:

1. `verify_remote_ci_branch_integration_authority.py --json` returns `valid: true`.
2. The evidence collector produces `docs/release-evidence/technical-audit/remote-ci-branch-integration`.
3. `verify_remote_ci_branch_integration_evidence.py` returns `valid: true`.
4. The blocker register is updated in a separate control commit.

