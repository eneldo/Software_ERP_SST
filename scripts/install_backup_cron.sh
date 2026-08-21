#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup_postgres.sh"
BACKUP_DIR="$PROJECT_DIR/backups"
CRON_SCHEDULE="${CRON_SCHEDULE:-15 2 * * *}"
CRON_MARKER="# erp-sst-daily-backup"
CRON_LINE="$CRON_SCHEDULE /usr/bin/flock -n /tmp/erp-sst-backup-cron.lock $BACKUP_SCRIPT >> $BACKUP_DIR/backup.log 2>&1 $CRON_MARKER"

command -v crontab > /dev/null
command -v flock > /dev/null

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
chmod +x "$BACKUP_SCRIPT" "$SCRIPT_DIR/restore_postgres.sh"

CURRENT_CRONTAB="$(crontab -l 2>/dev/null || true)"
{
  printf '%s\n' "$CURRENT_CRONTAB" | grep -vF "$CRON_MARKER" || true
  printf '%s\n' "$CRON_LINE"
} | sed '/^[[:space:]]*$/d' | crontab -

echo "Backup diario instalado: $CRON_SCHEDULE"
echo "Log: $BACKUP_DIR/backup.log"
