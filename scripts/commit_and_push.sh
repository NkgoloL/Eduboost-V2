#!/usr/bin/env bash
set -euo pipefail
msg="${1:-Automated commit: assistant changes}"
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
cd "$repo_root"
branch="$(git rev-parse --abbrev-ref HEAD)"
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi
git commit -m "$msg"
git push --set-upstream origin "$branch" 2>/dev/null || git push origin "$branch"
