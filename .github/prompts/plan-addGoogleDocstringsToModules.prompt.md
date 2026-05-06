# Plan: Add Google-Style Docstrings to app/modules/

## TL;DR
Add comprehensive Google-style docstrings with Sphinx cross-references to all undocumented functions and classes across `app/modules/`. Currently 29% documented (12/41 items). Will use the pattern found in `/temp/eduboost/app/modules/` as a template, including Attributes blocks, Args/Returns/Raises sections, Examples, and math notation where appropriate.

## Current State
- **Total items**: 41 functions/classes
- **Documented**: 12 (29%)
- **Undocumented**: 30 (71%)
- **Empty modules**: 4 (gamification, parent_portal, rlhf, study_plans)
- **Highest priority**: consent (0%), lessons/service.py (0%), learners (20%)

## Steps

### Phase 1: Document High-Priority Modules (70% of undocumented)
1. **consent/service.py** — `ConsentService` class + 9 methods
   - Add module-level docstring explaining POPIA compliance + audit logging
   - Add class docstring for `ConsentRecord` dataclass with Attributes
   - Add docstrings for all 9 ConsentService methods (grant, revoke, has_valid_consent, etc.)
   - Pattern: Attributes blocks for dataclass, Args/Returns/Raises/Example for methods
   - Template source: `/temp/eduboost/app/modules/consent/service.py`

2. **lessons/service.py** — Module + `LessonService` class + 4 methods
   - Add missing module-level docstring
   - Add class docstring for `LessonService`
   - Document all 4 methods with Args/Returns/Raises/Example
   - Cross-reference related types using `:class:` roles
   - Template source: `/temp/eduboost/app/modules/lessons/llm_gateway.py`

3. **learners/ether_service.py** — Helper methods + `EtherService` improvements
   - Document remaining 4 undocumented methods
   - Add class docstring for `EtherService`
   - Template source: `/temp/eduboost/app/modules/learners/` patterns

### Phase 2: Document Medium-Priority Modules (25% of remaining)
4. **diagnostics/irt_engine.py** — Complete partial coverage
   - Document 5 remaining functions (focus on `estimate_theta_eap()` and statistical helpers)
   - Use mathematical notation (LaTeX blocks) consistent with existing pattern

5. **auth/service.py** — Complete coverage
   - Add module docstring
   - Document 3 undocumented methods
   - Include CAPS/POPIA context where relevant

### Phase 3: Remaining Implementation Files
6. **jobs.py** — Document 4 undocumented helper functions

7. **lessons/** & **diagnostics/** subdirectories — Any remaining undocumented helpers

### Phase 4: (Optional) Stub Empty Modules
8. Placeholder docstrings for empty modules (gamification, parent_portal, rlhf, study_plans)
   - Add module-level docstrings explaining purpose
   - Skip class/function stubs (no implementation yet)

## Docstring Template Pattern
All docstrings follow **Google-style** with these components:
```python
def function(arg1: Type1, arg2: Type2) -> ReturnType:
    """Brief one-line summary.

    Longer description explaining context, behavior, and any domain-specific
    details (CAPS curriculum, IRT scoring, POPIA compliance, etc.).

    Args:
        arg1: Description referencing types via :class:`ClassName`.
        arg2: Description with inline code ``value``.

    Returns:
        ReturnType: Description of the return value and its meaning.

    Raises:
        ValueError: When condition X occurs.
        RuntimeError: When system fails Y.

    Example:
        ::

            result = function(arg1_value, arg2_value)
            assert result == expected
    """
```

**Key conventions from temp/**:
- Cross-reference types: `:class:`, `:attr:`, `:mod:`, `:meth:`
- Math notation: `.. math::` blocks for formulas (IRT 2PL, etc.)
- South African context: Mention grades R–7, CAPS subjects, province names
- Code highlighting: Use `::` syntax for Example blocks
- Backticks: Wrapped enums/values like ``"MATH"``, ``"1.2"``, ``True``

## Relevant Files to Modify
- app/modules/consent/service.py — Add 10 docstrings (1 class + 9 methods)
- app/modules/lessons/service.py — Add 5 docstrings (1 module + 1 class + 3 methods)
- app/modules/learners/ether_service.py — Add 4 docstrings (helper methods)
- app/modules/diagnostics/irt_engine.py — Add 5 docstrings (math/statistical methods)
- app/modules/auth/service.py — Add 3 docstrings
- app/modules/jobs.py — Add 4 docstrings
- Reference templates: temp/eduboost/app/modules/consent/service.py, temp/eduboost/app/modules/diagnostics/irt_engine.py, temp/eduboost/app/modules/lessons/llm_gateway.py

## Verification Steps
1. **Docstring completeness**: Run `python -m pydoc app.modules.<module>` for each module to verify rendering
2. **Sphinx validation**: Build Sphinx docs: `cd docs/api && make clean && make html` (after copying conf.py from /temp/)
3. **No syntax errors**: Run `python -m py_compile` on all modified files
4. **Cross-reference validity**: Check that all `:class:`, `:meth:` references point to actual symbols
5. **Manual inspection**: Review 2-3 docstrings from each module for clarity and completeness
6. **Coverage metric**: Confirm final coverage reaches ≥90% (37+/41 items documented)

## Decisions
- **Scope**: Only Google-style docstrings; exclude Sphinx config setup or MKDocs frontmatter (those live in docs/ once copied)
- **Empty modules**: Optional stubs only; no dummy implementations
- **Math notation**: Include only for algorithmic/scientific content (IRT, statistical tests); skip for business logic
- **South African context**: Preserve CAPS references, grade levels (R–7), subject codes in docstrings
- **Examples**: Minimal but runnable (can import locally, no external API calls)

## Further Considerations
1. **Sphinx autodoc setup** — After docstrings are complete, copy `conf.py`, `source/`, and `mkdocs.yml` from `/temp/` to `docs/` (separate task, not part of this plan)
2. **CI/CD integration** — Add docstring coverage check to test pipeline (e.g., `interrogate` or similar tool)
3. **Dataclass attributes** — Ensure all dataclass fields are documented in Attributes blocks (critical for autodoc)
