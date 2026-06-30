#!/usr/bin/env bash
set -euo pipefail

# EduBoost — simple idempotent Postgres backup script
# - Uses `pg_dump` to create a consistent dump
# - Stores compressed backups in $BACKUP_DIR
# - Rotates old backups older than $RETENTION_DAYS
# - Intended for cron or systemd-timer execution

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
PG_DUMP_BIN="${PG_DUMP_BIN:-pg_dump}"

# Optional encryption settings
# ENCRYPTION_TOOL: "age" or "gpg" (empty = no encryption)
# AGE_RECIPIENTS: space- or comma-separated age recipients (e.g. "age1... age1...")
# GPG_RECIPIENT: single GPG recipient identifier (email or keyid)
ENCRYPTION_TOOL="${ENCRYPTION_TOOL:-}"
AGE_RECIPIENTS="${AGE_RECIPIENTS:-}"
GPG_RECIPIENT="${GPG_RECIPIENT:-}"
KEEP_PLAINTEXT="${KEEP_PLAINTEXT:-false}"

# Database connection parameters (prefer DATABASE_URL or PG_ env vars)
DATABASE_URL="${DATABASE_URL:-}"

timestamp() { date -u +"%Y%m%dT%H%M%SZ"; }
log() { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [db-backup] $*"; }

mkdir -p "$BACKUP_DIR"

TS=$(timestamp)
FNAME="eduboost-db-${TS}.dump"
OUT_PATH="$BACKUP_DIR/$FNAME"

log "Starting backup -> $OUT_PATH"

if [[ -n "$DATABASE_URL" ]]; then
  # Use pg_dump with a URL
  "$PG_DUMP_BIN" --format=custom --file="$OUT_PATH" "$DATABASE_URL"
else
  # Rely on pg env vars (PGHOST, PGUSER, PGPASSWORD, PGDATABASE)
  "$PG_DUMP_BIN" --format=custom --file="$OUT_PATH"
fi

# Compress the dump to save space
gzip -f "$OUT_PATH"
OUT_GZ="$OUT_PATH.gz"

log "Backup completed: $OUT_GZ"

# Optional encryption step
if [[ -n "$ENCRYPTION_TOOL" ]]; then
  case "$ENCRYPTION_TOOL" in
    age)
      if ! command -v age >/dev/null 2>&1; then
        log "ERROR: age not installed; cannot encrypt"
        exit 2
      fi
      # build recipient args
      IFS=',' read -r -a _recips <<< "${AGE_RECIPIENTS// /,}"
      AGE_ARGS=()
      for r in "${_recips[@]}"; do
        [[ -n "$r" ]] && AGE_ARGS+=( -r "$r" )
      done
      ENC_OUT="$OUT_GZ.age"
      log "Encrypting backup with age -> $ENC_OUT"
      # shellcheck disable=SC2086
      age ${AGE_ARGS[*]} -o "$ENC_OUT" "$OUT_GZ"
      ;;
    gpg)
      if ! command -v gpg >/dev/null 2>&1; then
        log "ERROR: gpg not installed; cannot encrypt"
        exit 2
      fi
      if [[ -z "$GPG_RECIPIENT" ]]; then
        log "ERROR: GPG_RECIPIENT not set"
        exit 2
      fi
      ENC_OUT="$OUT_GZ.gpg"
      log "Encrypting backup with gpg -> $ENC_OUT"
      gpg --batch --yes --output "$ENC_OUT" --encrypt --recipient "$GPG_RECIPIENT" "$OUT_GZ"
      ;;
    *)
      log "Unknown ENCRYPTION_TOOL=$ENCRYPTION_TOOL; skipping encryption"
      ;;
  esac

  if [[ "$KEEP_PLAINTEXT" != "true" ]]; then
    log "Removing plaintext backup $OUT_GZ"
    rm -f "$OUT_GZ"
  else
    log "Keeping plaintext backup due to KEEP_PLAINTEXT=true"
  fi
fi

# Rotation: remove older backups
if command -v find >/dev/null 2>&1; then
  log "Pruning backups older than $RETENTION_DAYS days in $BACKUP_DIR"
  find "$BACKUP_DIR" -type f -name 'eduboost-db-*.dump.gz' -mtime +"$RETENTION_DAYS" -print -delete || true
fi

log "Backup finished successfully"

exit 0
#!/bin/bash
# EduBoost V2 Database Backup Script

# Default values
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
DB_NAME=${POSTGRES_DB:-eduboost_v2}
DB_USER=${POSTGRES_USER:-postgres}
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting backup of ${DB_NAME} to ${BACKUP_FILE}..."

# Export PG_PASSWORD to avoid prompt (ensure it's set in environment)
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Warning: POSTGRES_PASSWORD not set. You may be prompted for a password."
fi

pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F p -v > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup successful: ${BACKUP_FILE}"
    # Keep only last 7 days of backups
    find "$BACKUP_DIR" -name "*.sql" -mtime +7 -exec rm {} \;
else
    echo "Backup failed!"
    exit 1
fi
