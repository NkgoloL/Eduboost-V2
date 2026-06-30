# Final Release Blocker Register

## Required Fields

- blocker ID
- domain
- title
- severity
- status
- owner
- evidence path
- closure path
- waiver path
- external dependency
- blocks launch flag

## Required Rules

- blocker ID must follow RB-### format
- release blocker owner is required
- closed blockers require closure evidence
- waived blockers require waiver evidence
- external pending blockers require external dependency note
- critical/release-blocker items cannot remain open
- release-blocker severity cannot be waived by default

## Boundary

This register records repository-side blocker status. It does not approve launch.
