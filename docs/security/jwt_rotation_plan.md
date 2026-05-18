# JWT Rotation Plan

**Status:** helper implemented, environment rollout pending

## Configuration

Preferred:

```bash
JWT_KEYRING='[
  {"kid":"2026-05-current","secret":"<new-secret>","algorithm":"HS256","status":"current"},
  {"kid":"2026-04-previous","secret":"<old-secret>","algorithm":"HS256","status":"previous"}
]'
```

Fallback:

```bash
JWT_CURRENT_KID=legacy
JWT_SECRET_KEY=<existing-secret>
JWT_ALGORITHM=HS256
```

## Rotation procedure

1. Add new key as `current`.
2. Keep old key as `previous`.
3. Deploy.
4. Wait longer than the maximum refresh-token lifetime.
5. Remove old key.
6. Force revoke outstanding refresh tokens if compromise is suspected.

## Rollback

Promote the previous key back to `current` and redeploy. Do not remove previous keys until all refresh windows expire.
