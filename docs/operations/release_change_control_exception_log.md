# Release Change-Control Exception Log

## Purpose

The release change-control exception log records any change made after the beta
release freeze window begins.

## Exception Record Template

| Field | Value |
| --- | --- |
| Exception ID | pending |
| Change Type | literal repair / evidence refresh / approval completion / prohibited change |
| Requested By | pending |
| Approved By | pending |
| Commit SHA | pending |
| Release Candidate | pending |
| Reason | pending |
| Affected Evidence | pending |
| Required Rerun | final release verification |
| Outcome | pending |

## Required Rules

- literal evidence phrase repair may be recorded as low-risk
- generated snapshot refresh may be recorded as evidence refresh
- prohibited change must identify affected release boundary
- prohibited change requires explicit approval before merge
- prohibited change requires final release verification rerun
- authorization, consent, API, AI safety, deployment, or data-resilience changes require owner approval
- each exception must reference commit SHA and release candidate
- unresolved exception blocks beta execution

## Boundary

This log records change-control exceptions. It does not approve prohibited changes, execute deployment, create release tags, or bypass required reruns.

## Command

```bash
make release-change-control-exception-log-check
```
