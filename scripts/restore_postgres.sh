#!/usr/bin/env sh
set -eu

if [ "${1:-}" = "" ]; then
  echo "Uso: ./scripts/restore_postgres.sh ./backups/archivo.sql.gz"
  exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
  echo "No existe el archivo: $FILE"
  exit 1
fi

gunzip -c "$FILE" | docker exec -i erp_sst_db psql -U "${POSTGRES_USER:-erp_sst_user}" "${POSTGRES_DB:-erp_sst}"

echo "Restore finalizado desde: $FILE"
