#!/usr/bin/env bash
# Plantilla para copia offsite de backups SIN secretos en el script.
# Los secretos se inyectan por variables de entorno (archivos fuera del repo,
# ~/.restic-env con chmod 600, o prompting interactivo).
set -Eeuo pipefail

: "${RESTIC_REPOSITORY:?Defina RESTIC_REPOSITORY en el entorno}"
: "${RESTIC_PASSWORD_FILE:?Defina RESTIC_PASSWORD_FILE en el entorno}"
# Para OCI Object Storage (API S3) exportar también antes de ejecutar:
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (carga desde archivo externo, no hardcode)

command -v restic >/dev/null

FILES=()
for variable in BACKUP_DATABASE_FILE BACKUP_UPLOADS_FILE BACKUP_CHECKSUM_FILE; do
  if [[ -n "${!variable:-}" && -f "${!variable}" ]]; then
    FILES+=("${!variable}")
  fi
done

(( ${#FILES[@]} > 0 )) || { echo "No hay archivos de backup para subir." >&2; exit 1; }

restic backup "${FILES[@]}"
restic forget --prune --keep-daily "${KEEP_DAILY:-7}" --keep-weekly "${KEEP_WEEKLY:-4}" --keep-monthly "${KEEP_MONTHLY:-6}"
