# Despliegue en Oracle Cloud Infrastructure

Esta guía complementa `MANUAL_INSTALACION_Y_DESPLIEGUE.md` para una instancia
Ubuntu de OCI. Si el servidor ya usa Coolify, despliegue
`docker-compose.coolify.yml` desde Coolify y no instale Caddy adicional.

## Red de OCI

En la lista de seguridad o NSG de la instancia permita entradas TCP para:

- `22` desde la IP administrativa, siempre que sea posible.
- `80` desde `0.0.0.0/0` para validación y redirección HTTP.
- `443` desde `0.0.0.0/0` para HTTPS.

No publique `5432`, `6379` ni el backend `8000` del ERP. Con Coolify, el
frontend tampoco publica puertos del host y Traefik lo alcanza por la red
externa `coolify`.

## Variables requeridas

Use estos valores de red en `.env.production`:

```dotenv
VITE_API_URL=/api
FRONTEND_PORT=8080
FRONTEND_BIND=127.0.0.1
CORS_ORIGINS=https://vaner.cloud
TRUSTED_HOSTS=vaner.cloud
REFRESH_COOKIE_SECURE=true
REFRESH_COOKIE_PATH=/api/auth
```

Conserve las contraseñas y `SECRET_KEY` únicamente en `.env.production`, con
permisos `600`. No copie el archivo al repositorio ni a una imagen Docker.

## Secuencia de publicación

### Servidor administrado por Coolify

Use `docker-compose.coolify.yml` y asigne `https://vaner.cloud` al servicio
`frontend`, puerto interno `80`. No publique puertos del host. El backend
aplica las migraciones Alembic antes de iniciar Gunicorn.

Instale el respaldo automático como `admin_cloud`:

```bash
cd /opt/erp-sst
chmod +x scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/install_backup_cron.sh
./scripts/install_backup_cron.sh
```

### Servidor sin Coolify

```bash
cd /opt/erp-sst
docker compose -f docker-compose.prod.yml --env-file .env.production build
docker compose -f docker-compose.prod.yml --env-file .env.production up -d db redis
docker compose -f docker-compose.prod.yml --env-file .env.production --profile migrations run --rm backend-migrate
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
docker compose -f docker-compose.prod.yml --env-file .env.production ps
curl http://127.0.0.1:8080/health
```

Instale Caddy según el manual y copie `deploy/oracle/Caddyfile.example` a
`/etc/caddy/Caddyfile`. Después valide y recargue:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
curl -I https://vaner.cloud
```

## Datos existentes

Antes de publicar, genere un respaldo nuevo de PostgreSQL y copie también los
archivos cargados. Los respaldos disponibles son históricos y no deben
asumirse como la fuente más reciente.

Después de restaurar, compruebe inicio de sesión, carga y descarga de archivos,
migraciones, salud de contenedores y creación de un respaldo desde el servidor.
