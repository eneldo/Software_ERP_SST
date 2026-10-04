import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const src = (...parts) => readFileSync(resolve(root, "src", ...parts), "utf8");
const projectFile = (...parts) => readFileSync(resolve(root, "..", ...parts), "utf8");

const authService = src("services", "authService.js");
const securityUtils = src("utils", "security.js");
const authInitializer = src("components", "auth", "AuthInitializer.jsx");
const certificadoFirmaModal = src("components", "documental", "CertificadoFirmaModal.jsx");
const requireAuth = src("components", "auth", "RequireAuth.jsx");
const app = src("App.jsx");
const axiosClient = src("api", "axios.js");
const dashboard = src("pages", "admin", "DashboardEjecutivoSST.jsx");
const adminLayout = src("layouts", "AdminLayout.jsx");
const areaApi = src("api", "areaSstApi.js");
const portalApi = src("api", "portalEmpleadoApi.js");
const medidasPage = src("pages", "sst", "MedidasCorrectivasPage.jsx");
const permisosApi = src("api", "permisosSistemaApi.js");
const incidenteApi = src("api", "incidenteApi.js");
const revisionDireccion = src("pages", "verificar", "RevisionDireccionPage.jsx");
const loginPage = src("pages", "auth", "LoginPage.jsx");
const roleConstants = src("constants", "roles.js");
const publicReportPublisher = src("components", "dashboard", "PublicReportPublisher.jsx");
const productionCompose = projectFile("docker-compose.prod.yml");
const coolifyCompose = projectFile("docker-compose.coolify.yml");
const productionEnvExample = projectFile(".env.production.example");
const productionNginx = readFileSync(resolve(root, "nginx", "default.conf"), "utf8");
const backupScript = projectFile("scripts", "backup_postgres.sh");
const backupCronInstaller = projectFile("scripts", "install_backup_cron.sh");
const restoreScript = projectFile("scripts", "restore_postgres.sh");
const infrastructureWorkflow = projectFile(".github", "workflows", "infrastructure.yml");

assert.match(authService, /api\.post\("\/auth\/login-json"/, "login debe usar /auth/login-json");
assert.match(authService, /api\.post\("\/auth\/logout"/, "logout debe limpiar cookie HttpOnly en backend");
assert.match(authService, /setAccessToken\(data\.access_token\)/, "login debe guardar access_token mediante el helper seguro");
assert.match(authService, /api\.post\("\/auth\/login-mfa"/, "MFA debe usar /auth/login-mfa");
assert.doesNotMatch(authService, /refresh_token|setRefreshToken|getRefreshToken/, "authService no debe leer ni persistir refresh tokens");
assert.doesNotMatch(securityUtils, /refresh_token|REFRESH_KEY|getRefreshToken|setRefreshToken/, "security no debe exponer refresh tokens a JavaScript");
assert.doesNotMatch(axiosClient, /getRefreshToken|setRefreshToken|Authorization.*refreshToken/, "axios debe renovar solo mediante cookie HttpOnly");
assert.doesNotMatch(authInitializer, /getRefreshToken|setRefreshToken|Authorization.*refreshToken/, "AuthInitializer debe renovar solo mediante cookie HttpOnly");
assert.match(securityUtils, /let accessToken = null/, "access_token debe mantenerse solo en memoria");
assert.match(loginPage, /status === 428/, "login debe activar el desafío MFA ante HTTP 428");
assert.match(loginPage, /name="mfa_code"/, "login debe mostrar un campo para el código MFA");
assert.match(certificadoFirmaModal, /function escapeHtml\(/, "el certificado debe escapar contenido dinámico");
assert.match(certificadoFirmaModal, /noopener,noreferrer/, "la ventana del certificado debe aislar opener");
assert.doesNotMatch(certificadoFirmaModal, /\$\{certificado\?\./, "el HTML imprimible no debe interpolar datos sin escapar");

assert.match(requireAuth, /isAuthenticated\(\)/, "RequireAuth debe usar verificacion centralizada de autenticacion");
assert.match(authService, /getAccessToken\(\)/, "authService debe leer access_token mediante el helper seguro");
assert.match(requireAuth, /<Navigate to="\/" replace state=\{\{ from: location \}\}/, "RequireAuth debe redirigir al login sin token");
assert.match(loginPage, /resolverDestinoIngreso\(sesion\?\.usuario, destinoSolicitado\)/, "login debe validar el destino segun el rol");
assert.match(roleConstants, /destinoSolicitado\.startsWith\("\/portal-empleado"\)/, "roles administrativos no deben iniciar en Portal Empleado");
assert.match(roleConstants, /if \(esRolTrabajador\(usuario\)\) return "\/portal-empleado"/, "solo perfiles laborales deben iniciar directamente en Portal Empleado");

for (const route of [
  "/admin/dashboard",
  "/organizacion/empresas",
  "/hacer/examenes-medicos",
  "/documental/firma-digital",
  "/admin/usuarios-sistema",
]) {
  const routePattern = new RegExp(`path="${route.replaceAll("/", "\\/")}"[^\\n]+<ProtectedPage`);
  assert.match(app, routePattern, `la ruta critica ${route} debe estar protegida`);
}

assert.match(axiosClient, /headers\.Authorization = `Bearer \$\{token\}`/, "axios debe enviar Authorization Bearer");
assert.match(axiosClient, /withCredentials:\s*true/, "axios debe enviar cookies HttpOnly");
assert.match(axiosClient, /\/auth\/refresh/, "axios debe intentar renovar access token con refresh token");
assert.match(productionCompose, /FRONTEND_BIND:-127\.0\.0\.1/, "produccion debe enlazar el frontend a loopback por defecto");
assert.match(productionEnvExample, /REFRESH_COOKIE_PATH=\/api\/auth/, "la cookie refresh debe cubrir la ruta publica /api/auth");
assert.match(productionNginx, /X-Forwarded-Proto \$upstream_forwarded_proto/, "nginx debe conservar HTTPS del proxy frontal");
assert.doesNotMatch(coolifyCompose, /^\s+ports:/m, "Coolify no debe publicar puertos del stack en el host");
assert.match(coolifyCompose, /traefik\.docker\.network: coolify/, "Coolify debe usar red del proxy");
assert.match(coolifyCompose, /tls\.certresolver: letsencrypt/, "Coolify debe solicitar HTTPS con Let's Encrypt");
assert.match(coolifyCompose, /backend-migrate:/, "Coolify debe separar la migración en un servicio perfilado");
assert.match(coolifyCompose, /profiles: \[migrations\]/, "la migración Coolify debe ejecutarse solo bajo perfil");
assert.match(coolifyCompose, /command: \[alembic, upgrade, head\]/, "la migración Coolify debe usar alembic upgrade head");
assert.doesNotMatch(coolifyCompose, /alembic upgrade head && exec gunicorn/, "el arranque del backend no debe ejecutar migraciones implícitas");
assert.match(backupScript, /docker compose/, "el backup debe descubrir contenedores mediante Compose");
assert.match(backupScript, /_uploads\.tar\.gz/, "el backup debe incluir los archivos cargados");
assert.match(backupScript, /sha256sum/, "el backup debe generar checksums");
assert.doesNotMatch(backupScript, /docker exec erp_sst_db/, "el backup no debe depender de nombres antiguos");
assert.match(backupCronInstaller, /erp-sst-daily-backup/, "el instalador debe gestionar una entrada cron única");
assert.match(backupScript, /OFFSITE_COMMAND/, "el backup debe soportar hook offsite configurable");
assert.match(backupScript, /BACKUP_WRITER_MODE/, "el backup debe declarar el modo de coordinación de escritores");
assert.match(backupScript, /flock/, "el backup debe bloquear ejecuciones simultáneas");
assert.match(backupScript, /gzip -t/, "el backup debe verificar la base comprimida");
assert.match(restoreScript, /VALIDATE_ONLY/, "el restore debe soportar validación sin restaurar");
assert.match(restoreScript, /_uploads_restore_/, "el restore debe preparar uploads en volumen temporal");
assert.match(restoreScript, /_uploads_rollback_/, "el restore debe conservar rollback de uploads");
assert.match(restoreScript, /DB_SWAPPED/, "el restore debe intercambiar la base con rollback");
assert.match(restoreScript, /UPLOADS_SWAPPED/, "el restore debe coordinar el rollback conjunto de uploads");
assert.match(restoreScript, /CONFIRM_RESTORE/, "el restore debe exigir confirmación explícita");
assert.match(restoreScript, /pg_terminate_backend/, "el restore debe cortar conexiones activas antes del intercambio");
assert.match(productionEnvExample, /OFFSITE_COMMAND/, "el ejemplo de producción debe documentar offsite hook");
assert.match(productionEnvExample, /BACKUP_RETENTION_DAYS/, "el ejemplo debe documentar retención de backups");
assert.match(productionEnvExample, /IMAGE_TAG/, "el ejemplo debe documentar el despliegue por artefacto");
assert.match(infrastructureWorkflow, /shellcheck/, "CI debe validar scripts shell");
assert.match(infrastructureWorkflow, /VALIDATE_ONLY/, "CI debe validar el restore sin ejecutarlo");
assert.match(infrastructureWorkflow, /PLAYWRIGHT_EXTERNAL_SERVER/, "CI debe ejecutar smoke de Playwright determinista");

assert.match(dashboard, /obtenerResumenCompletoBI/, "dashboard debe integrar los KPI BI existentes");
assert.match(dashboard, /cobertura_evaluacion/, "dashboard debe separar cobertura de cumplimiento");
assert.match(dashboard, /empresas_sin_evaluacion/, "dashboard debe mostrar empresas sin evaluacion por separado");
assert.match(dashboard, /Acciones vencidas/, "dashboard debe mostrar acciones de mejora vencidas");
assert.match(dashboard, /Últimos 12 meses/, "dashboard debe permitir revisar tendencias de 12 meses");

assert.match(app, /path="\/hacer\/accidentes"/, "Accidentes debe tener una ruta propia");
assert.match(app, /path="\/hacer\/comites"/, "Comites SST debe tener una ruta protegida");
assert.match(app, /path="\/hacer\/emergencias"/, "Emergencias SST debe tener una ruta protegida");
assert.match(app, /roles=\{ROLES_DASHBOARD\}/, "Dashboard debe validar sus roles permitidos");
assert.match(app, /roles=\{ROLES_PORTAL_EMPLEADO\}/, "Portal Empleado debe validar sus roles permitidos");
assert.match(app, /tipoInicial="ACCIDENTE"/, "la ruta de Accidentes debe aplicar su filtro inicial");
assert.match(adminLayout, /isWorker/, "el menu debe distinguir roles de empleado");
assert.match(adminLayout, /isAuditor/, "el menu debe distinguir el rol auditor");
assert.match(adminLayout, /ALTA_DIRECCION/, "el menu debe distinguir a la alta direccion");
assert.match(adminLayout, /COPASST/, "el menu debe reconocer perfiles participativos SST");
assert.match(adminLayout, /\/hacer\/comites/, "el menu debe enlazar el modulo de comites SST");
assert.match(adminLayout, /\/hacer\/emergencias/, "el menu debe enlazar el modulo de emergencias SST");
assert.match(adminLayout, /await cerrarSesion\(\)/, "cerrar sesion debe invalidar el refresh token en backend");
assert.match(dashboard, /puedeFiltrarCatalogos/, "el dashboard debe limitar filtros globales por rol");
assert.match(dashboard, /puedePublicarReporte/, "el dashboard debe limitar la publicación del reporte público a roles gestores");
assert.match(publicReportPublisher, /window\.location\.origin.*\/reporte-sst/, "el publicador debe generar el enlace con el dominio actual");
assert.match(publicReportPublisher, /Copiar enlace/, "el publicador debe permitir copiar el enlace público");
assert.match(publicReportPublisher, /Descargar QR/, "el publicador debe permitir descargar el QR");
assert.match(revisionDireccion, /puedeAprobar/, "revision por la direccion debe separar aprobacion y edicion");
assert.match(revisionDireccion, /disabled=\{!puedeAprobar\}/, "solo alta direccion debe cambiar estados gerenciales");
assert.match(areaApi, /\/areas\/exportar\/excel/, "Areas debe exponer exportacion Excel");
assert.match(areaApi, /\/areas\/exportar\/pdf/, "Areas debe exponer exportacion PDF");
assert.match(portalApi, /\/reportes\/export\/excel/, "Portal Empleado debe exponer exportacion Excel");
assert.match(medidasPage, /actualizarMedidaCorrectiva/, "Medidas Correctivas debe conectar actualizar");
assert.match(medidasPage, /eliminarMedidaCorrectiva/, "Medidas Correctivas debe conectar eliminar");
assert.match(permisosApi, /api\.put\(`\/permisos\/\$\{id\}`/, "Permisos debe conectar actualizar");
assert.match(permisosApi, /api\.delete\(`\/permisos\/\$\{id\}`/, "Permisos debe conectar eliminar");
assert.match(incidenteApi, /value !== "TODOS"/, "Incidentes no debe enviar el marcador TODOS como filtro a FastAPI");
assert.match(incidenteApi, /params: limpiarFiltrosIncidentes\(params\)/, "Incidentes debe limpiar filtros al listar y cargar dashboard");

console.log("Frontend security tests OK");
