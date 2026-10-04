#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-erp-sst}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
BACKUP_WRITER_MODE="${BACKUP_WRITER_MODE:-stop-backend}"
OFFSITE_COMMAND="${OFFSITE_COMMAND:-}"

if [[ -n "${COMPOSE_FILE:-}" ]]; then
  COMPOSE_PATH="$COMPOSE_FILE"
else
  ACTIVE_COMPOSE_FILE="$(docker ps --filter "label=com.docker.compose.project=$COMPOSE_PROJECT_NAME" --format '{{.Label "com.docker.compose.project.config_files"}}' 2>/dev/null | head -n 1 || true)"
  ACTIVE_COMPOSE_FILE="${ACTIVE_COMPOSE_FILE%%,*}"
  COMPOSE_PATH="${ACTIVE_COMPOSE_FILE:-$PROJECT_DIR/docker-compose.prod.yml}"
fi

[[ -f "$ENV_FILE" ]] || { echo "No existe el archivo de entorno: $ENV_FILE" >&2; exit 1; }
[[ "$BACKUP_WRITER_MODE" == "stop-backend" ]] || { echo "BACKUP_WRITER_MODE no soportado: $BACKUP_WRITER_MODE" >&2; exit 1; }
command -v docker >/dev/null
command -v flock >/dev/null
command -v sha256sum >/dev/null

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
umask 077
exec 9>"$BACKUP_DIR/.backup.lock"
flock -n 9 || { echo "Ya hay un respaldo ERP SST en ejecución." >&2; exit 1; }

COMPOSE=(docker compose -p "$COMPOSE_PROJECT_NAME" -f "$COMPOSE_PATH" --env-file "$ENV_FILE")
DATE="$(date +%Y%m%d_%H%M%S)"
PREFIX="$BACKUP_DIR/erp_sst_backup_$DATE"
DATABASE_FILE="${PREFIX}_database.sql.gz"
UPLOADS_FILE="${PREFIX}_uploads.tar.gz"
CHECKSUM_FILE="${PREFIX}.sha256"
DATABASE_TEMP="${DATABASE_FILE}.tmp"
UPLOADS_TEMP="${UPLOADS_FILE}.tmp"
BACKEND_WAS_RUNNING="$("${COMPOSE[@]}" ps --status running --services | grep -cx backend || true)"
BACKEND_STOPPED=0

cleanup() {
  rm -f "$DATABASE_TEMP" "$UPLOADS_TEMP"
  if (( BACKEND_STOPPED == 1 && BACKEND_WAS_RUNNING > 0 )); then
    "${COMPOSE[@]}" up -d --wait backend >/dev/null || echo "No se pudo reanudar backend; requiere intervención." >&2
  fi
}
trap cleanup EXIT

cd "$PROJECT_DIR"
if (( BACKEND_WAS_RUNNING > 0 )); then
  "${COMPOSE[@]}" stop backend >/dev/null
  BACKEND_STOPPED=1
fi

"${COMPOSE[@]}" exec -T db sh -c 'pg_dump --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "$DATABASE_TEMP"
"${COMPOSE[@]}" run --rm -T --no-deps backend tar -C /app/app/uploads -czf - . > "$UPLOADS_TEMP"
gzip -t "$DATABASE_TEMP"
tar -tzf "$UPLOADS_TEMP" >/dev/null
mv "$DATABASE_TEMP" "$DATABASE_FILE"
mv "$UPLOADS_TEMP" "$UPLOADS_FILE"
(
  cd "$BACKUP_DIR"
  sha256sum "$(basename "$DATABASE_FILE")" "$(basename "$UPLOADS_FILE")"
) > "$CHECKSUM_FILE"

if (( BACKEND_STOPPED == 1 && BACKEND_WAS_RUNNING > 0 )); then
  "${COMPOSE[@]}" up -d --wait backend >/dev/null
  BACKEND_STOPPED=0
fi

if [[ -n "$OFFSITE_COMMAND" ]]; then
  BACKUP_DATABASE_FILE="$DATABASE_FILE" BACKUP_UPLOADS_FILE="$UPLOADS_FILE" BACKUP_CHECKSUM_FILE="$CHECKSUM_FILE" BACKUP_PREFIX="$PREFIX" /bin/sh -c "$OFFSITE_COMMAND"
fi

if [[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]] && (( BACKUP_RETENTION_DAYS > 0 )); then
  find "$BACKUP_DIR" -maxdepth 1 -type f \( -name 'erp_sst_backup_*_database.sql.gz' -o -name 'erp_sst_backup_*_uploads.tar.gz' -o -name 'erp_sst_backup_*.sha256' \) -mtime "+$BACKUP_RETENTION_DAYS" -delete
fi

trap - EXIT
echo "Backup consistente creado: $PREFIX"
