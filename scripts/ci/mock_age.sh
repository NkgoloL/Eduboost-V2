#!/usr/bin/env bash
set -euo pipefail

# Minimal mock of `age` for CI: accepts recipient args (-r), -o output, and input file.
OUT_FILE=""
IN_FILE=""
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -r)
      shift; ARGS+=("-r" "$1"); shift;;
    -o)
      shift; OUT_FILE="$1"; shift;;
    -o=*)
      OUT_FILE="${1#-o=}"; shift;;
    -*)
      shift;;
    *)
      IN_FILE="$1"; shift;;
  esac
done

if [[ -z "$OUT_FILE" ]]; then
  echo "mock_age: missing -o <out>" >&2
  exit 2
fi

mkdir -p "$(dirname "$OUT_FILE")"
echo "age-mock: encrypted $(basename "$IN_FILE") to $(basename "$OUT_FILE")" >"$OUT_FILE"
exit 0
