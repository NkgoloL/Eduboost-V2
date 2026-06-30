#!/usr/bin/env bash
set -euo pipefail

# Minimal mock of `gpg` for CI. Accepts --output <file> and an input file.
OUT_FILE=""
IN_FILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      shift; OUT_FILE="$1"; shift;;
    --output=*)
      OUT_FILE="${1#--output=}"; shift;;
    --*)
      # consume other flags like --batch/--yes/--encrypt/--recipient
      shift;;
    *)
      IN_FILE="$1"; shift;;
  esac
done

if [[ -z "$OUT_FILE" ]]; then
  echo "mock_gpg: missing --output <file>" >&2
  exit 2
fi

mkdir -p "$(dirname "$OUT_FILE")"
echo "gpg-mock: encrypted $(basename "$IN_FILE") to $(basename "$OUT_FILE")" >"$OUT_FILE"
exit 0
