# TSR-5.4 Backend Selection and Test Isolation Policy

## Policy
- Unit test paths default to deterministic test stubs (e.g. FASTMCP_BACKEND=test-stub).
- Real services execute under dedicated integration harnesses only.

## Review Metadata
- **Reviewer**: Nkgolo Lebelo (Lead Engineer, Self-Review)
- **Decision**: `completed`
- **Conflict Disclosure**: Self-review by sole developer; not independent approval.
