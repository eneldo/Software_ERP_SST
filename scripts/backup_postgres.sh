#!/usr/bin/env sh
set -eu

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE="$(date +%Y%m%d_%H%M%S)"
FILE="$BACKUP_DIR/erp_sst_backup_$DATE.sql.gz"

mkdir -p "$BACKUP_DIR"

docker exec erp_sst_db pg_dump -U "${POSTGRES_USER:-erp_sst_user}" "${POSTGRES_DB:-erp_sst}" | gzip > "$FILE"

echo "Backup creado: $FILE"
