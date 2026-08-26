# TSR-4.9 Concurrency, Cache, and Evidence Retention Policy

## Policy Definition
1. **Concurrency Control**: All pull request and push workflows enforce workflow-level concurrency cancellation (`cancel-in-progress: true`) keyed on `${{ github.workflow }}-${{ github.ref }}` to prevent redundant compute waste and conflicting check state.
2. **Deterministic Caching**: Caches are strictly keyed to input lockfiles (`pnpm-lock.yaml`, `requirements/base.txt`, `requirements/dev.txt`).
3. **Evidence Retention**: Release candidate evidence bundles generated in `docs/release-evidence/` are committed and cryptographically hashed in git history, retaining an immutable audit trail.
