# No False-Closure Status After code_911_950

**Status:** method-boundary improved; full auth behavior still needs HTTP payload tests

code_911_950 changes auth lifecycle route bodies into AuthApplicationService delegates and preserves the previous implementation bodies as private helpers.

## Not claimed

- It does not claim final AuthService purity.
- It does not remove every private legacy helper from `auth.py`.
- It does not prove every external auth payload shape with live DB persistence.

## Next closure work

Move `_auth_lifecycle_legacy_*_impl` helper bodies into `AuthApplicationService` proper and add request/response HTTP tests with dependency overrides.
