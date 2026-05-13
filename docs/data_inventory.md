# Data Inventory

Auto-maintained document. Last updated: 2026-05-13.
Covers §4.4 data minimisation requirements.

---

## Learner Fields

| Field | Purpose | Lawful Basis | Retention | Access Roles | Third-Party |
|-------|---------|-------------|-----------|--------------|-------------|
| `id` (UUID) | Primary key, internal linking | Contract | Lifetime of account | system | None |
| `first_name` | Personalise UI | Consent | Account lifetime | guardian, learner, admin | None |
| `last_name` | Personalise UI | Consent | Account lifetime | guardian, admin | None |
| `grade` | Match CAPS curriculum | Consent | Account lifetime | guardian, learner, teacher | None |
| `language` | Adapt content | Consent | Account lifetime | guardian, learner | None |
| `school_name` | Optional institutional context | Consent | Account lifetime | admin | None |
| `created_at` | Audit trail | Legal obligation | 5 years | admin | None |

> **Minimisation note:** Names are **never** included in LLM prompts. Only
> `learner_id` (tokenised) is passed to AI services.

---

## Guardian Fields

| Field | Purpose | Lawful Basis | Retention | Access Roles | Third-Party |
|-------|---------|-------------|-----------|--------------|-------------|
| `id` (UUID) | Primary key | Contract | Account lifetime | system | None |
| `email` | Authentication, notifications | Contract + Consent | Account lifetime | admin | None |
| `phone_number` (optional) | Consent verification | Consent | Account lifetime | admin | None |
| `created_at` | Audit | Legal obligation | 5 years | admin | None |

---

## Diagnostic Fields

| Field | Purpose | Lawful Basis | Retention | Access Roles | Third-Party |
|-------|---------|-------------|-----------|--------------|-------------|
| `session_id` | Link answers to session | Contract | 2 years | system, admin | None |
| `learner_id` (tokenised) | Link to learner | Contract | 2 years | system | AI service (tokenised) |
| `subject` | Determine question bank | Contract | 2 years | system | None |
| `answers` (JSONB) | Adaptive engine input | Contract | 2 years | system, admin | None |
| `score` | Progress tracking | Contract | 2 years | guardian, teacher | None |

---

## Lesson / AI Fields

| Field | Purpose | Lawful Basis | Retention | Access Roles | Third-Party |
|-------|---------|-------------|-----------|--------------|-------------|
| `lesson_id` | Internal reference | Contract | 1 year | system | None |
| `learner_id` (tokenised) | Link lesson to learner | Contract | 1 year | system | AI provider (tokenised) |
| `prompt_hash` | Audit of AI calls | Legal obligation | 5 years | admin | None |
| `model_version` | Reproducibility | Legal obligation | 5 years | admin | AI provider |
| `content` (JSONB) | Delivered content | Contract | 1 year | learner, guardian | None |

---

## Billing Fields

| Field | Purpose | Lawful Basis | Retention | Access Roles | Third-Party |
|-------|---------|-------------|-----------|--------------|-------------|
| `subscription_id` | Link to plan | Contract | 7 years (SARS) | admin | Payment provider |
| `plan_name` | Determine feature access | Contract | 7 years | admin, guardian | None |
| `billing_email` | Invoice delivery | Contract | 7 years | admin | Payment provider |
| `payment_reference` (tokenised) | Reconciliation | Contract | 7 years | admin | Payment provider |

---

## Identifiers Hashed / Tokenised

- Learner names → never sent to LLM; use `learner_id` (UUID) only
- Payment details → tokenised by payment gateway; raw card data never stored
- Diagnostic prompts → hash stored, not raw text

---

## Non-Essential Fields Removed

- ~~`ip_address`~~ – removed from learner_profiles (not essential)
- ~~`device_fingerprint`~~ – removed (not required for CAPS delivery)
