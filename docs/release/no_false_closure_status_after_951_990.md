# No False-Closure Status After code_951_990

**Status:** auth service ownership improved; success-path HTTP auth tests still pending

code_951_990 moves private auth lifecycle helper bodies out of `auth.py` into a service-owned implementation module and makes `AuthApplicationService` own lifecycle dispatch.

## Not claimed

- It does not prove success-path register/login/refresh against a real database.
- It does not prove email delivery or external auth provider behavior.
- It does not claim beta readiness.

## Remaining proof

- Add success-path HTTP tests using controlled repository/database fixtures.
- Add refresh-token scope preservation HTTP test.
- Add failure-path tests for duplicate email, wrong password, expired refresh token, and guardian scope.
