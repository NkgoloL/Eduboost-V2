# POPIA Consent Boundary Check

## Purpose

The consent-boundary matrix records the intended consent policy for V2 routes:

- `active_consent_required`
- `rights_exercise_not_active_consent_blocked`
- `authenticated_catalog_boundary`
- `non_learner_scoped`

This check validates that active-consent routes expose an active-consent marker
and that data-subject rights workflows remain explicitly classified.

## Commands

```bash
make popia-consent-boundary-check
pytest -c pytest.ini tests/unit/test_popia_consent_boundary_matrix_check.py -q --no-cov
```
