# Roadmap New-Work Freeze

**Status:** active after reconciliation evidence is captured

## Freeze statement

Until the Outstanding Work Register is reviewed and a next slice is selected from it, EduBoost must not introduce new roadmap phases, new implementation workstreams, or new architecture pivots.

## Allowed work

Allowed work must satisfy all of the following:

1. It cites one or more `RR-###` IDs from `docs/roadmap/reconciliation/outstanding_work_register.md`.
2. It does not weaken existing safety, privacy, security, or evidence controls.
3. It preserves current explicit non-authorisations unless the selected `RR-###` item specifically allows a controlled approval path.
4. It does not claim production release, public beta, production deployment, release tagging, or runtime KG implementation unless a later approved roadmap item explicitly authorises that claim.

## Blocked work

The following are blocked unless separately approved through roadmap reconciliation:

- new numbered phases beyond the reconciled roadmap;
- runtime KG implementation;
- public beta expansion;
- production release;
- production deployment;
- release tagging;
- destructive audit/consent database changes;
- production database mutation outside an approved migration window;
- replacing evidence with documentation-only assertions.

## Next-slice selection rule

The next implementation slice title must include the target `RR-###` ID or list the covered `RR-###` IDs in its PR body.
