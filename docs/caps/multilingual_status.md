# Multilingual Lesson Generation Status

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Status**: Verified for deterministic mock generation; human quality review still needed
**Languages Supported**: 4

---

## Supported Languages

| Language | Code | Status | Notes |
|----------|------|--------|-------|
| English | `en` | ✅ Mock generation verified | Primary language |
| isiZulu | `zu` | ✅ Mock generation verified | Language code is preserved through deterministic lesson generation |
| Afrikaans | `af` | ⚠️ Mock generation verified; quality partial | Needs native-speaker review |
| isiXhosa | `xh` | ⚠️ Mock generation verified; quality partial | Vocabulary and native-speaker review still needed |

---

## Verification Results

### 2026-06-14 Local CI Smoke

```text
python3 -m pytest --no-cov -q tests/unit/test_content_generation_executor.py tests/unit/test_content_generation_provider_factory.py tests/unit/test_lesson_service_v2.py
# 20 passed
```

The deterministic content generation provider generated one lesson for each supported language code: `en`, `zu`, `af`, and `xh`. The smoke test verifies language routing, source chunk preservation, and safety status. It does not claim native-speaker output quality.

### English (en) ✅

- **Test Date**: 2026-06-14
- **Mock Output**: Generated through deterministic provider
- **Output Quality**: Requires full LLM/human review outside deterministic smoke
- **Fallback**: Works correctly when LLM is unavailable

### isiZulu (zu) ✅

- **Test Date**: 2026-06-14
- **Mock Output**: Generated through deterministic provider
- **Features**:
  - Mathematical terms in isiZulu (official vocabulary)
  - Scaffolding with English translations
  - Bilingual explanations
- **Output Quality**: Requires full LLM/human review outside deterministic smoke

### Afrikaans (af) ⚠️

- **Test Date**: 2026-06-14
- **Mock Output**: Generated through deterministic provider
- **Output Quality**: Still needs native speaker review
- **Known Gaps**:
  - Limited Afrikaans mathematical vocabulary
  - Some idioms may not translate well

### isiXhosa (xh) ⚠️

- **Test Date**: 2026-06-14
- **Mock Output**: Generated through deterministic provider
- **Output Quality**: Still needs vocabulary expansion and native speaker review
- **Known Gaps**:
  - Limited curriculum-aligned vocabulary
  - Less prompt engineering attention

---

## Language Detection & Routing

The system detects learner language preference via:

1. **Learner Profile**: `learner.language` field (enum)
2. **Request Override**: `language` field in lesson request
3. **Fallback**: Default to English if not specified

### Request Flow

```python
# In app/api_v2_routers/lessons.py
language = body.language or learner.language or "en"
prompt_template = load_prompt(f"lesson_{language}.md", default="lesson_en.md")
```

---

## Generation Path

The current local smoke uses `app/services/content_generation/providers/deterministic.py` and `app/services/content_generation/prompt_payloads.py`. Production LLM prompt-template quality remains a separate review item.

---

## Known Issues

1. **Incomplete Vocabulary**: Afrikaans and isiXhosa lack full mathematical vocabularies
2. **Quality Variance**: Non-English outputs require native speaker review
3. **Fallback Handling**: When LLM output is low-quality, no graceful retry mechanism

---

## Recommendations

1. **Short-term**: Add native speaker review for Afrikaans outputs
2. **Medium-term**: Expand isiXhosa vocabulary with CAPS terminology
3. **Long-term**: Fine-tune models per language for better quality

---

## CI Smoke Test

The CI-compatible smoke is `test_deterministic_lesson_generation_preserves_supported_languages` in `tests/unit/test_content_generation_executor.py`.

---

## References

- Deterministic provider: `app/services/content_generation/providers/deterministic.py`
- Prompt payloads: `app/services/content_generation/prompt_payloads.py`
- Lesson context language handling: `tests/unit/test_lesson_context_builder.py`
