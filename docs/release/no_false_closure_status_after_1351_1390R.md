# No False-Closure Status After ARCH-001R / code_1351_1390R

**Status:** dynamic diagnostics repository resolution moved out of router.

## Proven

- `diagnostics.py` no longer performs `importlib.import_module` repository resolution.
- `diagnostics.py` no longer imports `app.repositories` directly.
- `diagnostics.py` no longer directly constructs the critical repository classes from router code.
- Dynamic compatibility resolution is centralized in `app/api_v2_deps/diagnostic_repositories.py`.

## Not claimed

- Full diagnostics subsystem service extraction is complete.
- Every v2 router is free of repository debt.
- All import-linter ignores have been removed.
- Staging diagnostics flow proof is complete.
