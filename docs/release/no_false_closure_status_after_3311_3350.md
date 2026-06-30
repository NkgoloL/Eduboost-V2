# No False-Closure Status After DB-ROLLBACK-001R / code_3311_3350

**Status:** DB backup / restore / rollback evidence gate added.

## Proven by default

- Backup/restore tooling exists.
- The workflow is durable and does not call `temp/code_*` scripts.
- Database dumps are not uploaded as artifacts.
- DB-ROLLBACK-001 remains beta-blocking unless accepted evidence mode passes.

## Proven only in accepted mode

- A backup dump was created from the source/staging DB.
- A SHA256 checksum and non-zero dump size were recorded.
- The dump was restored into a different disposable restore DB.
- Post-restore SQL smoke passed.
- Source and restore Alembic versions match.
- Source and restore table counts match.
- Key table counts match for `alembic_version`, `audit_events`, `diagnostic_items`, `irt_items`, and `parental_consents`.
- A successful GitHub Actions run matching the current commit is attached.

## Not claimed

- JWT-001 is closed.
- ARQ-001 is closed.
- DIAG-SCORE-001 is closed.
- AUDIT-WRITE-001 is closed.
- External approvals are complete.
- Frontend runtime proof is complete.
- Image digest/SBOM evidence is complete.
- Security scan artifact capture is complete.
- Beta release is approved.
