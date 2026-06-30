#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${BACKUP_ENCRYPTION_KEY:?BACKUP_ENCRYPTION_KEY is required}"

BACKUP_DIR="${BACKUP_DIR:-backups}"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
PLAIN_FILE="$BACKUP_DIR/eduboost_${TIMESTAMP}.dump"
ENCRYPTED_FILE="${PLAIN_FILE}.gpg"
CHECKSUM_FILE="${ENCRYPTED_FILE}.sha256"

mkdir -p "$BACKUP_DIR"
pg_dump "$DATABASE_URL" --format=custom --no-owner --no-privileges --file="$PLAIN_FILE"
gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase "$BACKUP_ENCRYPTION_KEY" --output "$ENCRYPTED_FILE" "$PLAIN_FILE"
sha256sum "$ENCRYPTED_FILE" > "$CHECKSUM_FILE"
rm -f "$PLAIN_FILE"

echo "backup_file=$ENCRYPTED_FILE"
echo "checksum_file=$CHECKSUM_FILE"
