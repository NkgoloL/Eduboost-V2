#!/bin/bash
# EduBoost V2 Database Restore Script

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE=$1
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
DB_NAME=${POSTGRES_DB:-eduboost_v2}
DB_USER=${POSTGRES_USER:-postgres}

echo "Starting restore of ${DB_NAME} from ${BACKUP_FILE}..."

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Warning: POSTGRES_PASSWORD not set. You may be prompted for a password."
fi

# Drop and recreate database (CAUTION: destructive)
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "DROP DATABASE IF EXISTS ${DB_NAME};"
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE ${DB_NAME};"

psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Restore successful!"
else
    echo "Restore failed!"
    exit 1
fi
