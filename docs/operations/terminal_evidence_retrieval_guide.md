# Terminal Evidence Retrieval Guide

## Purpose

The terminal evidence retrieval guide defines how authorized reviewers, release owners, and auditors locate the sealed controlled staging/beta evidence package after closeout.

## Required Retrieval Inputs

- final archive accession record
- post-closeout custody register
- final sealed package manifest
- audit review closeout certificate
- terminal handoff closure note
- terminal PR evidence index
- final release evidence table of contents
- post-closeout evidence access policy
- release evidence retention finalization
- cluster h release evidence checksum index

## Retrieval Steps

1. Confirm release candidate and commit SHA.
2. Confirm branch and PR number.
3. Open the final archive accession record.
4. Verify post-closeout custody register.
5. Open the final sealed package manifest.
6. Use terminal PR evidence index for PR evidence navigation.
7. Use final release evidence table of contents for full evidence navigation.
8. Verify checksum and ledger references.
9. Apply post-closeout evidence access policy.
10. Avoid unnecessary learner personal information.

## Retrieval Rules

- retrieval guide must reference release candidate and commit SHA
- retrieval guide must reference branch and PR number
- retrieval guide must preserve post-closeout evidence access policy references
- retrieval guide must preserve custody register references
- retrieval guide must preserve archive accession references
- retrieval guide must preserve checksum and ledger references
- retrieval guide must remain controlled staging/beta evidence

## Boundary

This terminal evidence retrieval guide records retrieval guidance only. It does not approve production launch, execute deployment, create release tags, or merge the pull request automatically.

## Command

```bash
make terminal-evidence-retrieval-guide-check
```
