# TSR-4.9 CI Concurrency, Cache, and Artifact Retention Policy

## Policy
- Concurrency group cancels redundant in-flight PR runs.
- Lockfile-keyed caching for pip and pnpm.
- 14-day retention for non-release artifacts; immutable retention for release evidence.

## Review Metadata
- **Reviewer**: Nkgolo Lebelo (Lead Engineer, Self-Review)
- **Decision**: `completed`
- **Conflict Disclosure**: Self-review by sole developer; not independent approval.
