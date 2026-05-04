# Create a bundle folder
mkdir -p .copilot_bundle

# 1) Save a directory tree (useful for navigation)
# If "tree" isn't installed: 
sudo apt-get update && sudo apt-get install -y tree
tree -a -I ".git|node_modules|venv|.venv|dist|build|target|bin|obj|__pycache__|.mypy_cache|.pytest_cache" \
  > .copilot_bundle/00_TREE.txt

# 2) Save basic repo metadata (optional but helpful)
{
  echo "# Repo Metadata"
  echo
  echo "## Git status"
  git status --porcelain=v1 2>/dev/null || true
  echo
  echo "## Recent commits"
  git log -n 30 --oneline 2>/dev/null || true
  echo
  echo "## Branch"
  git branch --show-current 2>/dev/null || true
} > .copilot_bundle/01_META.md

# 3) Bundle tracked files into a single markdown document
# Excludes common large/irrelevant paths and secret files.
OUT=".copilot_bundle/02_CODE_BUNDLE.md"
: > "$OUT"

echo "# Code Bundle" >> "$OUT"
echo "" >> "$OUT"
echo "_Generated: $(date -Iseconds)_" >> "$OUT"
echo "" >> "$OUT"

# If this is a git repo, use tracked files (best signal/noise).
# If not a git repo, we'll fall back later.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git ls-files > .copilot_bundle/files.txt
else
  # Fall back: include files in working dir (excluding heavy folders)
  find . -type f \
    ! -path "./.git/*" \
    ! -path "./node_modules/*" \
    ! -path "./venv/*" ! -path "./.venv/*" \
    ! -path "./dist/*" ! -path "./build/*" ! -path "./target/*" \
    ! -path "./bin/*" ! -path "./obj/*" \
    ! -path "./__pycache__/*" \
    > .copilot_bundle/files.txt
fi

# Exclude obvious secret/config artifacts from the bundle
grep -vE '(^|/)(\.env(\..*)?|secrets?\.|id_rsa|id_ed25519|\.pem|\.pfx|\.key|\.crt|credentials|token|\.kube/|\.aws/)' \
  .copilot_bundle/files.txt \
  > .copilot_bundle/files_filtered.txt

# Append each file to markdown with fences
while IFS= read -r f; do
  # Skip very large files (over ~550KB) to keep the bundle manageable
  if [ -f "$f" ] && [ "$(wc -c < "$f")" -le 550000 ]; then
    echo "" >> "$OUT"
    echo "## FILE: $f" >> "$OUT"
    echo "\`\`\`" >> "$OUT"
    cat "$f" >> "$OUT"
    echo "" >> "$OUT"
    echo "\`\`\`" >> "$OUT"
  fi
done < .copilot_bundle/files_filtered.txt

echo "Bundle written to $OUT"
