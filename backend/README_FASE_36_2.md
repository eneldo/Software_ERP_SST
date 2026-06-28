# FASE 36.2 — Limpieza y Seguridad Base Backend

## Objetivo
Aplicar hardening base al backend del ERP SST PRO sin cambiar reglas de negocio.

## Cambios incluidos

1. `app/main.py`
   - Se agregó patrón `create_app()`.
   - Se eliminó creación obligatoria de tablas en cada arranque.
   - Se parametrizó `AUTO_CREATE_TABLES` desde `.env`.
   - Se centralizó configuración de CORS, docs y uploads.
   - Se agregó endpoint `/health`.
   - Se registraron routers faltantes detectados en la auditoría:
     - `inspecciones_exportaciones`
     - `medidas_correctivas_bi`

2. `app/config.py`
   - Se agregaron variables de configuración Enterprise.
   - Se agregó validación de `SECRET_KEY` mínimo 32 caracteres.
   - Se agregó parsing de listas CSV para CORS y subcarpetas de uploads.

3. `app/database.py`
   - Se agregó configuración básica de pooling SQLAlchemy.
   - Se mantiene `pool_pre_ping=True` para conexiones PostgreSQL estables.

4. `app/routers/auth.py`
   - `/auth/crear-usuario` queda protegido por rol `SUPER_ADMIN`.
   - Se marca como deprecated porque la ruta oficial debe ser `/usuarios-sistema/`.
   - Se normalizan correo y rol al crear usuario.

5. `requirements.txt`
   - Convertido de UTF-16 a UTF-8 para evitar errores en Docker/Linux/pip.

6. `.env.example`
   - Reemplazado por plantilla segura sin credenciales reales.

7. `.gitignore` y `.dockerignore`
   - Agregadas reglas para excluir `.env`, `.venv`, `__pycache__`, uploads reales, logs y builds.

## Archivos que NO deben subirse a GitHub

- `.env`
- `.venv/`
- `__pycache__/`
- `app/uploads/*` con evidencias reales
- logs
- bases locales `.db` / `.sqlite3`

## Comandos de prueba

```bash
cd backend
python -m py_compile app/main.py app/config.py app/database.py app/routers/auth.py
uvicorn app.main:app --reload
```

Verificar:

```bash
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Variable importante

Para desarrollo local, si aún no usa migraciones:

```env
AUTO_CREATE_TABLES=true
```

Para producción:

```env
AUTO_CREATE_TABLES=false
```

