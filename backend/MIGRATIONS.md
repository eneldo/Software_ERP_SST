# Migraciones de Base de Datos

El proyecto usa Alembic para versionar cambios de esquema. En produccion `AUTO_CREATE_TABLES` debe permanecer en `false`; las tablas se crean o modifican con migraciones.

## Comandos

Ejecutar desde `backend/`:

```powershell
alembic current
alembic upgrade head
alembic revision --autogenerate -m "descripcion_del_cambio"
```

## Base nueva

```powershell
alembic upgrade head
```

En Docker produccion:

```powershell
docker compose -f docker-compose.prod.yml --profile migrations run --rm backend-migrate
```

## Base existente previa a Alembic

Si la base ya tiene el esquema actual creado manualmente o por `AUTO_CREATE_TABLES`, marcar el baseline sin recrear tablas:

```powershell
alembic stamp head
```

Despues de eso, todo cambio de modelos debe ir en una nueva revision Alembic y aplicarse con `alembic upgrade head`.

## Regla de produccion

No activar `AUTO_CREATE_TABLES` en produccion. Si falta una tabla o columna, crear una migracion formal.
