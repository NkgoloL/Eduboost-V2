# Grade 4 Mathematics — Lesson Coverage Matrix

**EduBoost SA  ·  AI Lesson Quality Dashboard  ·  Phase 5 Deliverable (L5-09)**  
*docs/caps/grade4_maths_lesson_coverage_matrix.md*

---

## Purpose

This document is the canonical coverage matrix for AI-generated Grade 4 Mathematics lessons in the EduBoost platform.  It provides a single, auditable view of:

- How many lessons exist per CAPS reference.
- How many of those lessons have been approved by a human reviewer.
- The distribution of quality scores and answer-key verification rates.
- The overall Milestone C readiness status for each topic.

This document is **auto-updated** by `scripts/generate_coverage_matrix.py` after each generation or review batch.  Do not edit it manually — edit the script or the lesson database instead.

---

## CAPS Reference Coding Scheme

| Component | Example | Description |
|---|---|---|
| Grade | 4 | Grade level |
| Subject | M | M = Mathematics |
| Term | 1 | CAPS term (1–4) |
| Topic Index | 1 | Topic within that term (1-based) |
| Subtopic Index | 1 | Subtopic within topic (optional) |
| **Full Example** | **4.M.1.1** | Grade 4 · Maths · Term 1 · Topic 1 (Whole Numbers) |

---

## Launch Scope: Grade 4 Mathematics

Launch scope for **Milestone C** covers Term 1, Topics 1–3 (three `caps_ref` values).  Full Grade 4 coverage across all four terms is targeted for the General Availability release.

---

## Coverage Table — Term 1 (Launch Scope)

| CAPS Ref | Topic | Subtopic | Total Lessons | Approved | In Review | Rejected | Avg Quality Score | AKV Pass Rate | Milestone C Ready |
|---|---|---|---|---|---|---|---|---|---|
| **4.M.1.1** | Whole Numbers | Ordering and Comparing 4-digit Numbers | — | — | — | — | — | — | ⬜ Pending |
| **4.M.1.2** | Common Fractions | Understanding Fractions as Part of a Whole | — | — | — | — | — | — | ⬜ Pending |
| **4.M.1.3** | 2D Shapes | Identifying and Naming 2D Shapes | — | — | — | — | — | — | ⬜ Pending |

> **Note:** The `—` values above will be populated by `scripts/generate_coverage_matrix.py` once lessons are generated and reviewed in Phase 3.  Milestone C requires **≥8 approved lessons per caps_ref** with `answer_key_verified=true` and `quality_score ≥ 0.7`.

---

## Coverage Table — Term 2 (Post-Launch)

| CAPS Ref | Topic | Subtopic | Total | Approved | In Review | Rejected | Avg Quality | AKV % | Status |
|---|---|---|---|---|---|---|---|---|---|
| 4.M.2.1 | Whole Numbers | Addition and Subtraction up to 5-digit Numbers | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.2.2 | Multiplication | 2-digit × 2-digit | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.2.3 | Division | Division with Remainders | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.2.4 | Measurement | Length (mm, cm, m, km) | — | — | — | — | — | — | 🔜 Post-launch |

---

## Coverage Table — Term 3 (Post-Launch)

| CAPS Ref | Topic | Subtopic | Total | Approved | In Review | Rejected | Avg Quality | AKV % | Status |
|---|---|---|---|---|---|---|---|---|---|
| 4.M.3.1 | Fractions | Equivalent Fractions | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.3.2 | Whole Numbers | Multiplication up to 99 × 99 | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.3.3 | Data Handling | Bar Graphs and Pictographs | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.3.4 | Geometry | 3D Objects | — | — | — | — | — | — | 🔜 Post-launch |

---

## Coverage Table — Term 4 (Post-Launch)

| CAPS Ref | Topic | Subtopic | Total | Approved | In Review | Rejected | Avg Quality | AKV % | Status |
|---|---|---|---|---|---|---|---|---|---|
| 4.M.4.1 | Whole Numbers | Division, including Long Division | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.4.2 | Decimals | Introduction to Decimal Fractions | — | — | — | — | — | — | 🔜 Post-launch |
| 4.M.4.3 | Probability | Simple Probability Language | — | — | — | — | — | — | 🔜 Post-launch |

---

## Quality Score Distribution (Launch Scope)

*To be populated by `generate_coverage_matrix.py` after Phase 3 generation.*

| CAPS Ref | ≥0.9 | 0.8–0.9 | 0.7–0.8 | <0.7 (Review Queue) |
|---|---|---|---|---|
| 4.M.1.1 | — | — | — | — |
| 4.M.1.2 | — | — | — | — |
| 4.M.1.3 | — | — | — | — |

---

## Answer-Key Verification Rate

All Milestone C approved lessons must have `answer_key_verified = true`.  A second independent LLM call re-solves every practice question without seeing the original answer key.  Any lesson where the second call disagrees with any answer is automatically queued for human review and cannot be marked approved until a reviewer resolves the disagreement.

| CAPS Ref | Total Generated | AKV Pass | AKV Fail (→ Review Queue) | AKV Pass Rate |
|---|---|---|---|---|
| 4.M.1.1 | — | — | — | — |
| 4.M.1.2 | — | — | — | — |
| 4.M.1.3 | — | — | — | — |

---

## Human Review Summary

| CAPS Ref | Awaiting Review | Reviewed | Approved | Rejected | Avg Review Latency |
|---|---|---|---|---|---|
| 4.M.1.1 | — | — | — | — | — |
| 4.M.1.2 | — | — | — | — | — |
| 4.M.1.3 | — | — | — | — | — |

---

## Milestone C Definition of Done — Per Caps Ref

Each of the three launch `caps_ref` values must satisfy all of the following before Milestone C can be marked complete:

| Gate | Requirement | Verified By |
|---|---|---|
| **1** | ≥8 lessons with `review_status = approved` | CI assertion (L5-04) |
| **2** | Every approved lesson has `answer_key_verified = true` | `lesson_validator.py` rule 3 |
| **3** | Every approved lesson has ≥2 worked examples | `lesson_validator.py` rule 4 |
| **4** | Every approved lesson has ≥3 practice questions | `lesson_validator.py` rule 5 |
| **5** | Every approved lesson has `safety_classification = safe` | `lesson_validator.py` rule 7 |
| **6** | Every approved lesson has `caps_ref` resolving in topic map | `caps_topic_map_service.py` |
| **7** | Every approved lesson has a non-null `reviewer_id` | `lesson_review_router.py` |
| **8** | `validate_lessons.py` reports 0 failures across approved lessons | CI job (L5-05) |
| **9** | Lesson regression suite passes after latest prompt version | CI regression job (L5-06) |
| **10** | Prometheus metrics live and visible in Grafana panel | Grafana panel (L5-10) |

---

## AI Transparency Labels

Every lesson rendered in the frontend displays a trust label:

| Label Component | Value | Source |
|---|---|---|
| CAPS-linked | ✅ Yes | `caps_ref` resolves in topic map |
| Answer-checked | ✅ Yes / ⚠️ Pending | `answer_key_verified` field |
| AI-generated | ✅ Always shown | `provider` field |
| Teacher-reviewed | ✅ Yes / ⬜ Pending | `review_status = approved` + `reviewer_id` non-null |

Learners and guardians can tap "Report a content problem" on any lesson to submit it directly to the human review queue.

---

## How to Update This Document

```bash
# After a generation or review batch:
python scripts/generate_coverage_matrix.py \
  --output docs/caps/grade4_maths_lesson_coverage_matrix.md

# For a specific caps_ref only:
python scripts/generate_coverage_matrix.py \
  --caps-refs 4.M.1.1 4.M.1.2 4.M.1.3 \
  --output docs/caps/grade4_maths_lesson_coverage_matrix.md
```

The script queries the live lesson database and rewrites the `—` cells with real values.  Commit the updated document to the repository after each generation or review sprint.

---

*EduBoost SA  ·  docs/caps/grade4_maths_lesson_coverage_matrix.md  ·  Phase 5 (L5-09)  ·  10 May 2026*
