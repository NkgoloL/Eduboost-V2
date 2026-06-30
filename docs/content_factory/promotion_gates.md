# Content Factory Promotion Gates

Production promotion must fail closed unless all required checks pass:

- diagnostic item and lesson coverage are green for configured targets
- production-bound artifacts are approved
- rejected, quarantined, and validation-failed artifacts are blocked
- source citations exist and pass provenance validation
- staging seed verification passes
- an admin actor initiates the action

Future configured layers must not silently pass when targets exist and coverage is unmet.
