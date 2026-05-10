# Grade 4 Mathematics — CAPS Item Bank Coverage Matrix

> **Auto-generated** from `scripts/generate_coverage_matrix.py`  
> Last updated: <!-- GENERATED_AT -->  
> Repository: [nkgolo-lebelo/Eduboost](https://github.com/nkgolo-lebelo/Eduboost)  
> Roadmap reference: Priority Action #6 of 11.3 · Phase 5 · Task P5-07

---

## Summary

| Metric | Value |
|--------|-------|
| **Launch Grade** | Grade 4 |
| **Launch Subject** | Mathematics |
| **Launch Scope** | Term 1 (Topics 1–3) |
| **Target Items per Topic** | ≥ 40 approved |
| **Total Target** | ≥ 120 approved |
| **Definition of Done** | All 3 CAPS refs ≥ 40 approved · `validate_item_bank.py` 0 failures · CI green |

---

## Coverage by CAPS Reference

Each row represents one CAPS topic cluster. The **Status** column reflects the
current review pipeline state. A cluster is **✅ READY** only when it has ≥ 40
approved, safety-cleared, human-reviewed items covering the required difficulty
distribution.

| CAPS Ref | Topic | Term | Approved | Draft | AI-Gen | Retired | Status | IRT Calibrated |
|----------|-------|------|----------|-------|--------|---------|--------|----------------|
| **4.M.1.1** | Whole Numbers | 1 | <!-- 4.M.1.1_APPROVED --> | <!-- 4.M.1.1_DRAFT --> | <!-- 4.M.1.1_AI_GEN --> | <!-- 4.M.1.1_RETIRED --> | <!-- 4.M.1.1_STATUS --> | <!-- 4.M.1.1_IRT --> |
| **4.M.1.2** | Common Fractions | 1 | <!-- 4.M.1.2_APPROVED --> | <!-- 4.M.1.2_DRAFT --> | <!-- 4.M.1.2_AI_GEN --> | <!-- 4.M.1.2_RETIRED --> | <!-- 4.M.1.2_STATUS --> | <!-- 4.M.1.2_IRT --> |
| **4.M.1.3** | 2D Shapes | 1 | <!-- 4.M.1.3_APPROVED --> | <!-- 4.M.1.3_DRAFT --> | <!-- 4.M.1.3_AI_GEN --> | <!-- 4.M.1.3_RETIRED --> | <!-- 4.M.1.3_STATUS --> | <!-- 4.M.1.3_IRT --> |

> **Populate this table** by running `python scripts/generate_coverage_matrix.py --output docs/caps/grade4_maths_coverage_matrix.md`
> The script queries the database and replaces all `<!-- ... -->` placeholders with live counts.

---

## Difficulty Distribution Target vs. Actual

The IRT 3-PL model requires ≥ 30 items per topic with spread across difficulty
levels to produce reliable ability (θ) estimates (standard error < 0.4).

### Target (per topic cluster, 40 items)

| Band | b-parameter range | Target count | Purpose |
|------|-------------------|-------------|---------|
| Easy | b < –1.0 | **10** | Struggling / foundational learners |
| Moderate | –1.0 ≤ b < 0.0 | **12** | Below-average learners |
| On-level | 0.0 ≤ b < +1.0 | **12** | Average Grade 4 learners |
| Challenging | b ≥ +1.0 | **6** | Above-average learners |

### 4.M.1.1 — Whole Numbers

| Band | Target | Actual | Gap |
|------|--------|--------|-----|
| Easy | 10 | <!-- 4M11_EASY --> | <!-- 4M11_EASY_GAP --> |
| Moderate | 12 | <!-- 4M11_MOD --> | <!-- 4M11_MOD_GAP --> |
| On-level | 12 | <!-- 4M11_ONL --> | <!-- 4M11_ONL_GAP --> |
| Challenging | 6 | <!-- 4M11_CHAL --> | <!-- 4M11_CHAL_GAP --> |

### 4.M.1.2 — Common Fractions

| Band | Target | Actual | Gap |
|------|--------|--------|-----|
| Easy | 10 | <!-- 4M12_EASY --> | <!-- 4M12_EASY_GAP --> |
| Moderate | 12 | <!-- 4M12_MOD --> | <!-- 4M12_MOD_GAP --> |
| On-level | 12 | <!-- 4M12_ONL --> | <!-- 4M12_ONL_GAP --> |
| Challenging | 6 | <!-- 4M12_CHAL --> | <!-- 4M12_CHAL_GAP --> |

### 4.M.1.3 — 2D Shapes

| Band | Target | Actual | Gap |
|------|--------|--------|-----|
| Easy | 10 | <!-- 4M13_EASY --> | <!-- 4M13_EASY_GAP --> |
| Moderate | 12 | <!-- 4M13_MOD --> | <!-- 4M13_MOD_GAP --> |
| On-level | 12 | <!-- 4M13_ONL --> | <!-- 4M13_ONL_GAP --> |
| Challenging | 6 | <!-- 4M13_CHAL --> | <!-- 4M13_CHAL_GAP --> |

---

## Item Quality Scores

Quality score formula (from roadmap §3, P3-11):

```
quality_score = 0.4 × correctness
              + 0.3 × caps_alignment
              + 0.2 × readability
              + 0.1 × south_african_context
```

A score ≥ 0.7 is required for an item to remain in approved status.

| CAPS Ref | Mean Quality | Min Quality | Items < 0.7 | Reviewed by |
|----------|-------------|-------------|-------------|-------------|
| 4.M.1.1 | <!-- 4M11_QUAL_MEAN --> | <!-- 4M11_QUAL_MIN --> | <!-- 4M11_QUAL_LOW --> | <!-- 4M11_REVIEWER --> |
| 4.M.1.2 | <!-- 4M12_QUAL_MEAN --> | <!-- 4M12_QUAL_MIN --> | <!-- 4M12_QUAL_LOW --> | <!-- 4M12_REVIEWER --> |
| 4.M.1.3 | <!-- 4M13_QUAL_MEAN --> | <!-- 4M13_QUAL_MIN --> | <!-- 4M13_QUAL_LOW --> | <!-- 4M13_REVIEWER --> |

---

## Exposure Heatmap

Tracks how heavily each topic's items have been served in production diagnostic
sessions. Items approaching their `max_exposure` cap (default: 50) should
trigger new item generation.

| CAPS Ref | Total Exposures | Items > 80% Cap | Items at 100% Cap | Replenishment Needed |
|----------|----------------|----------------|-------------------|----------------------|
| 4.M.1.1 | <!-- 4M11_EXP_TOTAL --> | <!-- 4M11_EXP_80 --> | <!-- 4M11_EXP_100 --> | <!-- 4M11_REPLENISH --> |
| 4.M.1.2 | <!-- 4M12_EXP_TOTAL --> | <!-- 4M12_EXP_80 --> | <!-- 4M12_EXP_100 --> | <!-- 4M12_REPLENISH --> |
| 4.M.1.3 | <!-- 4M13_EXP_TOTAL --> | <!-- 4M13_EXP_80 --> | <!-- 4M13_EXP_100 --> | <!-- 4M13_REPLENISH --> |

> **Replenishment threshold**: trigger new item generation when > 20% of a topic's
> items have reached 80% of their exposure cap.

---

## Misconception Tag Coverage

Each topic cluster should cover the key misconceptions documented in the CAPS
curriculum research. The IRT engine uses misconception tags to target lesson
remediation.

### 4.M.1.1 — Whole Numbers — Expected Misconception Tags

| Misconception Tag | Items Tagged | Coverage |
|-------------------|-------------|---------|
| `place_value_confusion` | <!-- WN_PVC --> | <!-- WN_PVC_COV --> |
| `carries_error` | <!-- WN_CE --> | <!-- WN_CE_COV --> |
| `digit_ordering_reversal` | <!-- WN_DOR --> | <!-- WN_DOR_COV --> |
| `rounding_direction_error` | <!-- WN_RDE --> | <!-- WN_RDE_COV --> |
| `number_sentence_inequality` | <!-- WN_NSI --> | <!-- WN_NSI_COV --> |

### 4.M.1.2 — Common Fractions — Expected Misconception Tags

| Misconception Tag | Items Tagged | Coverage |
|-------------------|-------------|---------|
| `fraction_as_two_numbers` | <!-- CF_ATN --> | <!-- CF_ATN_COV --> |
| `denominator_ordering_error` | <!-- CF_DOE --> | <!-- CF_DOE_COV --> |
| `equivalent_fraction_confusion` | <!-- CF_EFC --> | <!-- CF_EFC_COV --> |
| `fraction_of_collection_error` | <!-- CF_FCE --> | <!-- CF_FCE_COV --> |

### 4.M.1.3 — 2D Shapes — Expected Misconception Tags

| Misconception Tag | Items Tagged | Coverage |
|-------------------|-------------|---------|
| `shape_orientation_fixation` | <!-- S2D_SOF --> | <!-- S2D_SOF_COV --> |
| `symmetry_line_count_error` | <!-- S2D_SLC --> | <!-- S2D_SLC_COV --> |
| `triangle_type_confusion` | <!-- S2D_TTC --> | <!-- S2D_TTC_COV --> |
| `tessellation_gap_error` | <!-- S2D_TGE --> | <!-- S2D_TGE_COV --> |

---

## Definition of Done — Checklist

Use this checklist to confirm the item bank is production-ready for launch:

- [ ] `validate_item_bank.py` reports **0 failures** across all 120 approved items (CI P5-04)
- [ ] ≥ 40 approved items for **4.M.1.1** (CI P5-03)
- [ ] ≥ 40 approved items for **4.M.1.2** (CI P5-03)
- [ ] ≥ 40 approved items for **4.M.1.3** (CI P5-03)
- [ ] Every approved item: `reviewer_id` non-null, `reviewed_at` set (P3-05–P3-08)
- [ ] Every approved item: `safety_passed = TRUE` (P2-02)
- [ ] Every approved item: `answer_key` verified by second independent LLM call (P2-07)
- [ ] IRT engine serves real items from DB — no hardcoded arrays remain (P4-01)
- [ ] Exposure enforcement verified: no repeat items within or across 3 sessions (P5-05)
- [ ] Playwright E2E: full learner flow passes (P5-01, P5-02)
- [ ] Item selection p99 < 50ms under 10 concurrent sessions (P5-06)
- [ ] Prometheus `item_bank_coverage_ratio` ≥ 1.0 for all three CAPS refs (P4-11)
- [ ] Grafana panel live: Item Bank Coverage by CAPS Ref (P5-09)
- [ ] `CHANGELOG.md` updated with item bank milestone (P5-11)
- [ ] `TODO.md` §7.2 tasks marked done (P5-11)
- [ ] Release candidate tagged in Git (P5-12)

---

## How to Regenerate This Document

```bash
# From repo root
python scripts/generate_coverage_matrix.py \
    --output docs/caps/grade4_maths_coverage_matrix.md \
    --db-url "$DATABASE_URL"
```

The script queries `diagnostic_items` and `item_exposures` live and replaces
all `<!-- ... -->` placeholder tokens with current values. Commit the result.

---

## Related Documents

- [TODO.md](../../TODO.md) — Outstanding tasks (§7.2 item bank section)
- [RoadMap.md](../../RoadMap.md) — High-level project roadmap
- [docs/architecture/V2_ARCHITECTURE.md](../architecture/V2_ARCHITECTURE.md) — V2 system architecture
- [docs/project_status.md](../project_status.md) — Current project status snapshot
- [CHANGELOG.md](../../CHANGELOG.md) — Version history
- [SECURITY.md](../../SECURITY.md) — POPIA and security policy

---

*EduBoost SA · Grade 4 Mathematics Item Bank · Priority Action #6 · Phase 5 Task P5-07*
