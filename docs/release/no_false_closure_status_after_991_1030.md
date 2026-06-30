# No False-Closure Status After code_991_1030

**Status:** controlled HTTP success-path proof added; real DB auth proof still pending

code_991_1030 proves register/login/refresh HTTP paths with FastAPI dependency overrides and verifies refresh guardian learner scope propagation through the service response. It also proves duplicate registration and wrong-password failures are clean non-500 errors.

## Not claimed

- Real database persistence is not proven by this batch.
- Password hashing against the real user repository is not proven by this batch.
- Refresh-token store/revocation behavior is not proven against the real DB by this batch.
- External email/notification behavior is not proven.

## Remaining proof

- Transactional/in-memory DB success path for register/login/refresh.
- Refresh-token revocation and replay rejection.
- Duplicate email at repository/database constraint level.
- Guardian learner scope from real learner repository data.
