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
