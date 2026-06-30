# Diagnostics And Assessment

Diagnostics cover learner assessment sessions, item selection, scoring, mastery signals, and launch item-bank quality.

## Runtime map

- HTTP routes: `app/api_v2_routers/diagnostics.py` and `app/api_v2_routers/assessments.py`
- Diagnostic services: `app/modules/diagnostics/`
- Diagnostic repositories: `app/repositories/diagnostic_session_repository.py` and item-bank repositories
- Launch content data: `data/generated/items/` and `data/caps/`

## Current implementation notes

- The Grade 4 Mathematics launch slice is the strongest verified content path.
- Item-bank, IRT, and assessment contracts should be verified with runtime tests, not only static evidence checks.
- Source provenance and CAPS alignment remain mandatory for promoted learner-visible content.

## Verification

- `make diagnostics-assessment-check`
- `make lesson-bank-check`
- `make caps-alignment-contract-check`
- Relevant unit tests under `tests/unit/test_diagnostic_*`, `test_irt_*`, and `test_launch_content_factory.py`

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
