#!/usr/bin/env bash
set -euo pipefail

echo "Normalizing tracked file modes..."
# Remove exec bit from all tracked files
while IFS= read -r f; do
  git update-index --chmod=-x -- "$f" || true
done < <(git ls-files)

# Re-enable exec bit for files with a shebang
while IFS= read -r f; do
  if [ -f "$f" ] && head -n1 "$f" | grep -q '^#!'; then
    git update-index --chmod=+x -- "$f" || true
  fi
done < <(git ls-files)

echo "File mode normalization complete. Review 'git status' and commit changes." 
