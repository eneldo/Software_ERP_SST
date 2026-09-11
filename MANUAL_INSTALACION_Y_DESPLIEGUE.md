# Manual de instalación y despliegue — ERP SST PRO

Este manual está escrito para seguirlo de arriba hacia abajo. No hace falta saber programar. Cuando aparezca un bloque de comandos, cópielo completo, péguelo en la terminal y presione `Enter`.

## 1. Antes de comenzar

Hay dos instalaciones distintas:

- **Servidor local:** la plataforma funciona dentro de la oficina o en el mismo computador. Se accede mediante la IP local, por ejemplo `http://192.168.1.50:8080`.
- **VPS:** la plataforma queda disponible por Internet mediante un dominio y HTTPS, por ejemplo `https://sst.miempresa.com`.

En ambos casos se utiliza Docker. Docker instala PostgreSQL, Redis, backend y frontend sin tener que configurarlos uno por uno.

### Datos que debe tener preparados

- Acceso al repositorio de GitHub.
- Una contraseña larga para PostgreSQL.
- Una clave secreta de 64 caracteres o más.
- Correo y contraseña del primer administrador.
- Para VPS: IP pública, usuario con permisos `sudo` y un dominio.

> Nunca publique `.env.production`, contraseñas, llaves o copias de la base de datos en GitHub.

---

# PARTE A — INSTALACIÓN EN UN SERVIDOR LOCAL WINDOWS

## 2. Preparar el computador

Se recomienda Windows 10/11 de 64 bits, mínimo 8 GB de RAM, 4 núcleos y 30 GB libres.

### 2.1 Instalar Git

1. Entre a <https://git-scm.com/download/win>.
2. Descargue Git para Windows.
3. Instálelo aceptando las opciones predeterminadas.

### 2.2 Instalar Docker Desktop

1. Entre a <https://www.docker.com/products/docker-desktop/>.
2. Descargue Docker Desktop para Windows.
3. Instálelo con soporte WSL 2.
4. Reinicie el computador si se solicita.
5. Abra Docker Desktop y espere a que indique que Docker está funcionando.

### 2.3 Comprobar las instalaciones

Abra PowerShell y ejecute:

```powershell
git --version
docker --version
docker compose version
```

Los tres comandos deben mostrar un número de versión. Si alguno dice que no se reconoce, cierre PowerShell, vuelva a abrirlo y pruebe otra vez.

## 3. Descargar el proyecto

En PowerShell:

```powershell
cd C:\Proyectos
git clone https://github.com/eneldo/Software_ERP_SST.git sistema_gestion_sst
cd C:\Proyectos\sistema_gestion_sst
```

Si la carpeta ya existe, no vuelva a clonarla. Use:

```powershell
cd C:\Proyectos\sistema_gestion_sst
git pull origin main
```

## 4. Crear la configuración local

Copie el archivo de ejemplo:

```powershell
Copy-Item .env.production.example .env.production
notepad .env.production
```

En el Bloc de notas cambie obligatoriamente estos valores:

```dotenv
POSTGRES_PASSWORD=COLOQUE_UNA_PASSWORD_MUY_LARGA
SECRET_KEY=COLOQUE_UNA_LLAVE_ALEATORIA_DE_MINIMO_64_CARACTERES
FRONTEND_PORT=8080
FRONTEND_BIND=0.0.0.0
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
TRUSTED_HOSTS=localhost,127.0.0.1
REFRESH_COOKIE_SECURE=false
```

Para generar `SECRET_KEY`, abra otra ventana de PowerShell y ejecute:

```powershell
[Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(64)).ToLower()
```

Copie el resultado completo en `SECRET_KEY`. Guarde el archivo y cierre el Bloc de notas.

## 5. Construir e iniciar la plataforma

Desde la carpeta del proyecto:

```powershell
docker compose -f docker-compose.prod.yml --env-file .env.production build
docker compose -f docker-compose.prod.yml --env-file .env.production up -d db redis
docker compose -f docker-compose.prod.yml --env-file .env.production --profile migrations run --rm backend-migrate
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

La primera construcción puede tardar varios minutos.

### 5.1 Comprobar contenedores

```powershell
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

Debe ver `db`, `redis`, `backend` y `frontend` funcionando. Espere aproximadamente un minuto si alguno todavía dice `starting`.

### 5.2 Comprobar desde el navegador

Abra:

```text
http://127.0.0.1:8080
```

También puede probar:

```powershell
Invoke-WebRequest http://127.0.0.1:8080/health -UseBasicParsing
```

Debe responder con estado `200` y texto `ok`.

## 6. Crear el primer administrador

Este paso se hace una sola vez. Cambie el correo y la contraseña antes de ejecutar:

```powershell
docker compose -f docker-compose.prod.yml --env-file .env.production exec -e ADMIN_EMAIL=admin@miempresa.com -e ADMIN_PASSWORD="Cambiar_Esta_Clave_123!" backend python -c "import os; from app.database import SessionLocal; from app.models.usuario import Usuario; from app.auth.security import hash_password; db=SessionLocal(); correo=os.environ['ADMIN_EMAIL'].lower(); u=db.query(Usuario).filter(Usuario.correo==correo).first(); u=u or Usuario(nombres='Administrador',apellidos='Principal',correo=correo,password=hash_password(os.environ['ADMIN_PASSWORD']),rol='SUPER_ADMIN',activo=True); db.add(u); db.commit(); print('Administrador listo:',correo); db.close()"
```

Entre a `http://127.0.0.1:8080` con ese correo y contraseña. Después puede crear los demás usuarios desde el módulo **Usuarios**.

## 7. Permitir acceso desde otros computadores de la oficina

### 7.1 Conocer la IP del servidor

```powershell
ipconfig
```

Busque `Dirección IPv4`, por ejemplo `192.168.1.50`.

### 7.2 Abrir el puerto en el firewall

Abra PowerShell **como administrador**:

```powershell
New-NetFirewallRule -DisplayName "ERP SST PRO" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

En otro computador de la misma red abra:

```text
http://192.168.1.50:8080
```

Sustituya la IP del ejemplo por la IP real. Si la IP del servidor cambia, configure una IP reservada en el router o solicítela al técnico de red.

---

# PARTE B — INSTALACIÓN EN UN VPS UBUNTU

## 8. Requisitos del VPS

- Ubuntu 22.04 o 24.04 LTS.
- Mínimo 2 CPU, 4 GB RAM y 40 GB SSD; recomendado 4 CPU y 8 GB RAM.
- IP pública fija.
- Dominio apuntando a esa IP.

En el panel DNS de su dominio cree un registro tipo `A`:

```text
Nombre: sst
Valor: IP_PUBLICA_DEL_VPS
```

El resultado será algo como `sst.miempresa.com`. La propagación puede tardar.

## 9. Conectarse al VPS

Desde PowerShell en su computador:

```powershell
ssh usuario@IP_PUBLICA_DEL_VPS
```

Los comandos siguientes se ejecutan dentro del VPS.

## 10. Actualizar el servidor

```bash
sudo apt update
sudo apt upgrade -y
sudo timedatectl set-timezone America/Bogota
```

## 11. Instalar Git y Docker

```bash
sudo apt install -y git ca-certificates curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
exit
```

Vuelva a conectarse por SSH y compruebe:

```bash
docker --version
docker compose version
```

## 12. Configurar el firewall

Antes de activarlo, permita SSH:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

No abra PostgreSQL `5432`, Redis `6379`, backend `8000` ni frontend `8080` a Internet.

## 13. Descargar el proyecto

```bash
sudo mkdir -p /opt/erp-sst
sudo chown "$USER":"$USER" /opt/erp-sst
git clone https://github.com/eneldo/Software_ERP_SST.git /opt/erp-sst
cd /opt/erp-sst
```

Si GitHub solicita autenticación porque el repositorio es privado, use un token personal de GitHub como contraseña o configure una llave SSH.

## 14. Crear la configuración de producción

```bash
cp .env.production.example .env.production
nano .env.production
```

Configure como mínimo:

```dotenv
POSTGRES_DB=erp_sst
POSTGRES_USER=erp_sst_user
POSTGRES_PASSWORD=UNA_PASSWORD_LARGA_Y_UNICA
SECRET_KEY=UNA_LLAVE_ALEATORIA_DE_64_CARACTERES_O_MAS
VITE_API_URL=/api
FRONTEND_PORT=8080
FRONTEND_BIND=127.0.0.1
CORS_ORIGINS=https://sst.miempresa.com
TRUSTED_HOSTS=sst.miempresa.com
REFRESH_COOKIE_SECURE=true
REFRESH_COOKIE_PATH=/api/auth
ENVIRONMENT=production
DEBUG=false
AUTO_CREATE_TABLES=false
DOCS_URL=
REDOC_URL=
OPENAPI_URL=
```

Genere la clave secreta con:

```bash
openssl rand -hex 64
```

En `nano`, guarde con `Ctrl+O`, `Enter` y salga con `Ctrl+X`.

Proteja el archivo:

```bash
chmod 600 .env.production
```

## 15. Construir, migrar e iniciar

```bash
cd /opt/erp-sst
docker compose -f docker-compose.prod.yml --env-file .env.production build
docker compose -f docker-compose.prod.yml --env-file .env.production up -d db redis
docker compose -f docker-compose.prod.yml --env-file .env.production --profile migrations run --rm backend-migrate
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

Antes de instalar Caddy, confirme que el frontend escucha únicamente en
`127.0.0.1:8080`. No use el puerto `80` en Docker porque Caddy lo necesita:

```bash
ss -lntp | grep 8080
curl http://127.0.0.1:8080/health
```

Debe responder `ok`.

## 16. Crear el primer SUPER_ADMIN en el VPS

Cambie correo y contraseña:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec -e ADMIN_EMAIL=admin@miempresa.com -e ADMIN_PASSWORD='Cambiar_Esta_Clave_123!' backend python -c "import os; from app.database import SessionLocal; from app.models.usuario import Usuario; from app.auth.security import hash_password; db=SessionLocal(); correo=os.environ['ADMIN_EMAIL'].lower(); u=db.query(Usuario).filter(Usuario.correo==correo).first(); u=u or Usuario(nombres='Administrador',apellidos='Principal',correo=correo,password=hash_password(os.environ['ADMIN_PASSWORD']),rol='SUPER_ADMIN',activo=True); db.add(u); db.commit(); print('Administrador listo:',correo); db.close()"
```

## 17. Instalar HTTPS con Caddy

Caddy obtiene y renueva automáticamente el certificado HTTPS.

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

Edite la configuración:

```bash
sudo nano /etc/caddy/Caddyfile
```

Deje exactamente esto, cambiando el dominio:

```caddyfile
sst.miempresa.com {
    encode gzip zstd
    reverse_proxy 127.0.0.1:8080
}
```

Valide y reinicie:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
sudo systemctl status caddy --no-pager
```

Abra en el navegador:

```text
https://sst.miempresa.com
```

Si no abre, confirme que el dominio apunta a la IP correcta:

```bash
getent hosts sst.miempresa.com
```

## 18. Comprobación final

Marque cada punto:

- [ ] La página abre mediante HTTPS.
- [ ] El navegador muestra un candado válido.
- [ ] El administrador puede iniciar sesión.
- [ ] Se puede crear una empresa y un usuario de prueba.
- [ ] Se puede subir y descargar un archivo de prueba.
- [ ] `docker compose ... ps` muestra servicios saludables.
- [ ] Se creó y descargó una copia de seguridad.

---

# PARTE C — OPERACIÓN DIARIA

## 19. Ver el estado

Local Windows o VPS, desde la carpeta del proyecto:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

## 20. Ver errores

Todos los servicios:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=200
```

Solo backend:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=200 backend
```

Seguir los mensajes en vivo:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend
```

Salga con `Ctrl+C`; esto no apaga la plataforma.

## 21. Reiniciar

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production restart
```

## 22. Apagar y encender

Apagar sin borrar datos:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

Encender:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

> No use `down -v`: la opción `-v` borra los volúmenes y puede eliminar la base de datos.

## 23. Actualizar a una versión nueva

Primero haga backup. Después:

### Servidor con Coolify

```bash
cd /opt/erp-sst
./scripts/backup_postgres.sh
git pull origin main
docker compose -p erp-sst -f docker-compose.coolify.yml --env-file .env.production build --pull
docker compose -p erp-sst -f docker-compose.coolify.yml --env-file .env.production up -d
docker compose -p erp-sst -f docker-compose.coolify.yml --env-file .env.production ps
```

### Servidor con Caddy

```bash
cd /opt/erp-sst
git pull origin main
docker compose -f docker-compose.prod.yml --env-file .env.production build
docker compose -f docker-compose.prod.yml --env-file .env.production up -d db redis
docker compose -f docker-compose.prod.yml --env-file .env.production --profile migrations run --rm backend-migrate
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

En Windows cambie solamente la primera línea por:

```powershell
cd C:\Proyectos\sistema_gestion_sst
```

## 24. Crear una copia de seguridad

### VPS/Linux

```bash
cd /opt/erp-sst
chmod +x scripts/backup_postgres.sh
./scripts/backup_postgres.sh
```

Se crean tres archivos en `/opt/erp-sst/backups/`: base PostgreSQL comprimida,
uploads comprimidos y checksums SHA-256. Por defecto se eliminan copias de más
de 30 días. Configure `BACKUP_RETENTION_DAYS=0` para desactivar la retención.
Copie periódicamente estos archivos fuera del VPS.

> **Variable de entorno:** `BACKUP_RETENTION_DAYS` (default: 30).
> Añádala al `.env.production` o explícela antes de ejecutar el script:
> `BACKUP_RETENTION_DAYS=60 ./scripts/backup_postgres.sh`

### Windows PowerShell

```powershell
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
docker exec erp_sst_db pg_dump -U erp_sst_user erp_sst | gzip > "backups\erp_sst_$fecha.sql.gz"
```

Si Windows no tiene `gzip`, use esta copia sin compresión:

```powershell
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
docker exec erp_sst_db pg_dump -U erp_sst_user erp_sst | Set-Content "backups\erp_sst_$fecha.sql"
```

## 25. Restaurar una copia

Restaurar reemplaza datos. Haga antes otra copia y confirme que seleccionó el archivo correcto.

En VPS/Linux:

```bash
cd /opt/erp-sst
chmod +x scripts/restore_postgres.sh
./scripts/restore_postgres.sh \
  ./backups/NOMBRE_DEL_ARCHIVO_database.sql.gz \
  ./backups/NOMBRE_DEL_ARCHIVO_uploads.tar.gz
```

## 26. Backup automático diario en VPS

Ejecute como el usuario que administra Docker:

```bash
cd /opt/erp-sst
chmod +x scripts/install_backup_cron.sh
./scripts/install_backup_cron.sh
crontab -l
```

Esto crea una copia todos los días a las 2:15 a. m., evita ejecuciones
simultáneas y escribe el resultado en `/opt/erp-sst/backups/backup.log`.
Además debe copiar periódicamente los backups a otro servidor o almacenamiento.

---

# PARTE D — SOLUCIÓN DE PROBLEMAS

## 27. La página no abre

Ejecute:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=100 frontend backend
```

- Si `frontend` no aparece: ejecute `docker compose ... up -d`.
- Si indica puerto ocupado: cambie `FRONTEND_PORT` en `.env.production`.
- En VPS, compruebe Caddy con `sudo systemctl status caddy`.

## 28. El backend no arranca

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=200 backend
```

Errores habituales:

- `password authentication failed`: `POSTGRES_PASSWORD` no coincide con la base ya creada.
- `relation does not exist`: no se ejecutaron las migraciones.
- `SECRET_KEY`: la llave es vacía o demasiado corta.

Vuelva a ejecutar migraciones:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production --profile migrations run --rm backend-migrate
```

## 29. Error de CORS o dominio no permitido

Revise `.env.production`:

```dotenv
CORS_ORIGINS=https://sst.miempresa.com
TRUSTED_HOSTS=sst.miempresa.com
```

No agregue una `/` al final. Reinicie backend:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --force-recreate backend
```

## 30. Olvidé la contraseña del administrador

Cambie el correo y la nueva contraseña:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec -e ADMIN_EMAIL=admin@miempresa.com -e ADMIN_PASSWORD='Nueva_Clave_Segura_123!' backend python -c "import os; from app.database import SessionLocal; from app.models.usuario import Usuario; from app.auth.security import hash_password; db=SessionLocal(); u=db.query(Usuario).filter(Usuario.correo==os.environ['ADMIN_EMAIL'].lower()).first(); assert u, 'Usuario no encontrado'; u.password=hash_password(os.environ['ADMIN_PASSWORD']); u.activo=True; db.commit(); print('Contraseña actualizada'); db.close()"
```

## 31. Comandos que nunca debe ejecutar sin respaldo

```text
docker compose down -v
docker volume rm ...
docker system prune --volumes
DROP DATABASE ...
```

Estos comandos pueden borrar permanentemente la información.

## 32. Información útil para pedir soporte

Antes de pedir ayuda, recopile:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=200 > diagnostico.txt
docker version
docker compose version
```

No envíe `.env.production`. Oculte contraseñas, tokens, correos sensibles y datos personales antes de compartir registros.
