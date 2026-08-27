# Backup Retention and Erasure Policy (TSR-7.12)

## Policy Requirements under POPIA
1. **Retention Periods:**
   - Active learner profiles: Retained for duration of active subscription + 12 months grace period.
   - Audit trail records (`audit_events`): Retained for 5 years pursuant to statutory compliance requirements.
2. **Erasure Execution across Backups:**
   - When an `erasure_request` is completed, primary DB records are deleted/anonymized.
   - Point-in-time database backups cycle through a standard 30-day retention window, after which expired snapshots containing pre-erasure states are purged automatically.
3. **Encryption Standards:**
   - All backups encrypted at rest with AES-256 and in transit via TLS 1.3.
