# Incident Response Tabletop Exercise

**Date:** 2026-06-12  
**Exercise:** EduBoost V2 Production Incident Response  
**Participants:** Engineering Lead, Platform Engineer, Product Owner, Compliance Officer

---

## Scenario 1: Database Outage

### Situation
PostgreSQL database becomes unavailable at 14:00 SAST. All API endpoints
returning 500 errors. Users cannot access lessons or diagnostics.

### Discussion Points
1. **Detection:** How do we know? (Prometheus alerts, user reports, PagerDuty)
2. **Initial Response:** Who is on-call? What's the escalation path?
3. **Diagnosis:** Is it the primary DB or read replica? Network issue?
4. **Mitigation:** Failover to standby? Roll back recent DB changes?
5. **Communication:** Status page update, customer support guidance
6. **Recovery:** What data might be lost? How to verify integrity?

### Lessons Identified
- [ ] Runbook for database failover needs updating
- [ ] Add explicit alert for "database unavailable" vs "slow queries"
- [ ] Document RTO (Recovery Time Objective) and RPO (Recovery Point Objective)

---

## Scenario 2: LLM Provider Outage

### Situation
Groq API returns 503 errors for all requests. Lesson generation and
diagnostic scoring are blocked. Error rate: 100% of LLM calls.

### Discussion Points
1. **Detection:** Which alerts trigger? (high error rate, failed LLM calls)
2. **Fallback:** Does the app fallback to Anthropic? Is it configured?
3. **User Impact:** What do users see? Graceful degradation?
4. **Recovery:** When Groq recovers, how do we clear the backlog?
5. **Cost Control:** Did the fallback cause bill spike?

### Lessons Identified
- [ ] Verify Anthropic fallback is working in production
- [ ] Add rate-limit alerts for fallback provider
- [ ] Document expected user experience during LLM outage

---

## Scenario 3: Security Incident (Breach Detection)

### Situation
Security monitoring detects unusual data access patterns. 
Possible unauthorized access to learner PII. 500 suspicious API calls
from IP range outside South Africa in the last hour.

### Discussion Points
1. **Detection:** What triggered the alert? (failed auth rate, unusual volume)
2. **Initial Response:** Block suspicious IPs? Revoke tokens?
3. **Investigation:** Audit logs, identify affected accounts
4. **Containment:** Is the attacker still in the system?
5. **Notification:** POPIA breach notification required within 72 hours
6. **Recovery:** How to secure the system? Password reset required?

### Lessons Identified
- [ ] Confirm audit log integrity (HMAC verification works)
- [ ] Verify PII access logging is complete
- [ ] Confirm POPIA breach notification template exists
- [ ] Test emergency token revocation (scripts exist, need drill)

---

## Scenario 4: Consent/Erasure SLA Breach

### Situation
A parent submits a data erasure request via the portal. POPIA requires
completion within 30 days. System shows erasure still "pending" after 35 days.
Parent escalates to Information Regulator.

### Discussion Points
1. **Detection:** Why wasn't this flagged? (SLA monitoring exists?)
2. **Immediate Action:** Can we expedite this request manually?
3. **Root Cause:** Why did it stay pending? (legal hold? bug?)
4. **Prevention:** How to prevent future SLA breaches?
5. **Regulatory Response:** How to respond to Information Regulator?

### Lessons Identified
- [ ] Add SLA breach alert (erasure pending > 28 days)
- [ ] Verify erasure queue processing is working
- [ ] Prepare template for regulatory response
- [ ] Document manual erasure procedure

---

## Action Items

| Item | Owner | Priority | Due |
|---|---|---|---|
| Update database failover runbook | Platform | P1 | 2026-06-19 |
| Verify Anthropic fallback in prod | Engineering | P1 | 2026-06-15 |
| Test emergency token revocation | Security | P1 | 2026-06-15 |
| Add erasure SLA breach alert | POPIA | P1 | 2026-06-19 |
| Document regulatory response template | Legal | P2 | 2026-06-26 |
| Schedule next quarterly tabletop | Ops | Q3 | 2026-09-01 |

---

## Sign-Off

| Role | Name | Date |
|---|---|---|
| Engineering Lead | | |
| Platform Engineer | | |
| Product Owner | | |
| Compliance Officer | | |