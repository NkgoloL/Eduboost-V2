# TSR-5.5 Flake Policy Authority

## Policy Definition
1. **Flake Accountability**: Flaky tests are classified as bugs and must be quarantined immediately to prevent masking genuine PR regressions.
2. **Deterministic Selection**: Fast PR test selection avoids dynamic random discovery and executes pinned manifest files.
3. **Audit History**: All quarantined tests and resolution links are maintained in `docs/testing/flake_policy_and_quarantine_register.md`.
