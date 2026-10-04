# Entorno

Nunca almacenar secretos en este archivo.

## Desarrollo local
- **OS:** Windows 11
- **Python:** 3.12
- **Node.js:** 20
- **Docker Desktop:** disponible (a veces no responde en 120s)
- **Puertos locales:** Backend 8000, Frontend 8081 (8080 ocupada)
- **Base local:** PostgreSQL en `sst_db_local`, volumen Docker

## Producción — Oracle Cloud (vaner.cloud)
- **OS:** Ubuntu 24.04 LTS
- **Arquitectura:** ARM64 (aarch64) — 2 CPUs, 16GB RAM
- **Hostname:** instance-sst
- **Usuario SSH:** ubuntu
- **Docker:** Docker Engine (no Desktop)
- **Docker Compose:** v2
- **Redes Docker:** erp_sst_erp_sst_net + coolify (externa)
- **Contenedores:**
  - `erp_sst_db_prod` — PostgreSQL 17 (puerto 5432 interno)
  - `erp_sst_redis_prod` — Redis 8 (puerto 6379 interno)
  - `erp_sst_backend_prod` — FastAPI + Gunicorn (puerto 8000 interno)
  - `erp_sst_frontend_prod` — Nginx unprivileged (puerto 8080 → host 8081)
- **Proxy reverso:** Coolify/Traefik (puertos 80/443, cert Let's Encrypt automático)
- **Dominio:** vaner.cloud (HTTPS activo)
- **Environment:** /opt/erp-sst/.env.production (chmod 600)
- **Archivos estáticos:** /opt/erp-sst/uploads/ (montaje volume Docker)
- **Backups:** Pendiente — Restic a OCI Object Storage (guía generada)

### Servicios externos (producción)
- **PostgreSQL:** erp_sst_db_prod:5432 (usuario: erp_sst_user, db: erp_sst_produccion)
- **Redis:** erp_sst_redis_prod:6379 (password: [CREDENCIAL_REDIS_COMPROMETIDA])
- **OCI Object Storage:** Pendiente configurar para backups Restic

Nunca almacenar secretos en este archivo.
