#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-erp-sst}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"

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

FILE="${1:-}"
UPLOADS_FILE="${2:-}"
if [[ -z "$FILE" ]]; then
  echo "Uso: ./scripts/restore_postgres.sh archivo_database.sql.gz [archivo_uploads.tar.gz]" >&2
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "No existe el archivo: $FILE" >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "No existe el archivo de entorno: $ENV_FILE" >&2
  exit 1
fi

gzip -t "$FILE"
if [[ -n "$UPLOADS_FILE" ]]; then
  if [[ ! -f "$UPLOADS_FILE" ]]; then
    echo "No existe el backup de uploads: $UPLOADS_FILE" >&2
    exit 1
  fi
  tar -tzf "$UPLOADS_FILE" > /dev/null
fi

if [[ "${CONFIRM_RESTORE:-}" != "RESTAURAR" ]]; then
  read -r -p "Escriba RESTAURAR para reemplazar la base actual: " CONFIRM_RESTORE
fi

if [[ "$CONFIRM_RESTORE" != "RESTAURAR" ]]; then
  echo "Restauración cancelada."
  exit 1
fi

COMPOSE=(
  docker compose
  -p "$COMPOSE_PROJECT_NAME"
  -f "$COMPOSE_PATH"
  --env-file "$ENV_FILE"
)

cd "$PROJECT_DIR"
gunzip -c "$FILE" | "${COMPOSE[@]}" exec -T db sh -c \
  'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" "$POSTGRES_DB"'

echo "Restauración de PostgreSQL finalizada desde: $FILE"

if [[ -n "$UPLOADS_FILE" ]]; then
  "${COMPOSE[@]}" exec -T backend sh -c \
    'find /app/app/uploads -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +'
  cat "$UPLOADS_FILE" | "${COMPOSE[@]}" exec -T backend \
    tar -C /app/app/uploads -xzf -
  echo "Restauración de uploads finalizada desde: $UPLOADS_FILE"
fi
