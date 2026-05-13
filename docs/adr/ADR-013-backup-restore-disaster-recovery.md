# ADR-013: Backup, Restore, and Disaster Recovery Decision

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will use managed database snapshots with point-in-time recovery, versioned object storage replication, encrypted cross-region backup storage, immutable retention, documented restore runbooks, scheduled restore drills, and disaster recovery ownership.

## Rationale

Learner records, audit logs, content assets, and configuration evidence require recoverability, integrity verification, and privacy-aware retention. Repository-side contracts make backup and restore expectations verifiable before live infrastructure is provisioned.

## Required Controls

- database point-in-time recovery is required
- encrypted backup storage is required
- cross-region backup copy is required
- immutable retention is required
- backup integrity checksum verification is required
- restore runbooks are required
- restore drills are required
- RPO and RTO objectives are required
- disaster recovery escalation matrix is required
- post-incident review is required

## Boundary

This ADR records backup, restore, and disaster recovery decision evidence. It does not create backups, restore data, provision storage, or authorize production launch.
