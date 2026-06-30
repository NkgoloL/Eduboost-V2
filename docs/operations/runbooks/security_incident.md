# Runbook: Security Incident

**Last Updated**: 2026-06-12  
**Severity**: Critical  
**SLA Impact**: Potential data breach, regulatory notification required

---

## Symptoms

- Unusual API access patterns detected
- Failed authentication spike from unfamiliar IP ranges
- Suspicious data export requests
- Security tool alerts (WAF, DDoS protection)
- Unauthorized access to PII

---

## Incident Classification

| Level | Description | Examples |
|-------|-------------|-----------|
| P1 | Confirmed breach | Data exfiltration, unauthorized PII access |
| P2 | Suspected breach | Anomalous patterns, failed investigation |
| P3 | Threat detection | Blocked attacks, honeypot triggers |

---

## Response Procedure

### Phase 1: Detection & Triage (0–15 min)

1. **Acknowledge alert** — Confirm incident in PagerDuty
2. **Classify severity** — Use table above
3. **Notify** — Alert Security Lead and Engineering Lead

```bash
# Quick check - recent auth failures by IP
kubectl logs -l app=api -n eduboost | \
  grep -i "failed\|authentication" | \
  tail -100
```

### Phase 2: Containment (15–60 min)

1. **Block suspicious IPs** at WAF:
   ```bash
   az network waf policy rule blocking-rule create \
     --resource-group <rg> \
     --policy-name <waf> \
     --name block-attacker \
     --rule-type MatchRule \
     --match-condition "IP addr in <suspicious-ip>"
   ```

2. **Revoke compromised tokens**:
   ```bash
   # Use emergency revoke-all if breach confirmed
   python scripts/emergency_revoke_all.py --epoch $(date +%s)
   ```

3. **Disable accounts** if needed:
   ```bash
   # Mark accounts as locked
   psql -h <db> -U eduboost -c "UPDATE guardian SET locked=true WHERE id IN (<ids>)"
   ```

### Phase 3: Investigation (1–4 hours)

1. **Gather evidence**:
   ```bash
   # Export relevant logs
   kubectl logs -l app=api -n eduboost --since=4h > /tmp/incident-logs.txt
   
   # Export audit trail
   psql -h <db> -U eduboost -c "SELECT * FROM audit_events WHERE created_at > '2026-06-12'" > /tmp/audit-trail.sql
   ```

2. **Analyze attack vector**:
   - Compromised credentials?
   - API key leak?
   - Application vulnerability?
   - Insider threat?

3. **Document findings** in incident tracker

### Phase 4: Recovery (4–24 hours)

1. **Restore services** — Fix vulnerability, redeploy if needed
2. **Rotate credentials** — All secrets, API keys, database passwords
3. **Verify** — Confirm attacker no longer has access

### Phase 5: Notification (within 72 hours for POPIA)

If personal information was compromised:

1. **Notify Information Officer** — poipia@eduboost.co.za
2. **Notify affected users** — Email through SendGrid
3. **Notify Information Regulator** — Via POPIA portal

---

## Communication Templates

### Internal (Slack)

```
🚨 SECURITY INCIDENT - CLASSIFIED

Severity: P1
Status: Containment in progress
Action: Blocking IPs, revoking tokens
Contact: @security-lead
```

### Regulatory (POPIA)

```
Subject: POPIA Security Breach Notification

Dear Information Regulator,

We are writing to notify you of a security incident at EduBoost (Pty) Ltd.

1. Nature of breach: [brief description]
2. Categories of data affected: [list]
3. Approximate number of data subjects: [number]
4. Likely consequences: [assessment]
5. Measures taken: [steps taken]

We will provide further updates as our investigation progresses.

Regards,
EduBoost Information Officer
```

---

## Post-Incident

1. **Root cause analysis** — Document in incident tracker
2. **Remediation** — Fix vulnerabilities
3. **Retrospective** — 72-hour review meeting
4. **Update** — This runbook with lessons learned
5. **Training** — Security awareness if needed

---

## Contacts

| Role | Contact | Phone |
|------|---------|-------|
| Security Lead | security@eduboost.co.za | +27 XXX XXX |
| Engineering Lead | engineering@eduboost.co.za | +27 XXX XXX |
| POPIA Officer | privacy@eduboost.co.za | +27 XXX XXX |
| Legal Counsel | legal@eduboost.co.za | +27 XXX XXX |
| Incident Response | ir@eduboost.co.za | +27 XXX XXX |

---

## References

- POPIA Act Section 22: https://popia.co.za/section-22/
- Incident Response Plan: `docs/operations/incident_response.md`
- Audit Trail: `app/core/audit.py`
- Emergency Revocation: `scripts/emergency_revoke_all.py`