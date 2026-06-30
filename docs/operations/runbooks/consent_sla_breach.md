# Runbook: Consent/Erasure SLA Breach

**Last Updated**: 2026-06-12  
**Severity**: High  
**SLA Impact**: Regulatory non-compliance (POPIA)

---

## Background

POPIA requires data erasure requests to be completed within **30 days**. This runbook covers what to do when an erasure or export request approaches or exceeds the SLA.

---

## Symptoms

- Alert: "Erasure request pending > 28 days"
- Parent/guardian escalates to Information Regulator
- Manual review required due to legal hold

---

## Types of Requests

### Data Export

- **SLA**: 30 days
- **Format**: JSON or CSV
- **Includes**: Learner profile, diagnostics, lessons, consents, audit trail

### Data Erasure

- **SLA**: 30 days
- **Includes**: Learner profile, diagnostics, lesson progress, consent records
- **Exceptions**: Billing records (required for tax), legal holds

---

## Response Procedure

### Scenario A: Request Approaching SLA (Day 25–29)

**Action**: Prioritize and escalate

1. **Check queue**:
   ```bash
   # List pending erasure requests
   psql -h <db> -U eduboost -c \
     "SELECT id, learner_id, status, requested_at, DATEDIFF(day, requested_at, NOW()) as days_pending FROM erasure_requests WHERE status = 'pending'"
   ```

2. **Assign to engineer** — Triage to engineering backlog

3. **Process request**:
   ```bash
   # Run erasure process
   python -m app.services.popia execute-erasure --request-id <id>
   ```

### Scenario B: Request Exceeded SLA (Day 30+)

**Action**: Immediate escalation + manual processing

1. **Escalate**:
   ```
   🚨 ESCALATION: Erasure SLA Breached
   
   Request ID: <id>
   Days overdue: <N>
   Parent contact: <email>
   Action required: Manual completion + regulator notification
   ```

2. **Complete manually**:
   ```bash
   # Force complete the request
   python -m app.services.popia force-complete --request-id <id>
   ```

3. **Notify parent** — Apologize + explain delay

4. **Document** — Why did this happen?

### Scenario C: Legal Hold Detected

**Action**: Document and extend

1. **Check legal hold reason**:
   ```bash
   psql -h <db> -U eduboost -c \
     "SELECT * FROM erasure_requests WHERE id = <id> AND legal_hold = true"
   ```

2. **Extend with approval**:
   - Get approval from Legal/POPIA Officer
   - Update request with new target date
   - Communicate to parent

3. **Document**:
   - Legal basis for hold
   - Expected release date
   - Approver name

---

## Communication Templates

### Parent Apology Email

```
Subject: Apology — Your Data Request

Dear <Parent Name>,

We sincerely apologize that your data erasure request (ID: <id>) was not completed within our 30-day SLA.

This was due to <brief reason: e.g., high volume, technical issue>.

Your request is now being processed and will be completed by <new date>.

To prevent this from happening again, we've <action taken>.

If you have any questions, please contact privacy@eduboost.co.za.

Regards,
EduBoost Privacy Team
```

### Regulator Notification (for confirmed breach)

```
Subject: POPIA: Delayed Erasure Request Notification

Dear Information Regulator,

We are writing to inform you that EduBoost (Pty) Ltd failed to complete a data erasure request within the statutory 30-day period.

Request Details:
- Request ID: <id>
- Date Received: <date>
- Date Completed: <date>
- Delay: <N> days

Reason for delay: <brief explanation>

We have since completed the request and taken the following steps to prevent recurrence:
- <action 1>
- <action 2>

We regret this non-compliance and commit to ensuring it does not recur.

Regards,
EduBoost Information Officer
```

---

## Prevention

1. **Daily queue check** — Automated alert at day 25
2. **Weekly review** — Engineering team triage
3. **SLA dashboard** — Monitor in Grafana

```bash
# Check current SLA status
python -m app.services.popia sla-status
```

---

## Contacts

| Role | Contact |
|------|---------|
| POPIA Officer | privacy@eduboost.co.za |
| Legal | legal@eduboost.co.za |
| Engineering | engineering@eduboost.co.za |
| Regulator | https://popia.co.za/contact/ |

---

## References

- POPIA Section 17: Right to erasure
- Internal erasure service: `app/services/popia_service.py`
- SLA dashboard: Grafana /popia-sla