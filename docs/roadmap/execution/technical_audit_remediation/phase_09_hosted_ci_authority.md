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

## Status

`prepared_awaiting_real_hosted_ci_evidence`

This slice installs the hosted CI authority harness. It does **not** claim hosted
CI success until a real GitHub Actions run for the pushed commit is captured.

## Authority rules

1. Hosted CI success must be backed by a completed GitHub Actions run whose
   conclusion is `success` for the exact commit SHA under review.
2. A local verifier may pass with `--allow-unclaimed` only for the preparatory
   commit; that pass must not be described as hosted CI success.
3. Merge readiness is authorised only when:
   - hosted CI evidence is captured and verified, and
   - branch-protection evidence for the target branch is captured.
4. Evidence files must be recorded under
   `docs/release-evidence/technical-audit/phase-09-hosted-ci/` with SHA-256
   integrity coverage.

## Installed files

- `.github/workflows/technical-audit-hosted-ci.yml`
- `scripts/technical_audit/capture_hosted_ci_evidence.py`
- `scripts/technical_audit/verify_hosted_ci_authority.py`
- `docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json`
- `docs/release-evidence/technical-audit/phase-09-hosted-ci/SHA256SUMS.txt`

## Local preparatory verification

```bash
python scripts/technical_audit/verify_hosted_ci_authority.py --allow-unclaimed --json
```

Expected meaning: the repository is prepared and the no-false-claim contract is
valid. This is **not** hosted CI success.

## Capture real hosted CI evidence

After this commit is pushed and the GitHub Actions workflow succeeds:

```bash
python scripts/technical_audit/capture_hosted_ci_evidence.py \
  --repo OWNER/REPO \
  --branch "$(git branch --show-current)" \
  --sha "$(git rev-parse HEAD)" \
  --workflow "EduBoost Hosted CI Authority" \
  --require-success

python scripts/technical_audit/verify_hosted_ci_authority.py --json
```

If branch protection is required before merge readiness:

```bash
python scripts/technical_audit/capture_hosted_ci_evidence.py \
  --repo OWNER/REPO \
  --branch "$(git branch --show-current)" \
  --sha "$(git rev-parse HEAD)" \
  --workflow "EduBoost Hosted CI Authority" \
  --target-branch master \
  --require-success \
  --require-branch-protection
```

## Commit discipline

Recommended commit sequence:

1. `control(audit): add hosted CI authority harness`
2. Push branch and allow GitHub Actions to run.
3. Capture real hosted CI evidence.
4. `evidence(audit): record hosted CI run authority`
5. Only then move the blocker register to a closed/merge-ready state.
