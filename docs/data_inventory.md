# EduBoost V2 — Data Inventory & Classification (POPIA Compliance)

This document catalogs every personal data field collected by the EduBoost V2 platform, its purpose, lawful basis, and retention period.

## 1. Guardian (Data Subject)
| Field | Purpose | Lawful Basis | Retention | Sensitivity |
|-------|---------|--------------|-----------|-------------|
| `email_hash` | Identity lookup (deterministic) | Contract | Lifetime | Moderate |
| `email_encrypted` | Communications (transactional) | Contract | Lifetime | High |
| `display_name` | UI personalisation | Consent | Lifetime | Low |
| `password_hash` | Authentication | Contract | Lifetime | High |
| `stripe_customer_id` | Billing integration | Contract | 7 years | Moderate |
| `role` | Access control (RBAC) | Contract | Lifetime | Low |

## 2. Learner (Data Subject)
| Field | Purpose | Lawful Basis | Retention | Sensitivity |
|-------|---------|--------------|-----------|-------------|
| `display_name` | UI personalisation | Parental Consent | Lifetime | Low |
| `pseudonym_id` | Analytics linkage (non-identifiable) | Legitimate Interest | Lifetime | Low |
| `grade` | Curriculum alignment | Parental Consent | Lifetime | Low |
| `language` | Content delivery | Parental Consent | Lifetime | Low |
| `theta` | Ability estimate (IRT) | Parental Consent | Lifetime | Moderate |
| `archetype` | Learning style profile | Parental Consent | Lifetime | Moderate |
| `xp` / `streak` | Engagement / Gamification | Parental Consent | Lifetime | Low |

## 3. Parental Consent (Legal Record)
| Field | Purpose | Lawful Basis | Retention | Sensitivity |
|-------|---------|--------------|-----------|-------------|
| `guardian_id` | Linkage to parent | Legal Obligation | 5 years post-revoke | Moderate |
| `learner_id` | Linkage to child | Legal Obligation | 5 years post-revoke | Moderate |
| `policy_version` | Compliance tracking | Legal Obligation | 5 years post-revoke | Low |
| `granted_at` | Audit trail | Legal Obligation | 5 years post-revoke | Low |
| `ip_address_hash` | Non-repudiation | Legal Obligation | 5 years post-revoke | Moderate |

## 4. Audit Log (Append-Only Ledger)
| Field | Purpose | Lawful Basis | Retention | Sensitivity |
|-------|---------|--------------|-----------|-------------|
| `event_type` | Security / Compliance monitoring | Legitimate Interest | 10 years | Low |
| `actor_id` | Accountability | Legitimate Interest | 10 years | Moderate |
| `payload` | Contextual evidence | Legitimate Interest | 10 years | Moderate |

## 5. Third-Party Exposure (Sub-processors)
| Sub-processor | Purpose | Data Shared | Country |
|---------------|---------|-------------|---------|
| Groq / OpenAI | Lesson Generation | Subject, Topic, Grade (Anonymised) | USA |
| Stripe | Payment Processing | Email, Billing Address, Card Details | USA |
| PostHog | Analytics | Pseudonym ID, Event Type | USA |
| Azure | Cloud Hosting | Encrypted DB, Logs, Files | Global / ZA |

---
*Last updated: 2026-05-05*
