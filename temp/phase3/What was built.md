## What was built

**Core services (`app/modules/diagnostics/`)**

| File | Roadmap tasks | What it does |
|---|---|---|
| `item_validator.py` | P2-02, P2-09 | All 8 validation rules: CAPS ref check, answer-key match, FK readability ≤ grade 6.5, PII/harmful/brand scan, IRT bounds, ≥4 MCQ options, explanation length, distractor rationale completeness |
| `item_generator.py` | P2-03, P2-06, P2-07 | Two-call LLM pipeline — call 1 generates, call 2 independently re-solves and verifies; raises `AnswerKeyMismatchError` on disagreement |
| `quality_scorer.py` | P3-11 | Composite score = 0.40×correctness + 0.30×CAPS alignment + 0.20×readability + 0.10×SA context |
| `prompts/item_generation_v1.jinja2` | P2-06 | Full CAPS-aware generation prompt with SA context, difficulty band IRT target, and strict JSON output spec |
| `prompts/answer_key_verification_v1.jinja2` | P2-07 | Blind verification prompt — re-solves without seeing the original answer |

**Scripts (`scripts/`)**

| Script | Roadmap tasks | Usage |
|---|---|---|
| `generate_items.py` | P3-01, P3-02, P3-03, P2-04 | `--caps-ref 4.M.1.1 --n-items 60 --difficulty-band mixed` |
| `validate_item_bank.py` | P2-05, P3-04 | Offline CI runner; exits 1 if any item fails |
| `seed_item_bank.py` | P1-09, P3-12 | Validates → upserts approved items into PostgreSQL |
| `assign_irt_params.py` | P3-09, P3-10 | Calibrates b/a/c params + runs quality scorer in batch |

**Tests (`tests/`)**

| Test file | Roadmap tasks | Coverage |
|---|---|---|
| `test_item_validator.py` | P2-09 | Every rule tested independently + boundary conditions |
| `test_item_generator.py` | P2-03, P2-07 | Two-call pattern, mismatch detection, error handling, JSON fence stripping |
| `test_item_bank_pipeline.py` | P3-14 | Seed→query, exposure tracking, IRT selection, coverage summary, quality scoring |

**Data files**

- `grade4_maths_item_bank.json` — 15 hand-authored seed items (4.M.1.1 ×5, 4.M.1.2 ×5, 4.M.1.3 ×5); 14 approved, 1 flagged with a noted answer-key discrepancy for curriculum review
- `grade4_maths_coverage_matrix.md` — Living coverage dashboard (P5-07)

**One action needed before running `generate_items.py`:** plug your existing `LLMGateway` class path into the import in `item_generator.py` — the generator is already wired for dependency injection so tests run without it.