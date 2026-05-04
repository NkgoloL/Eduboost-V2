# Documentation and Repo Sync TODO

Updated: 2026-05-04
Source: `C:\Users\Lebelo\Downloads\EduBoost_V2_Comparative_Audit_Report.md`

Status legend:

- `[done]` completed and reflected in the repository
- `[pending]` still requires follow-through

## Audit-Driven Tasks

1. `[done]` Rewrite `README.md` so it describes the active V2 runtime, the
   remaining compatibility boundary, and the current compose-file map.
2. `[done]` Rewrite `SECURITY.md` so security claims match verifiable code and
   workflow state instead of stale completion tables.
3. `[done]` Rewrite `CONTRIBUTING.md` so contributor guidance matches the
   current development, testing, and documentation workflow.
4. `[done]` Update `docs/v2_migration.md` to describe the repo as V2-first with
   compatibility shims, not as a total historical deletion of every legacy
   artifact.
5. `[done]` Update `docs/index.md` so the docs entrypoint clearly points
   readers to the current-state documentation.
6. `[done]` Add `docs/project_status.md` as a plain-language snapshot of the
   verified repository state.
7. `[done]` Update `mkdocs.yml` so the current-state page is part of the
   published docs navigation.
8. `[done]` Document the JWT policy as implemented today: 15-minute access
   tokens and 7-day refresh tokens.
9. `[done]` Document the current audit path correctly: PostgreSQL append-only
   audit repository for sensitive events, with Redis used for revocation,
   caching, and job status rather than as the primary audit ledger.
10. `[done]` Document that the canonical GitHub Actions workflows live under
    `.github/workflows/`, addressing the earlier root-`ci.yml` concern.
11. `[done]` Document the current compose-file purpose mapping so
    `docker-compose.yml`, `docker-compose.v2.yml`, `docker-compose.aca.yml`,
    and `docker-compose.prod.yml` are not left unexplained.
12. `[done]` Confirm the earlier comparative-audit hygiene findings about
    committed `mnt/` and `scratch/` directories are no longer true in the
    current repository state.
13. `[done]` Confirm the architecture manifest is now represented by the stable
    `docs/architecture/V2_ARCHITECTURE.md` path instead of an opaque
    auto-generated filename.
14. `[pending]` Verify that the public canonical Git history is the intended
    source of truth, and document any remaining private-fork or mirror gap if
    it still exists.
15. `[pending]` Validate that production environment values and cookie settings
    match the documented JWT policy, not just the repository defaults.
16. `[pending]` Re-verify release automation, image-scan, and
    production-promotion workflows against the current Docker and Kubernetes
    assets before the next tagged release.
17. `[pending]` Continue retiring the remaining compatibility-only legacy
    surface before the configured retirement date.
18. `[pending]` Keep the docs synchronized whenever security, POPIA, runtime,
    or release behavior changes, so the next audit does not have to untangle
    conflicting markdown again.

## Notes

- This tracker replaces the earlier stale TODO that described a different and
  much older migration state.
- The comparative audit raised several issues that are already obsolete in the
  current working repository; those are marked `[done]` above so they remain
  visible without pretending they still need action.
