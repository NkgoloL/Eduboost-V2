# EduBoost V2: Evidence, Secrets & Access Custody Report

**Control ID**: `TSR-13.4`  
**Release Gate**: `RG-6`  
**Status**: Authoritative  
**Domain**: Operations / Security / Governance  

---

## 1. Scope & Purpose

This report documents the custody, backup, and escrow protocols for all critical project assets, cryptographic keys, and release verification evidence to ensure long-term survivability and zero dependency on a single developer workstation.

---

## 2. Custody & Escrow Matrix

| Asset Class | Primary Location | Escrow / Backup Mechanism | Access Control |
| :--- | :--- | :--- | :--- |
| **Git Repository & History** | GitHub Origin (`master`) | Nightly Git bundle mirrored to encrypted cloud cold storage | Multi-factor auth, branch protection rules |
| **Release Evidence Bundles** | `docs/release-evidence/` | Cryptographic SHA-256 digests committed to immutable Git tree | Read-only in CI/CD, signed by lead maintainer |
| **PostgreSQL Database Backups** | Dedicated AWS RDS / Local PG cluster | Automated daily snapshot + WAL archiving (30-day retention) | IAM role isolation, KMS envelope encryption |
| **Production Secrets & Keys** | HashiCorp Vault / AWS Secrets Manager | Split-knowledge Shamir secret sharing (2-of-3 threshold) | RBAC with mandatory access audit logging |
| **Audit Event Ledger** | Partitioned DB table `audit_events` | Immutable append-only write rules with monthly archive export | Service account restricted |

---

## 3. Custody Drill Verification

- **Drill Date**: `2026-08-27`
- **Result**: PASSED
- **Drill Execution**: Clean clone of repository executed in an air-gapped test container; verified all evidence SHA-256 digests matched verification records.
