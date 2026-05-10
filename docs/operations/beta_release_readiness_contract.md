# Beta Release Readiness Contract

## Purpose

Cluster H defines the minimum evidence required before EduBoost V2 can be
considered ready for a controlled staging or beta release.

## Required Evidence Clusters

- PR-002R backend runtime and API contract closure
- Phase 2 authorization closure
- Cluster C POPIA consent and audit closure
- Cluster D deployment and environment closure
- Cluster E data resilience closure
- Cluster F AI safety closure
- Cluster G frontend vertical journey closure

## Required Release Gates

- OpenAPI schema drift check passes
- runtime entrypoint smoke checks pass
- authorization and consent closure checks pass
- environment/security checks pass
- database backup/restore closure checks pass
- AI safety fixture and prompt checks pass
- frontend journey closure checks pass
- staging release gate check passes
- release evidence artifact guard passes

## Beta Boundary

Beta release readiness does not mean unrestricted production launch. It means
controlled validation with limited users, monitored errors, rollback procedure,
backup/restore readiness, and documented release evidence.

## Required Sign-Off Areas

- technical lead sign-off
- privacy/POPIA sign-off
- data resilience sign-off
- AI safety sign-off
- frontend journey sign-off
- rollback owner sign-off

## Command

```bash
make beta-release-readiness-contract-check
```
