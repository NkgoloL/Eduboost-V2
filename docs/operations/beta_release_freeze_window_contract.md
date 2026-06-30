# Beta Release Freeze Window Contract

## Purpose

The beta release freeze window contract defines what changes are allowed after
final Cluster H closeout evidence is generated.

## Freeze Entry Conditions

- Cluster H release readiness check passes
- Cluster H final closeout rollup check passes
- final release verification check passes
- beta evidence consistency check passes
- final PR merge readiness check passes
- release audit trail index check passes
- beta release closure attestation check passes

## Frozen Scope

- API contract evidence
- authorization and consent gate evidence
- deployment readiness evidence
- data resilience evidence
- AI safety evidence
- frontend journey evidence
- Cluster H release-readiness evidence
- release candidate tag manifest
- beta release evidence bundle
- PR closeout evidence

## Allowed Changes During Freeze

- literal evidence phrase repair
- generated snapshot refresh
- manual approval field completion
- decision log entry completion
- release candidate metadata update
- documentation typo that does not change release scope

## Prohibited Changes During Freeze

- new feature behavior
- schema or API contract change
- authorization boundary change
- consent boundary change
- deployment workflow semantic change
- data retention or deletion behavior change
- AI safety boundary change
- production migration change

## Exception Rule

Any prohibited change requires a release change-control exception log entry and
rerun of final release verification.

## Boundary

The freeze window contract controls release evidence discipline. It does not approve release, execute deployment, create release tags, or override manual approval.

## Command

```bash
make beta-release-freeze-window-check
```
