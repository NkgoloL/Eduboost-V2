#!/bin/bash
# EduBoost V2 - PostgreSQL Backup Script
# Automated, Encrypted, and Retained.

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DB_NAME="${POSTGRES_DB:-eduboost_v2}"
DB_USER="${POSTGRES_USER:-eduboost_admin}"
DB_HOST="${POSTGRES_HOST:-localhost}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting backup for $DB_NAME at $TIMESTAMP..."

# Perform backup
# Note: Assumes PGPASSWORD is set in environment or .pgpass is configured
pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

# Encrypt the backup
if [ -z "$BACKUP_ENCRYPTION_KEY" ]; then
    echo "WARNING: BACKUP_ENCRYPTION_KEY not set. Backup will NOT be encrypted."
else
    echo "Encrypting backup..."
    gpg --batch --yes --passphrase "$BACKUP_ENCRYPTION_KEY" -c "$BACKUP_FILE"
    rm "$BACKUP_FILE" # Remove the unencrypted file
    BACKUP_FILE="$ENCRYPTED_FILE"
fi

echo "Backup completed: $BACKUP_FILE"

# Retention policy: Remove backups older than X days
echo "Applying retention policy (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql*" -mtime +"$RETENTION_DAYS" -exec rm {} \;

echo "Backup process finished successfully."
