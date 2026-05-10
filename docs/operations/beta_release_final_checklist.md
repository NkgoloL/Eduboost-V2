# Beta Release Final Checklist

## Purpose

This checklist is the final pre-approval checklist for a controlled EduBoost V2
staging or beta release.

## Required Pre-Approval Checks

- working tree is clean except intentional release evidence files
- branch is rebased on remote target branch
- OpenAPI drift check passes
- staging release gate check passes
- release evidence artifacts check passes
- Cluster C POPIA consent closure check passes
- Cluster D deployment closure check passes
- Cluster E data resilience closure check passes
- Cluster F AI safety closure check passes
- Cluster G frontend journey closure check passes
- Cluster H closure check passes

## Required Generated Evidence

- staging smoke evidence manifest generated
- beta sign-off manifest generated
- beta release evidence bundle generated
- release candidate tag manifest generated

## Required Manual Confirmations

- technical lead approval recorded
- privacy/POPIA approval recorded
- data resilience approval recorded
- AI safety approval recorded
- frontend journey approval recorded
- rollback owner approval recorded
- post-deploy verification owner assigned

## Explicit Non-Goals

- no unrestricted production launch
- no real learner data migration without a separate approved plan
- no release tag push before approval
- no generated `coverage.xml` conflict carried into release commit

## Command

```bash
make beta-release-final-checklist-check
```
