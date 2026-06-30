---
title: "AI Transparency FAQ — EduBoost"
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

# AI Transparency FAQ — EduBoost

**Last Updated**: 2026-06-12  
**Audience**: Parents, educators, regulators

---

## How EduBoost Uses AI

EduBoost uses artificial intelligence to personalize learning for each student. This document explains what AI we use, how it works, and what data is involved.

---

## AI Systems in EduBoost

### 1. Lesson Generation

**Purpose**: Generate personalized lessons based on learner's diagnostic results

**How it works**:
1. Learner completes a diagnostic assessment
2. AI analyzes which topics the learner has mastered vs. needs to practice
3. AI generates a lesson targeting the learner's specific gaps
4. Lesson includes teaching content, examples, and practice questions

**Data sent to AI**:
- Learner's diagnostic responses (anonymized topic IDs)
- CAPS curriculum content for the topic
- Learning objective for the lesson

**Data NOT sent**:
- Learner's name or identity
- Parent/guardian information
- Any personal identifying information

### 2. Adaptive Difficulty

**Purpose**: Adjust question difficulty based on learner performance

**How it works**:
- Uses Item Response Theory (IRT) to estimate ability
- Selects questions at appropriate difficulty level
- Continuously updates ability estimate as learner answers

### 3. Content Safety Filtering

**Purpose**: Prevent inappropriate or harmful content from being shown to learners

**How it works**:
- All AI-generated content passes through safety filters
- Content flagged as harmful is rejected and regenerated
- Safety filters are regularly updated

---

## Data Sent to External AI Providers

### Which Providers?

| Provider | Purpose | Data Shared |
|----------|---------|--------------|
| Groq | Primary lesson generation | Topic context, curriculum data |
| Anthropic Claude | Fallback provider | Topic context, curriculum data |

### What data is shared?

When generating lessons, we send:

- ✅ CAPS topic content (e.g., "multiplication Grade 4")
- ✅ Learning objective
- ✅ Example questions from our item bank
- ✅ General context (grade level, subject)

We do NOT send:

- ❌ Learner name
- ❌ Learner email
- ❌ Parent/guardian information
- ❌ Any personally identifiable information
- ❌ School name (unless explicitly provided)
- ❌ Assessment responses linked to identity

---

## Safety Measures

### Content Filters

- All generated content passes through multiple safety filters
- Topics related to hate speech, violence, sexual content, etc. are blocked at the system level
- Human review of AI outputs before learner access

### Human Oversight

- Weekly reviews of AI-generated content samples
- Feedback loop to improve safety filters
- Flagging system for teachers/parents to report concerns

### Age-Appropriate Design

- Content is always grade-appropriate
- No adult themes or mature content
- Language simplified for younger learners

---

## Learner Data & AI

### Can AI see my child's answers?

No. Learner responses to diagnostic questions are processed by our IRT engine locally. Only anonymized topic performance data (e.g., "multiplication: 70%") is used for lesson selection — never linked to learner identity.

### Will AI replace teachers?

No. EduBoost is designed to supplement classroom teaching, not replace it. Teachers can:

- View learner progress data
- Generate reports for intervention planning
- Override AI lesson recommendations if needed

### Can I opt out of AI features?

Some AI features are core to the service:

- ❌ Cannot opt out: Adaptive difficulty (part of diagnostics)
- ✅ Can opt out: AI-generated lessons (limited to pre-built content only)

Manage consent in **Settings** → **Consent Management**.

---

## Transparency Commitments

1. **No hidden AI**: All AI-generated content is clearly marked in the system
2. **No identity sharing**: PII is never sent to external AI providers
3. **Human review**: Regular sampling of AI outputs by human reviewers
4. **Explainable**: IRT scores are interpretable by teachers and parents
5. **Auditable**: All AI decisions are logged for compliance

---

## Questions?

If you have questions about how EduBoost uses AI:

- **Email**: ai-safety@eduboost.co.za
- **Technical Details**: See our [Technical Architecture](../architecture/README.md)

---

## Related Documentation

- [Product Overview](../product/product_overview.md)
- [Privacy Policy](https://eduboost.co.za/privacy)
- [Parent Guide](../product/parent_guide.md)
- [POPIA Compliance](../compliance/popia_data_rights.md)