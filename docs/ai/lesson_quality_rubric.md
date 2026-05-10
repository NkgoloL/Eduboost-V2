# Lesson Quality Rubric — Human Reviewer Checklist

**EduBoost SA · AI-Generated Lesson Review · Grade 4 Mathematics (Launch Scope)**
*Phase 4 — L4-03 · Confidential — May 2026*

---

## Purpose

Every AI-generated lesson that enters the human review queue must be assessed
against this rubric before it can be marked `approved` and served to learners.
The checklist has **8 mandatory items**. A lesson fails review if **any item
scores 0**. A lesson with one or more items scoring 1 (needs work) should be
sent back for re-generation unless the reviewer can correct the issue directly.

---

## How to Use This Rubric

1. Open the lesson in the reviewer interface (`GET /api/v2/lessons/review/queue`).
2. Work through the 8 items below in order.
3. Score each item: **2 = Pass**, **1 = Minor issue (correctable)**, **0 = Fail**.
4. Record notes in the `reviewer_notes` field of the review submission.
5. Submit your decision via `POST /api/v2/lessons/{id}/review`.

A total score of **14–16 = Approved**, **10–13 = Conditional (note required)**,
**< 10 = Reject and re-generate**.

---

## Checklist Items

### Item 1 — CAPS Accuracy ✅

**Question:** Does the lesson accurately reflect the CAPS curriculum for the
stated grade, term, topic, and subtopic?

| Score | Criteria |
|-------|----------|
| **2** | `caps_ref` resolves correctly in the canonical topic map. Learning objectives precisely match the CAPS assessment standards for that subtopic. No off-topic content is present. |
| **1** | Minor phrasing misalignment in objectives but the conceptual content is correct and CAPS-aligned. |
| **0** | Wrong topic, wrong grade, wrong term, or learning objectives that contradict CAPS standards. |

**Reviewer notes to check:**
- Verify `caps_ref` (e.g. `4.M.1.1`) against the [Grade 4 Maths Topic Map](../../data/caps/caps_topic_map_grade4_maths.json).
- Confirm that all three learning objectives correspond to CAPS performance indicators.
- Check that worked examples use numbers, shapes, or contexts appropriate to the grade.

---

### Item 2 — Answer Correctness 🔢

**Question:** Are all answers in the answer key and worked examples mathematically correct?

| Score | Criteria |
|-------|----------|
| **2** | `answer_key_verified = true`. All worked example solutions are step-by-step correct. All practice question answers are correct and match the answer key. No arithmetic errors detected. |
| **1** | `answer_key_verified = true` but one minor formatting issue in a worked example (not a computational error). |
| **0** | `answer_key_verified = false`. Any incorrect answer in the answer key or worked examples. Any arithmetic error that would mislead a learner. |

**Reviewer notes to check:**
- Do **not** approve any lesson with `answer_key_verified = false`. Return it for re-generation.
- Manually solve at least one practice question independently to spot-check.
- Check that step-by-step solutions are sequential and each step is explained.

---

### Item 3 — South African Context 🇿🇦

**Question:** Does the lesson use authentic South African contexts, currency,
geography, and everyday references appropriate for a Grade 4 learner?

| Score | Criteria |
|-------|----------|
| **2** | All examples use ZAR (rand/cents), SA place names, SA school calendar, or everyday SA contexts (e.g. taxi, spaza shop, braai, school tuck shop). No foreign currency, US/UK references, or culturally inappropriate context. |
| **1** | Mostly appropriate but one example uses a neutral/generic context that could be made more SA-specific. |
| **0** | Uses foreign currency, foreign place names, or contexts that are clearly non-South African or inappropriate for SA learners. |

**Reviewer notes to check:**
- Is currency in Rand (R) and cents?
- Are place names South African (Johannesburg, Cape Town, Durban, rural areas)?
- Are the scenarios believable for a Grade 4 learner in a South African school?

---

### Item 4 — Age-Appropriateness 🧒

**Question:** Is the language, complexity, and content appropriate for a
9–10 year old Grade 4 learner?

| Score | Criteria |
|-------|----------|
| **2** | Reading level ≤ Grade 6 Flesch-Kincaid (≤ FK 6.0). Short sentences. No jargon. Concrete and visual explanations. Content is emotionally and psychologically appropriate for a 9–10 year old. |
| **1** | Slightly complex in one section but overall accessible. No concerning content. |
| **0** | Complex adult vocabulary. Emotionally inappropriate themes. Content that could distress, confuse, or harm a child. |

**Reviewer notes to check:**
- Can you read the explanation aloud and imagine a Grade 4 learner understanding it?
- Is `language_level` (Flesch-Kincaid) ≤ 6.0?
- Are there any words a Grade 4 learner would not know (without explanation)?

---

### Item 5 — Explanation Clarity 📖

**Question:** Is the main explanation clear, logically structured, and capable
of teaching the concept without a teacher present?

| Score | Criteria |
|-------|----------|
| **2** | Explanation introduces the concept, builds understanding step-by-step, uses concrete examples before abstract rules, and matches the stated learning objectives. A learner could follow it independently. |
| **1** | Explanation is mostly clear but skips one logical step or uses one unexplained term. |
| **0** | Explanation is incomplete, jumps to conclusions, uses undefined jargon, or does not match the stated learning objectives. |

**Reviewer notes to check:**
- Does the explanation follow: concrete → pictorial → abstract (CPA approach for SA maths)?
- Are all key terms defined when first introduced?
- Does it directly support the `learning_objectives`?

---

### Item 6 — Distractor Quality (MCQ) ❓

**Question:** Are the wrong-answer options in practice questions based on
real, common Grade 4 misconceptions — not random wrong numbers?

| Score | Criteria |
|-------|----------|
| **2** | Every distractor represents a specific, named misconception (e.g. "place value confusion: learner adds digits instead of values"). Each wrong answer is plausible and educational. |
| **1** | Most distractors are misconception-anchored but one or two are generic wrong numbers without pedagogical basis. |
| **0** | Distractors are random, implausible, or so obviously wrong that they do not challenge thinking or reveal misconceptions. |

**Reviewer notes to check:**
- Do the `remediation_hints` correspond to the wrong-answer distractors?
- Would a real Grade 4 learner plausibly choose each distractor?
- Are there at least 3 practice questions, each with 3–4 options?

---

### Item 7 — PII & Brand Check 🔒

**Question:** Does the lesson contain any Personally Identifiable Information
(PII) or real brand names that should not appear in educational content?

| Score | Criteria |
|-------|----------|
| **2** | No real names (learner or teacher), no ID numbers, no phone numbers, no addresses, no brand names (e.g. Coca-Cola, Nike), no school-specific names. `pii_check_passed = true`. |
| **1** | A common first name is used in a story context (acceptable if clearly fictional). No actual PII. |
| **0** | Any real or realistic PII. Any commercial brand name used in a way that could constitute advertising. `pii_check_passed = false`. |

**Reviewer notes to check:**
- Are names used in word problems clearly generic/fictional (e.g. "Sipho", "Amahle" — common SA names are fine as fictional characters)?
- Are there no product brand names, social media platforms, or commercial entities referenced?
- Is `pii_check_passed = true` on the lesson record?

---

### Item 8 — Cultural Sensitivity & Inclusiveness 🌍

**Question:** Is the content culturally appropriate, respectful, and inclusive
for all learners in a South African classroom?

| Score | Criteria |
|-------|----------|
| **2** | Content reflects the diversity of South African learners. Names and contexts represent multiple SA cultural groups. No stereotypes, no gender bias in examples, no assumptions about family structure or socioeconomic status that could make a learner feel excluded. |
| **1** | Mostly inclusive but one example defaults to a single cultural context without variety. |
| **0** | Stereotypes present. Culturally insensitive language. Content that could make a learner from any SA background feel excluded or marginalised. |

**Reviewer notes to check:**
- Do names in examples reflect a mix of SA cultural backgrounds (Zulu, Xhosa, Sotho, Afrikaans, English)?
- Are both male and female names used across examples?
- Does the content assume learners have access to resources not all SA children have (e.g. a computer, a pool)?
- Does any content reflect negatively on any language, religion, or cultural group?

---

## Review Decision Guide

| Total Score | Decision | Action |
|-------------|----------|--------|
| **14 – 16** | ✅ **Approve** | Submit `decision: "approved"`. Lesson enters the active bank. |
| **10 – 13** | ⚠️ **Conditional** | Submit `decision: "approved"` only if you can correct the issue in `reviewer_notes` and the corrections are minor. Otherwise reject. |
| **< 10** | ❌ **Reject** | Submit `decision: "rejected"`. Lesson is removed from the queue and re-generation is triggered. Document which rules failed in `reviewer_notes`. |
| **Any Item = 0** | ❌ **Reject** | Any single item scoring 0 is a hard reject regardless of total score. |

---

## Escalation

If you encounter content that is:
- Potentially harmful to a child
- Factually dangerous (medical, safety-related misinformation)
- Legally concerning (copyright, defamation)

→ Immediately mark as `rejected`, add detailed notes, and escalate to the
curriculum lead and product owner before re-generation is attempted.

---

## Reviewer Accountability

- Your `reviewer_id` and `reviewed_at` timestamp are permanently recorded on the lesson.
- Approved lessons carry your endorsement and may be served to learners.
- Periodic audits will cross-check reviewer decisions against the quality score.
- Disagreements between reviewers should be resolved by the curriculum lead.

---

*EduBoost SA — Curriculum & AI Quality Team · May 2026*
*For questions: open a GitHub issue tagged `curriculum-review` or contact the AI safety lead.*
