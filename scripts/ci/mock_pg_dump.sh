#!/usr/bin/env bash
set -euo pipefail

# Mock pg_dump used for CI dry-runs. Accepts --format and --file and writes
# a harmless placeholder file so the backup script can run without a real DB.

OUT_FILE=""
FORMAT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      shift
      OUT_FILE="$1"
      shift
      ;;
    --file=*)
      OUT_FILE="${1#--file=}"
      shift
      ;;
    --format)
      shift
      FORMAT="$1"
      shift
      ;;
    --format=*)
      FORMAT="${1#--format=}"
      shift
      ;;
    *)
      # ignore other args (like a DATABASE_URL)
      shift
      ;;
  esac
done

if [[ -z "$OUT_FILE" ]]; then
  echo "mock_pg_dump: --file <path> required" >&2
  exit 2
fi

mkdir -p "$(dirname "$OUT_FILE")"
{
  echo "-- mock pg dump --"
  echo "generated_at: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  echo "format: ${FORMAT:-plain}"
  echo "note: this is a CI mock, not a real dump"
  echo "CREATE TABLE mock_example(id integer primary key);"
} >"$OUT_FILE"

exit 0
