# Documentation Review Gate Contract

## Required Gate Fields

- gate ID
- release stage
- required docs
- required ADRs
- claim review required
- stale doc review required
- release notes required
- owner
- blocks release

## Required Rules

- documentation review gate requires docs
- documentation review gate requires ADRs
- required documentation must live under docs/
- required ADRs must live under docs/adr/
- claim review is required
- stale documentation review is required
- release notes are required
- documentation review gate must block release

## Boundary

This contract records documentation review-gate readiness. It does not approve production launch.
