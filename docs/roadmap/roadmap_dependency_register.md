# Roadmap Dependency Register

## Required Dependency Fields

- dependency ID
- source roadmap ID
- dependency type
- description
- owner
- external flag
- mitigation
- evidence path

## Required Rules

- dependency ID must follow DEP-### format
- source roadmap ID must follow RM-### format
- external dependencies require mitigation
- roadmap dependency evidence path must live under docs/roadmap/

## Boundary

This register records roadmap dependencies. It does not satisfy external dependencies.
