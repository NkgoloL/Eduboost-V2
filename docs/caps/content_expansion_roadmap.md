# CAPS Content Expansion Roadmap

**Date**: 2026-06-12  
**Version**: 1.0  
**Scope**: Grades R–7 coverage expansion beyond current Grade 4 Maths focus

---

## Executive Summary

This roadmap outlines the phased expansion of CAPS-aligned content across all required grades (R–7) and subjects. Currently, Grade 4 Mathematics has partial coverage. This plan addresses Foundation (R–3), Intermediate (4–6), and Senior (7) phases.

---

## Current State (as of 2026-06-12)

| Grade | Subject | Items | Lessons | Coverage % |
|-------|---------|-------|---------|------------|
| 4 | Mathematics | ~120 | ~40 | 45% |
| — | Other grades | 0 | 0 | 0% |

**Existing artifacts**:
- `docs/caps/grade4_maths_coverage_matrix.md` — Item-level breakdown
- `docs/caps/grade4_maths_lesson_coverage_matrix.md` — Lesson coverage

---

## Phase 1: Foundation Phase (Grades R–3)

### Target: End of Q3 2026

| Grade | Subject | Est. Items | Est. Lessons | Priority |
|-------|---------|------------|--------------|----------|
| R | Home Language (English) | 50 | 20 | P1 |
| R | Mathematics | 50 | 20 | P1 |
| 1 | Home Language (English) | 100 | 40 | P1 |
| 1 | Mathematics | 100 | 40 | P1 |
| 2 | Home Language (English) | 100 | 40 | P2 |
| 2 | Mathematics | 100 | 40 | P2 |
| 3 | Home Language (English) | 100 | 40 | P2 |
| 3 | Mathematics | 100 | 40 | P2 |

### Subjects Not in Phase 1
- First Additional Language (deferred to Phase 2)
- Life Skills (deferred to Phase 3)

**Est. Effort**: 400 items + 160 lessons  
**Source Strategy**: OER (Open Educational Resources), AI-assisted generation with human review

---

## Phase 2: Intermediate Phase Expansion (Grades 4–6)

### Target: End of Q4 2026

| Grade | Subject | Est. Items | Est. Lessons | Priority |
|-------|---------|------------|--------------|----------|
| 4 | Mathematics | 150 (+30) | 60 (+20) | Complete |
| 5 | Mathematics | 120 | 50 | P1 |
| 6 | Mathematics | 120 | 50 | P1 |
| 4-6 | Home Language (English) | 200 | 80 | P2 |
| 4-6 | First Additional Language | 150 | 60 | P3 |

**Est. Effort**: 740 items + 260 lessons

---

## Phase 3: Senior Phase (Grade 7) + Languages

### Target: End of Q1 2027

| Grade | Subject | Est. Items | Est. Lessons | Priority |
|-------|---------|------------|--------------|----------|
| 7 | Mathematics | 150 | 60 | P1 |
| 7 | Natural Sciences | 100 | 40 | P2 |
| 7 | Social Sciences | 100 | 40 | P2 |
| 7 | Home Language (English) | 100 | 40 | P2 |
| 4-7 | Afrikaans (FAL) | 200 | 80 | P2 |
| 4-7 | isiZulu (FAL) | 200 | 80 | P2 |

**Est. Effort**: 850 items + 340 lessons

---

## Content Generation Strategy

### Tier 1: AI-Assisted (Primary)
1. Generate item/lesson drafts using LLM with CAPS prompt templates
2. Human review for accuracy and age-appropriateness
3. Item bank insertion

### Tier 2: OER Acquisition
- Siyavula (partnership pending)
- OER Commons
- Department of Basic Education materials

### Tier 3: Manual Development
- High-priority content requiring exact accuracy
- Assessment rubrics

---

## Quality Gates

| Stage | Gate | Criteria |
|-------|------|----------|
| Generation | AI Quality | LLM output passes Judiciary gate |
| Review | Human Review | Subject matter expert approval |
| Staging | Pilot | 80% learner completion rate |
| Production | Promotion | <1% error rate in production |

---

## Dependencies

- **LLM Provider**: Groq/Anthropic for generation (see `app/modules/lessons/`)
- **Content Factory**: `app/services/content_factory/` for item generation
- **Item Bank**: `app/repositories/item_bank_repository.py` for storage

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM quality varies by subject | Medium | Human review mandatory for all AI content |
| Grade R-3 requires special design | High | Engage early childhood educators |
| Language accuracy for FAL | Medium | Native speaker review for Afrikaans/isiZulu/isiXhosa |

---

## Success Metrics

- **Coverage**: % of CAPS topics with at least one item/lesson
- **Quality**: Item difficulty calibration (IRT) within 30 days
- **Usage**: Learner engagement with non-Maths subjects

---

## References

- CAPS curriculum: https://www.education.gov.za/CAPS.aspx
- Current Grade 4 Maths coverage: `docs/caps/grade4_maths_coverage_matrix.md`
- Content Factory service: `app/services/content_factory/`
- Item generation prompts: `app/modules/lessons/prompts/`