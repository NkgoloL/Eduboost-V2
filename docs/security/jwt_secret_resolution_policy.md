---
title: "JWT Secret Resolution Policy"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# JWT Secret Resolution Policy

**Status:** active after JWT-001 / code_1071_1110

## Resolution order

1. `JWT_KEYRING`
2. `settings.JWT_SECRET`
3. `JWT_SECRET`
4. `settings.JWT_SECRET_KEY`
5. `JWT_SECRET_KEY`
6. `SECRET_KEY`
7. `ACCESS_TOKEN_SECRET_KEY`
8. development-only fallback

## Production rule

Production-like environments must not run with placeholder JWT secrets, including:

- `dev-insecure-secret-change-me`
- `changeme`
- `secret`
- `replace-me`

The application startup path calls `validate_jwt_keyring_environment()`.
