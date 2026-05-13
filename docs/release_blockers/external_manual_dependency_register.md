# External Manual Dependency Register

## Required Fields

- dependency ID
- description
- owner
- external system
- verification method
- required before launch
- evidence path
- status

## Example Dependencies

| ID | Description | External System | Required Before Launch |
| --- | --- | --- | --- |
| EXT-001 | GitHub branch protection settings verified outside repository | GitHub repository settings | false |
| EXT-002 | Legal/privacy launch approval completed outside repository | legal/privacy approval workflow | false |

## Required Rules

- dependency ID must follow EXT-### format
- external dependency owner is required
- external system is required
- verification method is required
- required external dependencies must be closed before launch
- external dependency evidence path must live under docs/release_blockers/

## Boundary

This register records external/manual dependencies. It does not satisfy those dependencies.
