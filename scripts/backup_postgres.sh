#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-erp-sst}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

if [[ -n "${COMPOSE_FILE:-}" ]]; then
  COMPOSE_PATH="$COMPOSE_FILE"
else
  ACTIVE_COMPOSE_FILE="$(
    docker ps \
      --filter "label=com.docker.compose.project=$COMPOSE_PROJECT_NAME" \
      --format '{{.Label "com.docker.compose.project.config_files"}}' \
      | head -n 1
  )"
  ACTIVE_COMPOSE_FILE="${ACTIVE_COMPOSE_FILE%%,*}"
  if [[ -n "$ACTIVE_COMPOSE_FILE" && -f "$ACTIVE_COMPOSE_FILE" ]]; then
    COMPOSE_PATH="$ACTIVE_COMPOSE_FILE"
  else
    COMPOSE_PATH="$PROJECT_DIR/docker-compose.prod.yml"
  fi
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "No existe el archivo de entorno: $ENV_FILE" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
umask 077

exec 9>"$BACKUP_DIR/.backup.lock"
if ! flock -n 9; then
  echo "Ya hay un respaldo ERP SST en ejecución." >&2
  exit 1
fi

DATE="$(date +%Y%m%d_%H%M%S)"
PREFIX="$BACKUP_DIR/erp_sst_backup_$DATE"
DATABASE_FILE="${PREFIX}_database.sql.gz"
UPLOADS_FILE="${PREFIX}_uploads.tar.gz"
CHECKSUM_FILE="${PREFIX}.sha256"
DATABASE_TEMP="${DATABASE_FILE}.tmp"
UPLOADS_TEMP="${UPLOADS_FILE}.tmp"

cleanup_partial_backup() {
  rm -f "$DATABASE_TEMP" "$UPLOADS_TEMP"
}
trap cleanup_partial_backup EXIT

COMPOSE=(
  docker compose
  -p "$COMPOSE_PROJECT_NAME"
  -f "$COMPOSE_PATH"
  --env-file "$ENV_FILE"
)

cd "$PROJECT_DIR"

"${COMPOSE[@]}" exec -T db sh -c \
  'pg_dump --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip > "$DATABASE_TEMP"

"${COMPOSE[@]}" exec -T backend \
  tar -C /app/app/uploads -czf - . > "$UPLOADS_TEMP"

gzip -t "$DATABASE_TEMP"
tar -tzf "$UPLOADS_TEMP" > /dev/null
mv "$DATABASE_TEMP" "$DATABASE_FILE"
mv "$UPLOADS_TEMP" "$UPLOADS_FILE"
(
  cd "$BACKUP_DIR"
  sha256sum "$(basename "$DATABASE_FILE")" "$(basename "$UPLOADS_FILE")"
) > "$CHECKSUM_FILE"
trap - EXIT

if [[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]] && (( BACKUP_RETENTION_DAYS > 0 )); then
  find "$BACKUP_DIR" -maxdepth 1 -type f \
    \( -name 'erp_sst_backup_*_database.sql.gz' \
       -o -name 'erp_sst_backup_*_uploads.tar.gz' \
       -o -name 'erp_sst_backup_*.sha256' \) \
    -mtime "+$BACKUP_RETENTION_DAYS" -delete
fi

echo "Backup de base creado: $DATABASE_FILE"
echo "Backup de uploads creado: $UPLOADS_FILE"
echo "Checksums creados: $CHECKSUM_FILE"
