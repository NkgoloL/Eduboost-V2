# Release Notes Discipline Contract

## Required Release Note Types

- feature
- fix
- security
- breaking change
- operations
- docs

## Required Release Note Fields

- entry ID
- release note type
- summary
- evidence path
- breaking change flag
- migration required flag
- user-visible flag
- owner

## Required Rules

- release note summary is required
- release note evidence path must be controlled
- breaking changes must use breaking_change release note type
- migration-required notes must be breaking_change or operations
- release note owner is required

## Boundary

This contract records release-note discipline readiness. It does not publish release notes.
