---
title: "EduBoost Product Overview"
status: active
owner: product
reviewers: [product, curriculum, release-management]
audience: stakeholder
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/product/README.md]
---

# EduBoost Product Overview

**Last Updated**: 2026-06-12  
**Audience**: Prospective users, school administrators, investors, partners

---

## What is EduBoost?

EduBoost is an AI-powered adaptive learning platform designed for South African students in Grades R to 7. Built on the South African CAPS (Curriculum and Assessment Policy Statement) curriculum, EduBoost delivers personalized learning experiences through interactive diagnostics, AI-generated lessons, and gamified practice.

---

## Our Mission

To democratize access to quality education in South Africa by providing every learner — regardless of socioeconomic background — with personalized, AI-driven instruction that adapts to their unique learning pace and style.

---

## Who We Serve

| Audience | Description |
|----------|-------------|
| **Primary Learners** | Grades R–7 students (ages 5–13) in South African schools |
| **Parents/Guardians** | Monitoring progress, managing consent, upgrading to premium |
| **Teachers** | Viewing assigned learner progress, accessing class-level analytics |
| **Schools** | Institutional accounts with teacher management and reporting |

---

## Core Features

### 1. Adaptive Diagnostics
- Initial placement assessment identifies knowledge gaps
- Continuous diagnostic checks track progress
- IRT-powered item bank ensures accurate ability estimation
- Topics covered: Mathematics, Language (English/Afrikaans)

### 2. AI-Generated Lessons
- Lessons generated dynamically based on learner gaps
- CAPS-aligned content for all topics
- Distractors designed to expose common misconceptions
- Safety filters prevent inappropriate content

### 3. Gamification
- XP points for completed activities
- Achievement badges for milestones
- Streak tracking for daily engagement
- Leaderboards (optional per class)

### 4. Progress Tracking
- Real-time dashboards for parents and teachers
- Topic-level mastery visualization
- Exportable progress reports

### 5. Privacy & Consent
- POPIA-compliant consent management
- Parent/guardian approval required for minors
- Data export and erasure rights

---

## Technology Stack

| Component | Technology |
|-----------|-------------|
| Frontend | Next.js 15, React 19, TypeScript |
| Backend | FastAPI (Python 3.12), SQLAlchemy 2.0 |
| Database | PostgreSQL 16 (Azure Database for PostgreSQL - Flexible Server) |
| Cache/Sessions | Redis 7 (Azure Cache for Redis) |
| AI/LLM | Groq (primary), Anthropic Claude (fallback) |
| Deployment | Azure Container Apps, Docker |
| Observability | Grafana Cloud, Sentry |

---

## Pricing Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Free** | R0/month | Basic diagnostics, limited lessons per day (20), ads-supported |
| **Parent** | R149/month | Unlimited diagnostics, unlimited lessons, no ads, progress reports |
| **School** | R99/student/year | All Parent features + teacher dashboards, class analytics, bulk onboarding |

---

## Data Privacy

EduBoost is fully POPIA (Protection of Personal Information Act) compliant:

- **Lawful Basis**: Consent from parent/guardian for minors; legitimate interest for educational purposes
- **Data Minimization**: Only collected data necessary for service delivery
- **Security**: Field-level encryption, TLS in transit, audit logging
- **Rights**: Export, correction, and erasure available via self-service portal

See our [Privacy Policy](https://eduboost.co.za/privacy) for full details.

---

## Getting Started

1. **Sign Up**: Visit [eduboost.co.za](https://eduboost.co.za) and create an account
2. **Add Learner**: Add your child(ren) to your guardian account
3. **Consent**: Review and approve consent terms for each learner
4. **Start Learning**: Learner completes initial diagnostic → AI generates personalized learning path

---

## Contact

- **Support**: support@eduboost.co.za
- **Sales**: schools@eduboost.co.za
- **Privacy Inquiries**: privacy@eduboost.co.za

---

## Version

This document reflects EduBoost V2 as of the production release (June 2026).