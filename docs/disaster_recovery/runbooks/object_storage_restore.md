# Object Storage Restore Runbook

## Pre-Restore Checks

- confirm target bucket namespace
- confirm object manifest checksum
- confirm restore prefix
- confirm access policy

## Restore Steps

- restore versioned objects
- verify object metadata
- restore access-control metadata
- sample object reads

## Post-Restore Validation

- sample object access
- run learner asset smoke test
- verify object checksum samples
- confirm no public access drift

## Rollback Steps

- remove restored objects
- restore previous object pointers
- record restore failure evidence

## Boundary

This runbook is repository-side evidence and does not restore live object storage automatically.
