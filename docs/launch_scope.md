# Production Launch Scope (v1.0)

This document defines the features, content, and limitations for the EduBoost V2 production launch.

## 1. Supported Educational Content
- **Grades**: R through 7.
- **Subjects**: Mathematics, English (Home Language), Natural Sciences & Technology (Grade 4-7).
- **CAPS Alignment**: 100% coverage for Term 1 & 2 topics for the above grades.
- **Languages**: English (Instructional), with support for key terminology in Afrikaans and isiZulu.

## 2. Core Features
- **Learner Portal**:
    - Diagnostic assessment (IRT-based).
    - Personalized study plans.
    - AI-generated lesson explanations.
    - Practice exercises with immediate feedback.
- **Parent/Guardian Portal**:
    - Learner progress tracking.
    - Consent management (POPIA compliant).
    - Performance reports (PDF).
- **Gamification**:
    - Points, streaks, and basic badges.

## 3. Operational Features
- **Authentication**: Secure email/password login with JWT family rotation.
- **Audit**: Append-only audit ledger for all sensitive actions.
- **POPIA**: Full Right to Access (Export) and Right to Erasure (Deletion).

## 4. Known Limitations (Out of Scope)
- **Offline Mode**: Full offline capability is deferred to v1.1.
- **Teacher/Classroom Dashboard**: Institutional features are limited to early-access partners.
- **Mobile Apps**: Launch is Web-only (Responsive). Native apps are in the roadmap.
- **Live Tutoring**: No synchronous human interaction in this version.

## 5. Unsupported Features
- External LMS integrations (LTI).
- Third-party SSO (Google/Microsoft) - deferred to v1.2.
- Complex group/team-based learning activities.
