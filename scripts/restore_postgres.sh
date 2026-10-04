#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-erp-sst}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"
DATABASE_FILE="${1:-}"
UPLOADS_FILE="${2:-}"
CHECKSUM_FILE="${3:-${DATABASE_FILE%_database.sql.gz}.sha256}"

if [[ -n "${COMPOSE_FILE:-}" ]]; then
  COMPOSE_PATH="$COMPOSE_FILE"
else
  ACTIVE_COMPOSE_FILE="$(docker ps --filter "label=com.docker.compose.project=$COMPOSE_PROJECT_NAME" --format '{{.Label "com.docker.compose.project.config_files"}}' 2>/dev/null | head -n 1 || true)"
  ACTIVE_COMPOSE_FILE="${ACTIVE_COMPOSE_FILE%%,*}"
  COMPOSE_PATH="${ACTIVE_COMPOSE_FILE:-$PROJECT_DIR/docker-compose.prod.yml}"
fi

[[ -n "$DATABASE_FILE" && -f "$DATABASE_FILE" ]] || { echo "Uso: $0 archivo_database.sql.gz archivo_uploads.tar.gz [archivo.sha256]" >&2; exit 1; }
[[ -n "$UPLOADS_FILE" && -f "$UPLOADS_FILE" ]] || { echo "Restore coordinado requiere el archivo de uploads emparejado." >&2; exit 1; }
for required in "$ENV_FILE" "$CHECKSUM_FILE"; do
  [[ -f "$required" ]] || { echo "No existe el archivo requerido: $required" >&2; exit 1; }
done
command -v sha256sum >/dev/null
command -v gzip >/dev/null
command -v tar >/dev/null

BACKUP_DIR="$(cd -- "$(dirname -- "$CHECKSUM_FILE")" && pwd)"
(
  cd "$BACKUP_DIR"
  sha256sum --check --strict "$(basename "$CHECKSUM_FILE")"
)
gzip -t "$DATABASE_FILE"
tar -tzf "$UPLOADS_FILE" >/dev/null
if tar -tzf "$UPLOADS_FILE" | grep -Eq '(^|/)\.\.(/|$)|^/'; then
  echo "El archivo de uploads contiene rutas inseguras." >&2
  exit 1
fi

if [[ "${VALIDATE_ONLY:-false}" == "true" ]]; then
  echo "Backup validado sin restaurar."
  exit 0
fi
command -v docker >/dev/null
if [[ "${CONFIRM_RESTORE:-}" != "RESTAURAR" ]]; then
  read -r -p "Escriba RESTAURAR para intercambiar base y uploads: " CONFIRM_RESTORE
fi
[[ "$CONFIRM_RESTORE" == "RESTAURAR" ]] || { echo "Restauración cancelada."; exit 1; }

COMPOSE=(docker compose -p "$COMPOSE_PROJECT_NAME" -f "$COMPOSE_PATH" --env-file "$ENV_FILE")
DB_USER="$("${COMPOSE[@]}" exec -T db sh -c 'printf %s "$POSTGRES_USER"')"
DB_NAME="$("${COMPOSE[@]}" exec -T db sh -c 'printf %s "$POSTGRES_DB"')"
[[ "$DB_USER" =~ ^[A-Za-z_][A-Za-z0-9_]*$ && "$DB_NAME" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || { echo "Identificadores PostgreSQL inválidos." >&2; exit 1; }
STAMP="$(date +%Y%m%d%H%M%S)"
TEMP_DB="${DB_NAME}_restore_$STAMP"
OLD_DB="${DB_NAME}_rollback_$STAMP"
FAILED_DB="${DB_NAME}_failed_$STAMP"
BACKEND_CONTAINER="$("${COMPOSE[@]}" ps -q backend)"
[[ -n "$BACKEND_CONTAINER" ]] || { echo "No se encontró el contenedor backend para resolver uploads." >&2; exit 1; }
UPLOADS_VOLUME="$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/app/app/uploads"}}{{.Name}}{{end}}{{end}}' "$BACKEND_CONTAINER")"
[[ -n "$UPLOADS_VOLUME" ]] || { echo "No se encontró el volumen montado en /app/app/uploads." >&2; exit 1; }
STAGE_VOLUME="${COMPOSE_PROJECT_NAME//[^A-Za-z0-9_.-]/_}_uploads_restore_$STAMP"
ROLLBACK_VOLUME="${COMPOSE_PROJECT_NAME//[^A-Za-z0-9_.-]/_}_uploads_rollback_$STAMP"
BACKEND_WAS_RUNNING="$("${COMPOSE[@]}" ps --status running --services | grep -cx backend || true)"
DB_SWAPPED=0
UPLOADS_SWAPPED=0

cleanup() {
  if (( DB_SWAPPED == 0 )); then
    "${COMPOSE[@]}" exec -T db dropdb --if-exists -U "$DB_USER" "$TEMP_DB" >/dev/null 2>&1 || true
  fi
  if (( UPLOADS_SWAPPED == 0 )); then
    docker volume rm "$STAGE_VOLUME" >/dev/null 2>&1 || true
    docker volume rm "$ROLLBACK_VOLUME" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

"${COMPOSE[@]}" exec -T db createdb -U "$DB_USER" "$TEMP_DB"
gunzip -c "$DATABASE_FILE" | "${COMPOSE[@]}" exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" "$1"' sh "$TEMP_DB"
"${COMPOSE[@]}" exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" "$1" -c "SELECT 1" >/dev/null' sh "$TEMP_DB"
docker volume create "$STAGE_VOLUME" >/dev/null
docker volume create "$ROLLBACK_VOLUME" >/dev/null
docker run --rm -i -v "$STAGE_VOLUME:/stage" alpine:3.20 sh -c 'tar -C /stage -xzf -' < "$UPLOADS_FILE"
docker run --rm -v "$STAGE_VOLUME:/stage:ro" alpine:3.20 sh -c 'test -d /stage && find /stage -type f -print -quit >/dev/null'

"${COMPOSE[@]}" stop backend >/dev/null

docker run --rm -v "$UPLOADS_VOLUME:/current:ro" -v "$ROLLBACK_VOLUME:/rollback" alpine:3.20 sh -c 'cp -a /current/. /rollback/'

if ! "${COMPOSE[@]}" exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" postgres -v current="$1" -v old="$2" -v replacement="$3" <<SQL
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN (:'"'"'current'"'"', :'"'"'replacement'"'"') AND pid <> pg_backend_pid();
ALTER DATABASE :"current" RENAME TO :"old";
ALTER DATABASE :"replacement" RENAME TO :"current";
SQL' sh "$DB_NAME" "$OLD_DB" "$TEMP_DB"; then
  echo "Intercambio de base de datos fallido; restaurando nombre original y saliendo." >&2
  if ! "${COMPOSE[@]}" exec -T db sh -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'\" -U \"\$POSTGRES_USER\" postgres | grep -q 1"; then
    echo "Restaurando nombre de base anterior: $OLD_DB -> $DB_NAME" >&2
    "${COMPOSE[@]}" exec -T db sh -c "psql -v ON_ERROR_STOP=1 -U \"\$POSTGRES_USER\" postgres -c \"ALTER DATABASE $OLD_DB RENAME TO $DB_NAME\"" || true
  fi
  exit 1
fi
DB_SWAPPED=1

docker run --rm -v "$UPLOADS_VOLUME:/current" -v "$STAGE_VOLUME:/stage:ro" alpine:3.20 sh -c 'find /current -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + && cp -a /stage/. /current/' || {
  echo "Falló el intercambio de uploads; revirtiendo base y uploads." >&2
  docker run --rm -v "$UPLOADS_VOLUME:/current" -v "$ROLLBACK_VOLUME:/rollback:ro" alpine:3.20 sh -c 'find /current -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + && cp -a /rollback/. /current/' || true
  "${COMPOSE[@]}" exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" postgres -v current="$1" -v old="$2" -v failed="$3" <<SQL
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :'"'"'current'"'"' AND pid <> pg_backend_pid();
ALTER DATABASE :"current" RENAME TO :"failed";
ALTER DATABASE :"old" RENAME TO :"current";
SQL' sh "$DB_NAME" "$OLD_DB" "$FAILED_DB" || true
  UPLOADS_SWAPPED=0
  DB_SWAPPED=1
  echo "Restore revertido: uploads y base restaurados a la copia previa." >&2
  exit 1
}
UPLOADS_SWAPPED=1

if (( BACKEND_WAS_RUNNING > 0 )) && ! "${COMPOSE[@]}" up -d --wait backend; then
  "${COMPOSE[@]}" stop backend >/dev/null || true
  docker run --rm -v "$UPLOADS_VOLUME:/current" -v "$ROLLBACK_VOLUME:/rollback:ro" alpine:3.20 sh -c 'find /current -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + && cp -a /rollback/. /current/'
  "${COMPOSE[@]}" exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" postgres -v current="$1" -v old="$2" -v failed="$3" <<SQL
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :'"'"'current'"'"' AND pid <> pg_backend_pid();
ALTER DATABASE :"current" RENAME TO :"failed";
ALTER DATABASE :"old" RENAME TO :"current";
SQL' sh "$DB_NAME" "$OLD_DB" "$FAILED_DB"
  "${COMPOSE[@]}" up -d backend >/dev/null || true
  echo "Restore revertido conjuntamente; base fallida conservada como $FAILED_DB." >&2
  exit 1
fi

docker volume rm "$STAGE_VOLUME" >/dev/null
echo "Restore finalizado. Base rollback: $OLD_DB; volumen uploads rollback: $ROLLBACK_VOLUME"
trap - EXIT
