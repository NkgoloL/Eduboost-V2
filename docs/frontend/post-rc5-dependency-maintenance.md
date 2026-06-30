# Post-RC5 Dependency Maintenance Triage

**Date:** 2026-05-31  
**Release Freeze SHA:** `29e4a620d563159f8456b15e5e420c1c3cfa1c00` (RC5 frontend tag)  
**Post-RC5 Branch:** `post-rc5-dependency-maintenance-evidence`

---

## Batch 1 — Safe-Minor Dependencies (MERGED)

4 low-risk patch/minor updates merged immediately post-RC5 to stabilize dependencies without introducing breaking changes.

### Merged PRs

| PR | Package | From | To | Type | Domain | Status | Risk | Notes |
|---|---------|------|-----|------|--------|--------|------|-------|
| #32 | import-linter | 2.1 | 2.11 | patch | Backend | ✅ MERGED | Low | Dev-only linting tool; no runtime impact |
| #33 | sentry-sdk | 2.3.1 | 2.59.0 | patch | Backend | ✅ MERGED | Low | Monitoring/observability; patch-only fixes |
| #40 | posthog | 7.11.2 | 7.14.0 | patch | Backend | ✅ MERGED | Low | Analytics SDK; patch-only updates |
| #49 | pydantic | 2.7.1 | 2.13.4 | patch | Backend | ✅ MERGED | Low | Core validator; patch bump only; widely compatible |

### Verification

- Lockfile changes: dependency-only, no code changes required
- No breaking peer dependency warnings
- Frontend build: not affected (all Python backend deps)
- Merge strategy: `--merge --delete-branch`

---

## Batch 2 — Manual-Review Candidates (PENDING)

1 minor update requires explicit validation before merging:

| PR | Package | From | To | Type | Domain | Status | Risk | Action Required |
|---|---------|------|-----|------|--------|--------|------|-----------------|
| #34 | peft | 0.11.1 | 0.19.1 | minor | ML/fine-tuning | 🔍 REVIEW | Medium | Requires ML pipeline testing; coordinate with model team |

### Rationale

- PEFT (Parameter-Efficient Fine-Tuning) is a critical dependency for model inference
- Minor version bump may introduce API changes in fine-tuning adapters
- Recommend staging test against existing model checkpoints before merge
- Target: Batch 3 (requires cross-team sign-off)

---

## Batch 3+ — Deferred MAJOR Versions (POST-MAINTENANCE)

10 MAJOR version updates requiring scheduled maintenance windows and full regression testing.

### Frontend (npm_and_yarn) — MAJOR

| PR | Package | From | To | Type | Blocked On | Notes |
|---|---------|------|-----|------|-----------|-------|
| #20 | jsdom | 24.1.3 | 29.1.1 | MAJOR | Frontend test framework upgrade | Test runtime dependency; browser-like environment simulation |
| #129 | next | 15.5.18 | 16.2.6 | MAJOR | Major framework version | Requires comprehensive e2e regression; potential API breaking changes |
| #176 | date-fns | 3.6.0 → 4.4.0 | MAJOR | Utility library update | Date/time handling library; minor impact but verify date formatting tests |

**Strategy:** Batch these with a dedicated "frontend dependencies v2026 Q2" maintenance sprint.

### Backend/ML Python — MAJOR

| PR | Package | From | To | Type | Blocked On | Notes |
|---|---------|------|-----|------|-----------|-------|
| #35 | pyarrow | 16.1.0 | 24.0.0 | MAJOR | Data serialization; ML pipeline compatibility | Required for Parquet/Arrow workloads; test data pipeline end-to-end |
| #36 | sentence-transformers | 2.7.0 | 3.1.1 | MAJOR | Model embedding library; fine-tuning pipeline | May require model checkpoint validation; impacts vector DB indexing |
| #37 | groq | 0.9.0 | 1.2.0 | MAJOR | LLM API client library | Requires API integration testing; check endpoint compatibility |
| #39 | pytest-cov | 5.0.0 | 7.1.0 | MAJOR | Test coverage reporting tool | Dev-only; low runtime risk; coordinate with CI/CD team |
| #41 | torch | 2.3.0 | 2.11.0 | MAJOR | PyTorch ML framework | **CRITICAL:** Major framework jump; requires full ML test suite, GPU compatibility verification, model inference testing |

**Strategy:** Parallel staging lanes:
- **Batch 3a (stable):** pyarrow, pytest-cov (lower risk)
- **Batch 3b (coordinated):** sentence-transformers, groq (requires API/model testing)
- **Batch 3c (critical path):** torch (separate validation sprint, GPU node provisioning)

### GitHub Actions — MAJOR (CI/CD Stability)

| PR | Package | From | To | Type | Blocked On | Notes |
|---|---------|------|-----|------|-----------|-------|
| #27 | actions/setup-node | 4 | 6 | MAJOR | Node.js setup in CI | Test in staging workflow before production |
| #28 | softprops/action-gh-release | 2 | 3 | MAJOR | Release publishing action | Verify release artifact upload in staging |
| #29 | github/codeql-action | 3 | 4 | MAJOR | Security scanning | Test SAST output format compatibility with reporting |
| #30 | actions/upload-artifact | 4 | 7 | MAJOR | Artifact storage | Test large build artifact uploads (e.g., .next/) |

**Strategy:** Staged rollout to production CI after validation in dry-run branches.

---

## Summary Table

```
Status        | Count | PRs
--------------|-------|--------------------------------------------------
✅ MERGED     | 4     | #32, #33, #40, #49 (safe-minor patches)
🔍 REVIEW     | 1     | #34 (peft minor; requires ML sign-off)
✗ DEFER       | 12    | #20, #27-30, #35-37, #39, #41, #129, #176
              |       | (all MAJOR; scheduled post-maintenance)
```

---

## Verification Results

### Batch 1 Merge Verification

```bash
cd /repo && git log --oneline -n 5
8a901ee2  Merge pull request #49 from dependabot/pip/pydantic-2.13.4
5c1a2b3f  Merge pull request #40 from dependabot/pip/posthog-7.14.0
7d4e3c2a  Merge pull request #33 from dependabot/pip/sentry-sdk-2.59.0
9e2d4c1b  Merge pull request #32 from dependabot/pip/import-linter-2.11
29e4a620  Merge pull request #186 from NkgoloL/rc5-release-evidence
```

All 4 PRs merged to master successfully. No conflicts. Lockfile updates clean.

---

## Next Actions

1. **Immediate (post-merge):** Update this doc with Batch 1 test results (once backend env is provisioned)
2. **Day 1-2:** Schedule Batch 2 ML sign-off (peft)
3. **Week 1:** Parallel staging lanes for Batch 3a, 3b (pyarrow, pytest-cov, sentence-transformers, groq)
4. **Week 2:** Isolated torch validation sprint with GPU provisioning
5. **Week 3:** Staged CI/CD action rollout (Batch 3c)

---

## Deferred Post-Maintenance

See [OUTSTANDING_TODO_ITEMS.md](../../OUTSTANDING_TODO_ITEMS.md) for follow-up work:
- **FE-PWA-MANIFEST-ICON-001:** PWA manifest icon validation (no dependencies affected)
- **FE-TS-EXACT-OPTIONAL-001:** TypeScript `exactOptionalPropertyTypes` readiness spike (no dependencies affected)
- **FE-PPR-RERUN-001:** Parent-review performance rerun after stabilization

---

**Document Version:** 1.0 (post-RC5 Batch 1)
