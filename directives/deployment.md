# Deployment

No realizar despliegues destructivos sin verificar:
- configuración;
- variables;
- backups y checksum SHA-256;
- servicios;
- migraciones;
- health checks reales de PostgreSQL, Redis y HTTP;
- rollback.

## Restore y rollback

1. Generar un backup nuevo y copiarlo fuera del host.
2. Validar el manifiesto SHA-256 antes de descomprimir o modificar servicios.
3. Restaurar primero en una base temporal y ejecutar una consulta de validación.
4. Detener el backend para bloquear escrituras antes del intercambio de bases.
5. Renombrar la base actual como rollback; no sobrescribirla ni eliminarla.
6. Iniciar backend y exigir healthcheck exitoso.
7. Si falla, detener backend, devolver la base anterior a su nombre original y reiniciar.
8. Mantener el rollback hasta validar login, migraciones, uploads y operaciones críticas.
9. Tratar uploads por separado: conservar y restaurar el paquete emparejado con el mismo checksum.
