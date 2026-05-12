# Makefile Duplicate Target Patch
# =================================
# Recommendation 4: Remove duplicate Makefile target definitions.
#
# Apply with:
#   patch -p0 < docs/patches/makefile_deduplicate.patch
#
# Or run the automated script:
#   python3 scripts/deduplicate_makefile_targets.py --fix
#
# Five targets are defined twice.  In each case the SECOND definition is the
# one that Make actually uses (later definitions win), so the FIRST occurrence
# of each is removed.  Verify which copy is canonical before applying.
#
# Duplicates and their line positions (as of the 2026-05-12 assessment):
#
#   observability-ops-check                        lines ~276 and ~490
#   post-deploy-staging-smoke-checklist-check      lines ~280 and ~577
#   release-candidate-tag-manifest-check           lines ~290 and ~598
#   release-state-snapshot-check                   lines ~293 and ~606
#   staging-smoke-evidence-manifest-check          lines ~286 and ~602
#
# The patch below removes the FIRST (earlier) occurrence of each duplicate.
# -------------------------------------------------------------------------
#
# NOTE: Because the Makefile is 681 lines and context lines shift with each
# removal, apply hunks individually or use the Python script which handles
# shifting automatically.
#
# The authoritative fix mechanism is the Python script.  This file serves
# as human-readable documentation of what the script will do.
#
# -------------------------------------------------------------------------
# Summary of changes
# -------------------------------------------------------------------------
#
# REMOVE (first occurrence – overridden by later definition):
#
#   observability-ops-check:
#   \t$(PYTHON) scripts/check_observability_ops_evidence.py
#   [blank line]
#
#   post-deploy-staging-smoke-checklist-check:
#   \t$(PYTHON) scripts/check_post_deploy_staging_smoke_checklist.py
#   [blank line]
#
#   release-candidate-tag-manifest-check:
#   \t$(PYTHON) scripts/check_release_candidate_tag_manifest.py
#   [blank line]
#
#   release-state-snapshot-check:
#   \t$(PYTHON) scripts/check_release_state_snapshot.py
#   [blank line]
#
#   staging-smoke-evidence-manifest-check:
#   \t$(PYTHON) scripts/check_staging_smoke_evidence_manifest.py
#   [blank line]
#
# KEEP (second occurrence – this is what Make currently executes):
#
#   observability-ops-check:           line ~490  ← KEEP
#   post-deploy-staging-smoke-checklist-check: line ~577  ← KEEP
#   release-candidate-tag-manifest-check:      line ~598  ← KEEP
#   release-state-snapshot-check:              line ~606  ← KEEP
#   staging-smoke-evidence-manifest-check:     line ~602  ← KEEP
#
# ALSO UPDATE: The .PHONY line at the top of the Makefile lists these
# targets.  No change needed there since .PHONY entries are not affected
# by duplicate target definitions (they are just annotations).
# However, the .PHONY list itself should be checked for any duplicate
# entries and sorted for maintainability:
#
#   .PHONY: ... observability-ops-check ... (appears once – no change needed)
#
# -------------------------------------------------------------------------
# Verification after applying
# -------------------------------------------------------------------------
#
#   make -n observability-ops-check 2>&1 | grep -v "^make\[" | head -5
#   # Should print exactly ONE recipe line, no "overriding" warnings.
#
#   python3 scripts/deduplicate_makefile_targets.py
#   # Should print [PASS] No duplicate Makefile targets found.
#
# -------------------------------------------------------------------------
# CI gate (add to Makefile after deduplication):
# -------------------------------------------------------------------------
#
# deduplicate-check:
# \t$(PYTHON) scripts/deduplicate_makefile_targets.py
#
# Add to .PHONY and to the relevant CI workflow step.
