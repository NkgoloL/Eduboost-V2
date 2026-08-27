# EduBoost V2: Post-Release Stabilization Dashboard Specification

**Control ID**: `TSR-13.1`  
**Release Gate**: `RG-6`  
**Status**: Authoritative  
**Domain**: Operations / Site Reliability / Quality Governance  

---

## 1. Overview & Stabilization Window

The **14-day post-launch stabilization window** follows any release tag deployment. During this window, feature freeze is maintained, and all operational telemetry is aggregated into the **Stabilization Dashboard**.

---

## 2. Dashboard Panels & Telemetry Feeds

### Panel 1: Reliability & Performance
- **HTTP Request Volume & Error Budget**: Real-time graph of requests/sec by response code (`2xx`, `4xx`, `5xx`).
- **Database Connection Pool & Query Latency**: Active connections vs maximum pool limit; p95/p99 query execution times.
- **Worker Queue Health**: Background Celery/Redis queue depth, task failure count, and retry latency.

### Panel 2: Security, Privacy & DSR
- **POPIA Erasure Queue**: Volume of pending, processing, and completed DSR erasure requests.
- **Session Revocation Rate**: Real-time rate of user logouts, refresh token rotations, and forced expirations.
- **WAF / Rate Limiter Drops**: Counts of blocked requests originating from abusive IP ranges or malformed signatures.

### Panel 3: AI Pipeline & Resource Consumption
- **Token Ingestion & Generation Count**: Cumulative token usage against the daily ceiling.
- **Circuit Breaker Status**: State of external model providers (`CLOSED`, `HALF_OPEN`, `OPEN`).
- **Safety Violation Flags**: Alerts on any flagged prompt injections or unaligned learner interactions.

### Panel 4: Educational Engagement & Quality
- **Learner Active Sessions**: Concurrent active learners in practice exercises.
- **Item Response Correctness Distribution**: Aggregated item difficulty curve (IRT verification).
- **Mastery Score Cap Conformity**: Continuous assertion that zero learner mastery states exceed `0.85`.

---

## 3. Daily & Weekly Review Cadence

1. **Daily Standup Audit (09:00 SAST)**:
   - Review 24h error budget burn rate.
   - Audit any Sev 1 / Sev 2 incident tickets filed in the defect register.
   - Inspect daily database backup verification checksums.
2. **Weekly Executive Health Rollup**:
   - Aggregate weekly uptime (target $\ge 99.9\%$).
   - Review learner and educator feedback tickets.
   - Publish stabilization status update to repository evidence archive.
