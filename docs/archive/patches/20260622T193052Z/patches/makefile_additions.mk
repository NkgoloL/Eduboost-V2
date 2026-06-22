# =============================================================================
# Makefile additions – paste these into the existing Makefile
# (or apply via: patch -p0 < docs/patches/makefile_additions.patch)
#
# These additions address Recommendations 4 and 6 from the 2026-05-12
# technical state report.
# =============================================================================

# Add to the existing .PHONY line (or replace the line entirely):
# .PHONY: ... deduplicate-check refresh-current-state refresh-current-state-report sync-check-origin

# ---------------------------------------------------------------------------
# Recommendation 4: Makefile hygiene – detect duplicate targets
# ---------------------------------------------------------------------------

deduplicate-check:
	$(PYTHON) scripts/deduplicate_makefile_targets.py

deduplicate-fix:
	$(PYTHON) scripts/deduplicate_makefile_targets.py --fix

deduplicate-fix-dry-run:
	$(PYTHON) scripts/deduplicate_makefile_targets.py --fix --dry-run


# ---------------------------------------------------------------------------
# Recommendation 5: Sync check – verify local branch is up to date
# ---------------------------------------------------------------------------

sync-check-origin:
	./scripts/sync_check_origin.sh

sync-and-verify:
	./scripts/sync_check_origin.sh --sync


# ---------------------------------------------------------------------------
# Recommendation 6: Refresh current state documentation
# ---------------------------------------------------------------------------

refresh-current-state:
	$(PYTHON) scripts/refresh_current_state_doc.py

refresh-current-state-report:
	$(PYTHON) scripts/refresh_current_state_doc.py --dated-report

refresh-current-state-dry-run:
	$(PYTHON) scripts/refresh_current_state_doc.py --dry-run --dated-report


# ---------------------------------------------------------------------------
# Omnibus: run all six recommendation fixes in sequence
# ---------------------------------------------------------------------------
# Intended for use after applying all code changes from the 2026-05-12
# technical report.  Run this once to verify everything is clean.

rec-all-checks: deduplicate-check \
                frontend-e2e-opt-in-workflow-check \
                pr002r-check \
                runtime-check \
                openapi-check \
                route-inventory-check
	$(PYTHON) -m pytest tests/unit -m "not llm and not e2e" --tb=short --no-cov -q
	$(PYTHON) scripts/refresh_current_state_doc.py --dated-report
	@echo ""
	@echo "All recommendation checks passed."
	@echo "Review docs/current_state.md and commit."
