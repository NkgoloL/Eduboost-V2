# Auth, session, and RBAC policy baseline

## Runtime scope

The canonical backend runtime is `app.api_v2:app`. Authentication routes live under `/api/v2/auth`.

## Password policy

Registration and reset flows must use `app.core.password_policy.validate_password_strength`.

Baseline rules:

- minimum complex password length: `PASSWORD_MIN_LENGTH`, default `12`
- long passphrase support: `PASSWORD_PASSPHRASE_MIN_LENGTH`, default `16`, with at least three words
- complex passwords require uppercase, lowercase, digit, and symbol characters
- common password fragments and EduBoost-specific terms are rejected
- password hashes use bcrypt with `PASSWORD_BCRYPT_ROUNDS`, default `12`

## Access-token policy

- Access tokens are JWTs signed with `JWT_SECRET` and `JWT_ALGORITHM`.
- Production default TTL is `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15`.
- Access tokens include `sub`, `role`, `type=access`, `jti`, `iat`, and `exp`.
- Access-token revocation is Redis-backed by JTI.

## Refresh-token policy

- Production default TTL is `JWT_REFRESH_TOKEN_EXPIRE_DAYS=7`.
- Refresh tokens are JWTs with `type=refresh`, `jti`, and `family` claims.
- Refresh tokens are stored hashed at rest in Redis.
- Refresh tokens are single-use and rotate on every `/auth/refresh` call.
- Token reuse revokes the token family.
- Session inventory exposes token metadata only: JTI, family ID, and TTL. Raw refresh tokens are never returned.

## Cookie policy

The refresh-token cookie is named `eduboost_refresh` and is set with:

- `HttpOnly`
- `Secure`
- `SameSite=strict`
- `Path=/api/v2/auth`
- `Max-Age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600`

Access tokens remain bearer tokens and must not be stored in JavaScript-readable persistent storage in production clients.

## RBAC and object-level authorization

Persisted V2 roles currently include:

- `student`
- `parent`
- `teacher`
- `admin`

Reserved operational roles are defined in `app.core.rbac.OperationalRole` for future migration and policy work:

- `support_operator`
- `content_reviewer`
- `compliance_auditor`

Learner-scoped access must call `app.core.authorization.assert_can_access_learner` or an equivalent policy helper. The current baseline permits:

- admins to access learner records for operational/legal workflows
- parents/guardians to access only linked learners
- learner self-access only when token subject equals learner ID

Teacher/class assignments, support minimization, content-reviewer scope, and compliance-auditor scope remain intentionally denied until their assignment/scope tables exist.

## Redis persistence note

Refresh-token rotation and access-token revocation depend on Redis. Production Redis must use managed persistence, backups, and failover. If Redis is configured as volatile-only cache, token revocation guarantees degrade after restart. This remains a deployment-readiness gate.
