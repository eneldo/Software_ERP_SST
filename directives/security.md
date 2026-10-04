# Seguridad

Nunca versionar secretos.
Verificar `.env`, credenciales, permisos, dependencias, servicios y logs sensibles.

## Secret scanning

- Ejecutar localmente: `python scripts/scan_tracked_secrets.py`
- Test estático: `python -m unittest discover -s tests -p test_secret_scan.py`
- CI: workflow `.github/workflows/secret-scanning.yml` en push/PR a `main`.

## Pendiente (crítico)

Las credenciales de PostgreSQL y Redis expuestas en chat el 2026-09-11 siguen
requiriendo: (1) rotación en producción y (2) limpieza del historial Git
(BFG/git-filter-repo). No se rotan ni se reescribe el historial desde este
repositorio; son operaciones externas pendientes.
