#!/usr/bin/env bash
# =============================================================================
# scripts/sync_check_origin.sh
# =============================================================================
# Recommendation 5: Re-run the full local verification story on a checkout
# synced to origin/master.
#
# This script:
#   1. Fetches origin.
#   2. Reports how far behind (and ahead) the local branch is.
#   3. Optionally fast-forward merges when it is safe to do so.
#   4. Runs the full local verification story (the same commands listed in
#      the technical report) once the branch is in sync.
#   5. Exits non-zero if the branch cannot be auto-synced (e.g. diverged).
#
# Usage:
#   ./scripts/sync_check_origin.sh             # report only
#   ./scripts/sync_check_origin.sh --sync      # fetch + fast-forward + verify
#   ./scripts/sync_check_origin.sh --sync --dry-run  # show what would run
#
# Environment variables:
#   EXPECTED_BRANCH   Branch to compare against (default: master)
#   REMOTE            Remote name (default: origin)
# =============================================================================

set -euo pipefail

EXPECTED_BRANCH="${EXPECTED_BRANCH:-master}"
REMOTE="${REMOTE:-origin}"
SYNC=false
DRY_RUN=false

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --sync)     SYNC=true ;;
    --dry-run)  DRY_RUN=true ;;
    --help|-h)
      grep '^#' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown argument: $arg" >&2
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
run() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] $*"
  else
    "$@"
  fi
}

header() {
  echo ""
  echo "============================================================"
  echo "  $*"
  echo "============================================================"
}

# ---------------------------------------------------------------------------
# 1. Fetch origin
# ---------------------------------------------------------------------------
header "Fetching $REMOTE"
run git fetch "$REMOTE" "$EXPECTED_BRANCH" --prune

# ---------------------------------------------------------------------------
# 2. Check divergence
# ---------------------------------------------------------------------------
LOCAL_REF=$(git rev-parse HEAD)
REMOTE_REF=$(git rev-parse "$REMOTE/$EXPECTED_BRANCH")
AHEAD=$(git rev-list --count "$REMOTE/$EXPECTED_BRANCH"..HEAD)
BEHIND=$(git rev-list --count "HEAD..$REMOTE/$EXPECTED_BRANCH")

echo ""
echo "Local  HEAD : $LOCAL_REF"
echo "Remote HEAD : $REMOTE_REF ($REMOTE/$EXPECTED_BRANCH)"
echo "Ahead  : $AHEAD commit(s)"
echo "Behind : $BEHIND commit(s)"

if [[ "$AHEAD" -eq 0 && "$BEHIND" -eq 0 ]]; then
  echo ""
  echo "[OK] Local branch is in sync with $REMOTE/$EXPECTED_BRANCH."
elif [[ "$AHEAD" -gt 0 && "$BEHIND" -eq 0 ]]; then
  echo ""
  echo "[INFO] Local branch is $AHEAD commit(s) ahead of remote – nothing to pull."
elif [[ "$AHEAD" -gt 0 && "$BEHIND" -gt 0 ]]; then
  echo ""
  echo "[WARN] Branches have diverged ($AHEAD ahead, $BEHIND behind)."
  echo "       A fast-forward merge is not possible."
  echo "       Resolve manually:  git rebase $REMOTE/$EXPECTED_BRANCH"
  if [[ "$SYNC" == "true" ]]; then
    exit 1
  fi
else
  # $AHEAD -eq 0 and $BEHIND -gt 0: clean fast-forward candidate
  echo ""
  echo "[INFO] Local branch is $BEHIND commit(s) behind remote."
  if [[ "$SYNC" == "true" ]]; then
    header "Fast-forwarding to $REMOTE/$EXPECTED_BRANCH"
    run git merge --ff-only "$REMOTE/$EXPECTED_BRANCH"
    echo "[OK] Fast-forward complete."
  else
    echo "       Run with --sync to fast-forward automatically."
    exit 1
  fi
fi

# ---------------------------------------------------------------------------
# 3. Bail here if only a report was requested
# ---------------------------------------------------------------------------
if [[ "$SYNC" == "false" ]]; then
  echo ""
  echo "Re-run with --sync to fast-forward and then execute the verification story."
  exit 0
fi

# ---------------------------------------------------------------------------
# 4. Full local verification story (mirrors the technical report)
# ---------------------------------------------------------------------------
header "Running full local verification story"

echo ""
echo "--- Runtime and contract checks ---"
run make runtime-check
run make openapi-check
run make route-inventory-check

echo ""
echo "--- Backend unit gate ---"
run python3 -m pytest tests/unit \
  -m "not llm and not e2e" \
  --tb=short \
  --no-cov \
  -q

echo ""
echo "--- Frontend quality loop ---"
(
  run cd app/frontend
  run npm run lint
  run npm run type-check
  run npm test -- --run
)

echo ""
echo "--- Evidence and contract checks ---"
run make pr002r-check
run make frontend-e2e-opt-in-workflow-check
run make frontend-e2e-runtime-command-check

echo ""
echo "--- Makefile hygiene ---"
run python3 scripts/deduplicate_makefile_targets.py

# ---------------------------------------------------------------------------
# 5. Summary
# ---------------------------------------------------------------------------
header "Verification story complete"
echo ""
echo "All checks passed on a checkout synced to $REMOTE/$EXPECTED_BRANCH."
echo "Proceed to refresh docs/current_state.md (Recommendation 6)."
