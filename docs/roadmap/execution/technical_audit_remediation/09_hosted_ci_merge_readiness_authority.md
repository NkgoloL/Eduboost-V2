---
title: TA Phase 09 — Hosted CI Run Evidence / Merge Readiness Authority
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

# TA Phase 09 — Hosted CI Run Evidence / Merge Readiness Authority

**Status:** Ready for controlled execution  
**Scope:** Hosted CI evidence and branch merge-readiness authority  
**Boundary:** remote CI success is not inferred. release readiness is not claimed. Runtime KG implementation is not introduced.

## Objective

Phase 09 turns the completed static authority gates into a hosted-CI merge-readiness control. It requires a real hosted CI success artifact whose `head_sha` matches the branch HEAD before the evidence verifier can pass.

This phase intentionally separates three claims:

1. Static/local authority gates are present and previously evidenced.
2. Hosted CI has passed for the exact branch HEAD.
3. Release readiness is approved.

Only the first two are in scope. Release readiness remains out of scope.

## Authority commands

```bash
python3 scripts/audit_remediation/verify_hosted_ci_merge_readiness_authority.py --json
bash scripts/audit_remediation/collect_hosted_ci_merge_readiness_evidence.sh
python3 scripts/audit_remediation/verify_hosted_ci_merge_readiness_evidence.py \
  --evidence-dir docs/release-evidence/technical-audit/hosted-ci-merge-readiness \
  --json
```

To claim hosted CI success, the collector must be given a real status artifact:

```bash
REMOTE_CI_STATUS_JSON=var/audit-remediation/hosted-ci-status.json \
  bash scripts/audit_remediation/collect_hosted_ci_merge_readiness_evidence.sh
```

Required hosted CI artifact shape:

```json
{
  "remote_ci_run_claimed": true,
  "conclusion": "success",
  "head_sha": "<branch HEAD sha>",
  "workflow": "<workflow name or id>",
  "run_id": "<run id or number>",
  "run_url": "<optional hosted run URL>"
}
```

## Evidence policy

The evidence verifier fails closed unless:

- all prior authority evidence checks are valid;
- the working tree was clean before evidence collection;
- hosted CI success is explicitly claimed;
- hosted CI `conclusion` is `success`;
- hosted CI `head_sha` matches the collected branch HEAD;
- the evidence bundle hash manifest is internally consistent.

A diagnostic bundle may be generated without hosted CI success, but it must not be committed as passing Phase 09 evidence.

## Out of scope

- Full production release readiness.
- Full backend-backed E2E readiness beyond already recorded Playwright static authority.
- Any runtime KG implementation.
- Security vulnerability remediation beyond the already closed dependency-scan enforcement gate.
