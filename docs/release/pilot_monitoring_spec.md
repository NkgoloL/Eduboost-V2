# EduBoost V2: Controlled Production Pilot Monitoring & Telemetry Specification

**Control ID**: `TSR-12.5`  
**Release Gate**: `RG-5`  
**Status**: Authoritative  
**Domain**: Operations / Telemetry / Learner Safety  

---

## 1. Overview & Pilot Objectives

This specification defines the real-time telemetry, service level indicators (SLIs), service level objectives (SLOs), and safety tripwires for the controlled, time-boxed EduBoost V2 pilot.

The controlled pilot is constrained to:
- Max Cohort Size: 50 consented learners (Grade 4–9 CAPS Mathematics).
- Commercial Status: **FAIL-CLOSED** (Zero live billing / Zero paid subscriptions).
- Environment: Isolated staging/canary runtime with audit immutability enabled.

---

## 2. Core Telemetry Dimensions & SLIs

### A. API Health & Latency
| Metric | Threshold (SLO) | Alert Condition | Action on Breach |
| :--- | :--- | :--- | :--- |
| **API Error Rate (`5xx`)** | $< 0.1\%$ | $\ge 0.5\%$ over 5 min window | Page On-Call, Route Throttling |
| **API Latency (`p95`)** | $< 250\text{ms}$ | $> 750\text{ms}$ over 10 min window | Auto-scale worker containers |
| **API Latency (`p99`)** | $< 500\text{ms}$ | $> 1500\text{ms}$ over 5 min window | Degrade non-essential telemetry |

### B. Security & Privacy Invariants
| Metric | Target | Hard Tripwire | Response Protocol |
| :--- | :--- | :--- | :--- |
| **POPIA DSR Processing Latency** | $< 24\text{h}$ | $> 48\text{h}$ pending request | Immediate operational escalation |
| **PII Leakage in Sentry/Logs** | $0$ events | $\ge 1$ unmasked PII event | Instant Pilot Freeze (`FAIL_CLOSED`) |
| **Unauthorized Role Escalation** | $0$ events | $\ge 1$ forbidden access attempt | Token revocation cascade & quarantine |

### C. AI Tutor & Budget Guardrails
| Metric | Target | Hard Tripwire | Response Protocol |
| :--- | :--- | :--- | :--- |
| **Daily LLM Token Consumption** | $< 100,000$ tokens/day | $\ge 150,000$ tokens/day | Circuit breaker trips; fallback to static hints |
| **Hallucination / Guardrail Flag** | $< 0.5\%$ of responses | $\ge 2\%$ of responses | LLM tutor disabled for cohort |
| **Safety Filter Trigger Rate** | $< 0.1\%$ | $\ge 1.0\%$ | Immediate transcript audit |

### D. Educational & Mastery Integrity
| Metric | Invariant | Tripwire |
| :--- | :--- | :--- |
| **Confidence Cap Violations** | $0$ (Never $> 0.85$ without LEV) | Any `mastery_score > 0.85` flagged authoritative |
| **Curriculum Inversion / Cycle** | $0$ cycles detected | Graph validation exception in session planner |

---

## 3. Telemetry Ingestion Architecture

1. **Structured JSON Logs**: All application logs emit ISO-8601 timestamps, tenant identifiers, and request correlation IDs with PII masking pre-applied via `app/core/pii_sanitizer.py`.
2. **Prometheus Metrics Exporter**: `/metrics` endpoint guarded by internal network isolation exposing request rates, database connection pool utilization, and circuit breaker trip states.
3. **Audit Ledger Verification**: Hourly checksum validation of `audit_events` append-only database partition to ensure record immutability.
