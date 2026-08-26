# TSR-5.9 Slow Test and Shard Timeout Policy

## Policy
- Individual test timeouts bounded at 5 seconds unless explicitly marked `@pytest.mark.slow`.
- Shards bounded within deterministic time budgets.

## Review Metadata
- **Reviewer**: Nkgolo Lebelo (Lead Engineer, Self-Review)
- **Decision**: `completed`
- **Conflict Disclosure**: Self-review by sole developer; not independent approval.
