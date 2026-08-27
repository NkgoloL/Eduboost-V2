# EduBoost V2: Operational Handover & Rotation Runbook

**Control ID**: `TSR-13.3`  
**Release Gate**: `RG-6`  
**Status**: Authoritative  
**Domain**: Operations / Resilience  

---

## 1. Objective

This runbook establishes a clear protocol for rotating operational and on-call responsibilities between engineers, ensuring that no single individual represents a single point of operational failure.

---

## 2. On-Call Responsibilities & Rotation Protocol

1. **Primary On-Call Operator**:
   - First responder to PagerDuty/Alertmanager alerts (15-minute SLA for Sev 1).
   - Monitors daily backups and database health metrics.
   - Authorizes incident triage and engages the rollback playbook if necessary.
2. **Secondary On-Call Operator**:
   - Escalation backup if Primary fails to acknowledge within 10 minutes.
   - Assists during major incident remediation and coordinates stakeholder notifications.

---

## 3. Handover Checklist & Verification Steps

At each weekly rotation changeover:

```
[ ] 1. Verify Access Credentials: Confirm secondary operator has active SSH, DB read-replica, and cloud console access.
[ ] 2. Drill Disaster Recovery Commands: Run `pytest tests/integration/test_disaster_recovery_drill.py` in test environment.
[ ] 3. Review Open Defects: Review all active tickets in `docs/roadmap/production_readiness/defect_register_baseline.json`.
[ ] 4. Check DSR Erasure Pipeline: Verify no pending POPIA erasure tasks exceed 24 hours.
[ ] 5. Confirm Fail-Closed Invariants: Validate live billing remains locked.
```
