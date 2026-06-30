#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${BACKUP_FILE:?BACKUP_FILE is required}"
: "${BACKUP_ENCRYPTION_KEY:?BACKUP_ENCRYPTION_KEY is required}"

WORK_DIR="${RESTORE_WORK_DIR:-/tmp/eduboost_restore}"
mkdir -p "$WORK_DIR"
DECRYPTED_FILE="$WORK_DIR/$(basename "${BACKUP_FILE%.gpg}")"

if [ -f "${BACKUP_FILE}.sha256" ]; then
  sha256sum -c "${BACKUP_FILE}.sha256"
fi

gpg --batch --yes --decrypt --passphrase "$BACKUP_ENCRYPTION_KEY" --output "$DECRYPTED_FILE" "$BACKUP_FILE"
pg_restore --clean --if-exists --no-owner --no-privileges --dbname="$DATABASE_URL" "$DECRYPTED_FILE"
rm -f "$DECRYPTED_FILE"

echo "restore_completed=true"
