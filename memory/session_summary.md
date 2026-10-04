# Última sesión

## 2026-10-04 — Remediación integral P0/P1 y validación final

- TDD aplicado en aislamiento tenant (profesiograma, auditoría evidencias, permisos), autenticación/MFA/XSS y biblioteca/firmas/uploads. Refresh token ya queda solo en cookie HttpOnly y el frontend no lo expone a JavaScript.
- Plan Anual: nueva migración reparadora segura (`m5n6o7p8q9r0`), uploads atómicos, conteo solo activos y agregados sin huérfanos; ISSUE-020 quedó mitigado (RBAC DELETE de actividad aún pendiente).
- Infraestructura endurecida: restore coordinado base+uploads con rollback conjunto, backup con modo writer y off-site documentado, CI shell/static/Docker, smoke E2E determinista, secrets scanning y despliegue por `IMAGE_TAG`.
- Dependencias auditadas: `anyio` 4.14.2, `PyJWT` 2.15.0, `pyasn1` 0.6.4, eliminada cadena vulnerable de `ecdsa`, `pip` 26.2.0; `pip_audit` 0 vulnerabilidades y Ruff OK.
- Validación final: backend 260 passed; unittest raíz 35/35; npm test/lint/build/audit OK; `docker compose config` prod y Coolify OK; Alembic limpia hasta `head`; scripts shell validados.
- Pendientes externos: rotar credenciales PostgreSQL/Redis y limpiar historial Git, ejecutar smoke/restore en servidor y registrar versión productiva.
- Git: commit `d80df18` y push a `origin/main`.

## 2026-10-04 — P0/P1 infraestructura: restore coordinado, backup, CI shell/smoke, artefacto SHA

- Sin commits. Se corrigió la atomicidad real del restore: primero se intercambia la base (con reintento de restaurar nombre original si falla) y después uploads; fallo en uploads ahora revierte base y uploads conjuntamente; VALIDATE_ONLY ya no requiere Docker (chequeos movidos detrás) y funciona en CI.
- Backup: `BACKUP_WRITER_MODE` (stop-backend) y `OFFSITE_COMMAND` documentados en `.env.production.example`; nueva plantilla `scripts/offsite_restic_example.sh` sin secretos inline.
- `scan_tracked_secrets.py`: la regex de asignaciones ahora detecta `SECRET_KEY`/`*_TOKEN` con prefijo; el manual ya no contiene placeholders no reconocidos. Escaneo y tests OK.
- Compose: `image: erp-sst-{backend,frontend}:${IMAGE_TAG:-local}` para despliegue por artefacto SHA; healthcheck de prod ya no hardcodea `Host: vaner.cloud` (usa `TRUSTED_HOSTS`); Coolify mantiene migración como servicio perfilado separado (README corregido: ya NO dice que el backend migra al arrancar).
- CI: nuevo job `shell-scripts` (bash -n, shellcheck --severity=warning, fixture VALIDATE_ONLY de restore, tests estáticos); smoke de Playwright determinista contra el stack Compose en `infrastructure.yml` (external server, CI=true).
- `tests/test_infrastructure_static.py` (13 pruebas) + assertions nuevas en `frontend/tests/security.test.mjs` (restore coordinado, offsite, IMAGE_TAG, Chrome migración separada).
- Validaciones: bash -n OK; shellcheck 0 findings; fixture VALIDATE_ONLY OK; unittest raíz 35/35 OK; security.test.mjs OK; YAML OK.
- Limitaciones: no se ejecutó Docker/docker compose localmente (daemon no disponible en dev); el smoke real en CI corre contra la red de compose y Postgres efímero; `shellcheck-py` fue instalado solo localmente.

## 2026-10-04 — Sanitización de credenciales versionadas + secret scanning

- Búsqueda exhaustiva en archivos versionados (Markdown/config/scripts): sin valores reales restantes; placeholders `[CREDENCIAL_*]` y `CAMBIAR_*` conservados.
- `MANUAL_INSTALACION_Y_DESPLIEGUE.md`: sustituidos literales de ejemplo `Cambiar_Esta_Clave_123!`/`Nueva_Clave_Segura_123!` y `POSTGRES_PASSWORD`/`SECRET_KEY` no neutros por referencias neutrales.
- Corregido regex de `scripts/scan_tracked_secrets.py` para detectar `SECRET_KEY`/`*_SECRET_KEY` (antes no capturaba el sufijo `_KEY`).
- Scan: OK; test estático `tests/test_secret_scan.py`: 2/2 OK. CI ya definida en `.github/workflows/secret-scanning.yml`.
- Documentado en `directives/security.md` e ISSUE-013 que la **rotación de credenciales y la limpieza de historial Git siguen pendientes** (operaciones externas, no ejecutadas). Sin commits.

## 2026-10-04 — P1 autenticación, MFA UI y XSS (TDD)

- Auth backend emite exactamente un refresh token por login/refresh, lo almacena solo en cookie HttpOnly, no lo incluye en `TokenResponse` y `/auth/refresh` ya no acepta Bearer fallback.
- Frontend eliminó lectura/persistencia de refresh token en `security`, `authService`, Axios y `AuthInitializer`; la rotación usa únicamente `withCredentials` y conserva mutex compartido.
- Login UI maneja HTTP 428, solicita TOTP de 6 dígitos y completa el flujo por `/auth/login-mfa`.
- `CertificadoFirmaModal` escapa todos los campos insertados en el HTML imprimible y abre la ventana con `noopener,noreferrer` y `opener=null`.
- TDD RED: backend 6 fallos/14 éxitos; frontend falló por MFA ausente. GREEN: backend focalizado 20/20 y frontend security OK.
- Validaciones: frontend lint 0 errores/245 warnings preexistentes y build limpio OK. Suite backend completa bloqueada por `DATABASE_URL` ausente; Ruff no está instalado en `.venv`.
- Sin commits.

## 2026-10-04 — P0 aislamiento tenant: profesiograma, evidencias de auditoría y permisos

- TDD RED confirmado: 10 regresiones nuevas fallaron por accesos cross-tenant y mutaciones globales sin restricción.
- Profesiograma fuerza tenant para no SUPER_ADMIN, valida cargo/empresa y limita mutaciones de catálogos globales a SUPER_ADMIN.
- Evidencias de hallazgos validan hallazgo/auditoría padre y filtran eliminación por tenant; SUPER_ADMIN conserva acceso global.
- CRUD global de permisos queda exclusivo de SUPER_ADMIN; asignación/consulta de terceros permite SUPER_ADMIN global y administradores autorizados solo dentro de su empresa.
- GREEN: 10/10 nuevas y 34/34 suite relacionada; Ruff, py_compile y git diff --check aprobados. Suite backend completa no inició porque DATABASE_URL no estaba definido.
- Sin commits.

## 2026-10-04 — P1 uploads, biblioteca y firmas digitales con TDD

- Auditoría hallazgos reutiliza `validate_upload` para límite y magic bytes; ante fallo de persistencia hace rollback y elimina el archivo físico.
- Biblioteca exige permiso documental de escritura en upload, valida `archivo_id` activo del mismo tenant y crea archivo/documento en una sola transacción con `flush`, rollback y compensación física.
- Firmas digitales validan el tenant del usuario propietario en upload, listados, firma activa, activación y eliminación.
- TDD focalizado: RED confirmado (5 fallos/1 pase); GREEN final 9/9. `py_compile` y Ruff focalizados aprobados.
- Sin commits. Se preservaron modificaciones preexistentes, incluido el aislamiento tenant ya presente en auditoría.

## 2026-09-23 — Ejecución local y recorrido funcional

- Puertos revisados antes del arranque: `8001` pertenece a SIGEM (Docker); `8000` y `5173` estaban libres.
- Backend ERP iniciado en `http://127.0.0.1:8000` y frontend en `http://127.0.0.1:5173`; healthcheck 200 con base de datos OK.
- Login UI correcto con usuario local SUPER_ADMIN; refresh token respondió 200 y la sesión se restauró después de navegación.
- Módulos verificados en modo lectura con respuestas API 200: Dashboard, Empresas, Plan Anual, EPP, Inspecciones, Indicadores y Biblioteca Documental.
- Una navegación masiva activó el rate limiter; la UI mostró el mensaje controlado y la sesión sobrevivió, consistente con ISSUE-019.
- Servicios quedaron ejecutándose. `frontend/.env` local apunta a `VITE_API_URL=http://127.0.0.1:8000` para evitar conflicto con SIGEM.

## 2026-09-21 — Levantamiento local en puertos alternos + tour funcional + validación ISSUE-019

### Servicios locales (sin Docker)
- **Backend:** FastAPI `http://127.0.0.1:8001` (PID 13272, health 200, db ok) — puerto `8000` ocupado por otro proyecto (SIGEM), por eso se usa `8001`.
- **Frontend:** Vite `http://127.0.0.1:5173` (PID 18988) con `frontend/.env` (gitignored) apuntando a `VITE_API_URL=http://127.0.0.1:8001`.
- **PostgreSQL:** nativo Windows en `5432`, base `sst_erp` (empresa 9 Radiologia RAD).
- Lanzamiento persistente vía `Win32_Process.Create` (los hijos de `Start-Process` mueren al terminar el comando).

### Tour funcional verificado (UI + API)
- **Login/logout:** API 200 (`admin@sst.com`) y UI OK como `prueba@sst.com` (RESPONSABLE_SST, sesión restaurada) y `admin@sst.com` (SUPER_ADMIN).
- **Dashboard:** KPIs reales, tendencia 12 meses, top riesgos, sedes/áreas ROJO.
- **Empresas:** 1 empresa, 25 trabajadores, logo, KPIs, tabla completa.
- **Empleados:** 3 empleados, tabla + dashboard lateral.
- **Plan Anual:** cabecera vigencia 2026 carga.
- **Matriz IPER GTC45:** tabla NP/NR/nivel riesgo.
- **Exámenes médicos:** permiso por rol OK — "Nuevo examen" deshabilitado para RESPONSABLE_SST, habilitado para SUPER_ADMIN.
- **EPP:** cobertura 66.7%, 5 entregas, catálogo EPP-001–004, 9 alertas críticas.
- **Inspecciones:** 1 inspección, PDF Platinum, semáforo VERDE.
- **Indicadores:** 0 registrados; bajo ráfaga muestra "Demasiadas solicitudes" y se recupera tras ventana de 60s.

### ISSUE-019 VALIDADO (pendiente cerrado)
- 429 real reproducido: `Access-Control-Allow-Origin: http://127.0.0.1:5173` presente en la respuesta 429.
- Axios lee el 429 (no es opaco), la UI muestra mensaje graceful y `auth/refresh` sigue 200 — la sesión sobrevive.
- Evidencia: `.tmp/local-admin-dashboard-2026-09-21.png`.

### Nota
- Dejar corriendo backend (8001) y frontend (5173) para las pruebas del usuario. `frontend/.env` local ahora apunta a `8001` (ignorado por Git).

## 2026-09-18 — Auditoría integral Exámenes Médicos: correcciones de seguridad, roles, dashboard y permisos

### Correcciones backend (examenes_medicos.py, relation_guard.py, examen_medico_schema.py, profesiograma.py)

1. **ROLES_SST ampliado (examenes_medicos.py):** `TECNICO_SST`, `TALENTO_HUMANO` y `MEDICO_OCUPACIONAL` ahora pueden acceder al módulo de exámenes médicos. Antes solo podían `SUPER_ADMIN`, `ADMIN_EMPRESA` y `RESPONSABLE_SST`.
2. **ROLES_SST ampliado (profesiograma.py):** Mismos roles agregados para mantener consistencia.
3. **Smart Delete tenant isolation:** `_validar_tenant_ownership()` agregada a `ejecutar_eliminacion_inteligente()` Y `validar_eliminacion()` (GET + DELETE) en `relation_guard.py`. Valida que el registro pertenece al tenant del usuario. `SUPER_ADMIN` excluido. Entidades: `examen_medico`, `epp_catalogo`, `epp_entrega`, `inspeccion`, `capa`, `incidente`, `comite`.
4. **Dashboard con métricas reales:** `dashboard_examenes_medicos()` ahora calcula y devuelve `empleados_activos`, `empleados_con_examen`, `cobertura_poblacion`, `indice_aptitud`, `indice_restricciones`, `riesgo_medico` (BAJO/MEDIO/CRITICO), `vencen_7`, `vencen_15`, `vencen_30`. Agregados charts `por_area`, `tendencia_mensual`, `vencimientos_mensuales`.
5. **Evidencias empresa_id desde empleado:** `subir_evidencia_examen_medico()` ahora obtiene `empresa_id` del empleado asociado al examen, no del parámetro `tenant_id`.
6. **Generador desde profesiograma:** Observaciones marcadas como `[GENERADO DESDE PROFESIOGRAMA] Requiere valoración médica`. `MAPEO_TIPO_EVALUACION` convierte códigos legacy a enums válidos (`PRE_INGRESO→INGRESO`, `PERIODICA→PERIODICO`, `EGRESO→RETIRO`, `RETORNO→RETORNO_LABORAL`).
7. **Validación fecha_vencimiento:** `ExamenMedicoBase` y `ExamenMedicoUpdate` ahora validan que `fecha_vencimiento >= fecha_examen`.

### Correcciones frontend (ExamenesMedicosSSTPage.jsx)

1. **Permisos por rol:** Botones de Editar, Evidencias y Eliminar ahora solo se muestran para roles autorizados:
   - Editar/Evidencias: `SUPER_ADMIN`, `ADMIN_EMPRESA`, `MEDICO_OCUPACIONAL`
   - Eliminar: `SUPER_ADMIN`, `ADMIN_EMPRESA`, `RESPONSABLE_SST`, `COORDINADOR_SST`
   - Botón "Nuevo examen" deshabilitado para roles sin permisos de escritura clínica.
2. **emptyDashboard sin valores engañosos:** `indice_cumplimiento`, `cobertura_poblacion`, `indice_aptitud` ahora inician en `0` en lugar de `100`. `riesgo_medico` inicia en `SIN_DATOS`.

### Ejemplos creados (empresa 9)
- **ID 4:** Lina Sofia Gonzalez Valcarcel (empleado 25) — PERIODICO, APTO, 2026-09-10 a 2027-09-10
- **ID 5:** Edna Rubiela valcarcel Vargas (empleado 24) — INGRESO, APTO_CON_RESTRICCIONES, 2026-09-12 a 2027-09-12
- Ambos con observaciones "EJEMPLO AUDITORIA EXAMENES MEDICOS" para identificación.

### Validaciones
- Tests: 32/32 pasando (test_auditoria_p0_epp_insp_med, test_export_redaction, test_concepto_medico, test_historia_clinica, test_dashboard_concepto, test_upload_security_p1).
- Frontend build: OK.

## 2026-09-18 — Exportaciones Plan Anual, ficha EPP, Comités, Perfil Sociodemográfico y Profesiogramas

### Correcciones funcionales
- **Plan Anual:** permisos de exportación ahora usan la matriz por rol cuando no hay permisos explícitos. PDF corregido para leer vigencia, alcance, objetivo, meta general y firmas desde `PlanAnualCabecera`; Excel incluye vigencia, alcance, objetivo y meta general.
- **EPP:** la ficha técnica ahora usa `resolveFileUrl()` y el CSP permite `frame-ancestors` desde los orígenes configurados en CORS. El archivo protegido respondió 200 y dejó de resolver hacia el SPA/dashboard.
- **Comités SST:** creados COPASST (id 1) y Comité de Convivencia (id 3), cada uno con 4 integrantes paritarios. El Vigía SST de prueba se desactivó porque la empresa registra 25 trabajadores y corresponde COPASST. Nuevo endpoint `GET /sst/comites/{id}/acta-constitucion-pdf` y botón `Acta PDF`; los documentos incorporan marco normativo, integrantes y firmas.

### Perfil Sociodemográfico
- Nuevo dashboard por empresa, sede, año y mes con corte histórico al final del período.
- KPIs: plantilla al corte, activos, inactivos, perfiles registrados/completados, cobertura, empleados sin fecha de ingreso y datos históricos incompletos.
- Tendencia mensual y distribución por sede en React/Recharts.
- Nuevos endpoints: `/empleados-perfil/dashboard`, `/dashboard/exportar-excel`, `/dashboard/exportar-pdf`.
- Añadido `empleados.fecha_retiro` (modelo, schemas, formulario y migración `l4m5n6o7p8q9`).
- Alembic local actualizado desde `b4c5d6e7f8a9` hasta `l4m5n6o7p8q9 (head)` como propietario PostgreSQL debido a ownership mixto de tablas.
- Validación real: anual 2026 = 3 activos; junio 2026 = 1 activo. Excel 200 (2 hojas: Resumen/Detalle empleados), PDF 200 y UI verificada.

### Profesiograma / Evaluaciones Médicas
- Registrados 3 profesiogramas activos para empresa 9: Auxiliar Administrativo (id 1), Profesional HSEQ (id 2), Talento Humano (id 3).
- Cada profesiograma tiene las 7 categorías de evaluación y exámenes del catálogo según riesgos del cargo.
- Talento Humano actualizado a `requiere_vigilancia_medica=true`.
- UI verificada: 3 profesiogramas activos, 7 tipos de evaluación y 20 exámenes en catálogo.
- No se generaron evaluaciones clínicas automáticas: el generador actual tiene incompatibilidades de enums y no debe emitir conceptos `APTO` automáticamente sin valoración médica.

### Validaciones
- Frontend `npm run build`: OK.
- Tests focalizados Perfil Sociodemográfico: 6 pasando; py_compile y Ruff OK.
- PDFs de actas, dashboard y Plan Anual: respuestas válidas `%PDF`.
- Excel de dashboard y Plan Anual: archivos XLSX válidos.

## 2026-09-18 — Levantamiento local + revisión Plan Anual + fix CORS 429

### Servicios locales levantados
- **Backend:** FastAPI `http://127.0.0.1:8000` (uvicorn `.venv`, PID 17212, health 200)
- **Frontend:** Vite `http://127.0.0.1:5173` (PID 5796)
- **PostgreSQL:** 1 solo servidor en `5432` (PID 9532); NO hay Docker en `5433`. Un solo backend activo.

### Vección: solo una base del ERP (`sst_erp`, empresa 9)
- Servidor tiene 16 bases; el ERP solo usa `sst_erp` (1 empresa: Radiología RAD, NIT 902249656). Las demás (SGA, sigm, internado_db, vaner_asset*, vitalflow_*, sga_clean, sga_pro) son de otros proyectos.
- Tabla de usuarios: `usuarios` — `admin@sst.com` (id 1, SUPER_ADMIN) y `prueba@sst.com` (id 21, RESPONSABLE_SST), ambos empresa_id=9. 98 tablas en public.

### Fix ISSUE-019: respuestas 429 sin cabeceras CORS
- **Síntoma:** errores CORS opacos en plan-anual y logout inesperado al recorrer módulos.
- **Causa:** `RateLimitMiddleware` fuera de `CORSMiddleware` → 429 sin `access-control-allow-origin`; afectaba a `auth/refresh`.
- **Fix:** `CORSMiddleware` movido a middleware MÁS EXTERNO en `backend/app/main.py`. Verificado: plan-anual cargando con 200 y sin errores CORS.

### Revisión Plan Anual (como `prueba@sst.com`)
- Solo 1 cabecera vigente: **id=10, vigencia 2026** (creada por usuario 21). Las de 2025/2027/2028 fueron eliminadas (hard delete) durante pruebas previas.
- `GET /cabeceras/9` devuelve la misma cabecera para admin y prueba → mis datos correctos, sin conflicto de backends.
- **CRUD actividades verificado vía API (todo 200):** crear (id 14) → listar → editar (PUT incl. avance) → finalizar (PATCH → EJECUTADO 100%) → eliminar con admin (soft delete `activo=False`; **403 para RESPONSABLE_SST**).
- Actividad de prueba eliminada y limpiada; BD quedó sin residuos (cabecera 10 = 0 actividades).
- Comportamiento `normalizar_estado_y_avance`: crea la actividad como **VENCIDO** si `fecha_fin < hoy`.

### ISSUE-020 (documentado): anomalías del Plan Anual
1. `DELETE /actividades/{id}` solo SUPER_ADMIN/ADMIN_EMPRESA, pero el frontend muestra el botón Eliminar a RESPONSABLE_SST (403). En cambio, el RESPONSABLE_SST SÍ puede eliminar la cabecera.
2. `actividades_count` cuenta actividades `activo=False` (tras soft-delete dice 1 con lista vacía).
3. 3 actividades huérfanas legacy (ids 11-13, `plan_anual_cabecera_id=NULL`, vigencias 2026 pasadas) inflan `resumen`/`dashboard` (total 3, presupuesto 49,3M) sin aparecer en el módulo.

### Archivos tocados
- `backend/app/main.py` — fix CORS (ISSUE-019)
- `memory/learnings.md`, `memory/known_issues.md`, `memory/session_summary.md` — documentación

### Pendiente
- Reproducir un 429 real para confirmar cabeceras CORS en la respuesta.
- Decidir permisos de DELETE de actividad por rol (ISSUE-020) y limpiar/migrar huérfanas legacy.
- Recorrido de módulos incompleto (plan-mejoramiento, HACER/*, VERIFICAR/*, documental/*, admin/*).

## 2026-09-17 — Plan Anual SST: cabeceras CRUD + fix rutas + seed IPER

### Estado final funcional
- **URL frontend:** http://127.0.0.1:5173/planear/plan-anual
- **Credenciales test:**
  - `admin@sst.com` / `[CREDENCIAL_LOCAL_ADMIN]` (SUPER_ADMIN, empresa_id=9)
  - `prueba@sst.com` / `[CREDENCIAL_LOCAL_PRUEBAS]` (RESPONSABLE_SST, ID 21, empresa_id=9) — creada hoy para pruebas manuales
- **Cabeceras activas finales:** ID 6=2025, ID 1=2026, ID 7=2027, ID 8=2028
- **Matriz IPER:** 6 registros (IDs 1-3 originales + 6,7,8 seeded hoy)
- **Tests:** 226 pasando antes del trabajo de Plan Anual; seed IPER validado via API
- **Frontend build:** OK (`npm run build` en 7.68s)

### Fix principal: "Cabecera del Plan Anual no encontrada" al cargar actividades
- **Causa raíz:** Ruta `GET /cabecera/{empresa_id}/{vigencia}` definida ANTES que `GET /cabecera/{cabecera_id}/actividades/`. FastAPI capturaba `/cabecera/1/actividades/` como empresa_id=1, vigencia="actividades" → 404.
- **Solución:** Reordenar rutas en `backend/app/routers/plan_anual.py`: las rutas de actividades (`/cabecera/{id}/actividades/`) ahora van ANTES que la ruta de búsqueda por empresa/vigencia.
- **Verificado via API (200):**
  - `GET /planear/plan-anual/cabeceras/9` → 4 cabeceras
  - `GET /planear/plan-anual/cabecera/1/actividades/` → 200 `[]`
  - `GET /planear/plan-anual/cabecera/9/2026` → 200 ID 1
  - `GET /planear/plan-anual/detalle/1` → 200
  - `DELETE /planear/plan-anual/cabecera/8` → 200, luego recrear misma vigencia 2028 → 200 (hard delete permite re-crear)

### Cambios en `backend/app/routers/plan_anual.py`
- Añadido `DELETE /cabecera/{cabecera_id}` (hard delete con cascade de actividades) — soft delete bloqueaba re-crear misma vigencia por `UniqueConstraint(empresa_id, vigencia)`.
- Renombrada ruta detalle: `/cabecera/{id}/completo` → `/detalle/{cabecera_id}` (la original colisionaba con ruta empresa/vigencia).
- Reordenadas rutas: actividades antes que `obtener_cabecera` (empresa/vigencia).
- Endpoints con `_error_response` usan campo `message` (NO `detail`) — frontend lee ambos.

### Cambios en `frontend/src/pages/planear/PlanAnualPage.jsx`
- Vigencia: solo dígitos (`replace(/\D/g,"").slice(0,4)`), `inputMode="numeric"`, `pattern="\d{4}"`, maxLength 4.
- `guardarCabecera`: fix de estado stale (usa variable local `cabeceraId` en vez de `cabeceraSeleccionada`), regex `^\d{4}$`, pre-chequeo de vigencia duplicada.
- `mostrarError`: lee `resp?.detail || resp?.message`.
- Botones **Ver / Editar / Eliminar** visibles en AMBOS pasos ("cabecera" y "actividades") — antes solo en "cabecera", pero `seleccionarCabecera` avanzaba automáticamente al paso actividades.
- Formulario de edición con "Cancelar Edición"; modal detalle (info + firmas + tabla actividades).
- Estilos nuevos en `frontend/src/styles/plan-anual.css` (`.pa-modal*`, `.pa-detail*`).

### Cambios en BD (manuales, sin migración Alembic)
- Creada tabla `plan_anual_cabecera` (antes no existía → 500 DATABASE_ERROR).
- Añadida columna `plan_anual_cabecera_id` (FK) a `plan_anual_sst`.
- Modelos: `backend/app/models/plan_anual_cabecera.py`, `backend/app/models/plan_anual.py`.
- Schema: `backend/app/schemas/plan_anual.py` — `vigencia` con `pattern=r"^\d{4}$"`.

### Seed IPER (via API, MatrizIPERPage)
- Creados riesgos IDs 6, 7, 8 para empresa 9 → verificados en listado y dashboard.
- Rol test: OPERADOR(no existe/500) → EMPLEADO(sin permisos SST) → TECNICO_SST(403 en IPER) → **RESPONSABLE_SST** (accede IPER, Empleados, Dashboard).

### Firma sesión — aprendizajes registrados en learnings.md y known_issues.md
- ISSUE-016 (hard delete para unique constraint), ISSUE-017 (orden de rutas FastAPI), ISSUE-018 (plan_anual_cabecera manual sin migración).
- Ver `memory/learnings.md` y `memory/known_issues.md`.

## 2026-09-17 — Revisión funcional módulo Empresa + Logo Upload

### Corrección: botón subir logo no abre selector de archivos
- **Problema:** El botón "Subir o cambiar logo" (icono nube 28x28px) no abría el selector de archivos. El usuario hacía click en las iniciales del logo (div 44x44px) que no tenía handler.
- **Causa raíz:** Un `<input type="file">` oculto con `display: none` bloquea `.click()` en Firefox/Safari. Además, el `<div>` de iniciales no tenía onClick.
- **Corrección aplicada** en `frontend/src/pages/organizacion/EmpresasSSTPage.jsx`:
  - Eliminado `fileInputRef`, `empresaLogoTargetRef`, el `<input>` oculto del JSX, y `handleLogoChange`.
  - `seleccionarLogo()` ahora crea el input dinámicamente con `document.createElement("input")` usando `position: fixed; opacity: 0` (no `display: none`).
  - `renderLogo()` acepta parámetro `onLogoClick` — las iniciales del logo ahora son clickeables.
  - Ambos (iniciales + botón nube) disparan `seleccionarLogo()`.
- **Archivos modificados:**
  - `frontend/src/pages/organizacion/EmpresasSSTPage.jsx` — refactoring completo del upload de logo
  - `frontend/src/styles/empresas-sst.css` — CSS del input oculto cambiado a `position: fixed`

### Corrección: limpieza de logos en backend
- **Problema:** `POST /empresas/{id}/logo` no eliminaba el archivo físico anterior al subir uno nuevo (acumulaba archivos huérfanos). `DELETE /empresas/{id}/logo` solo ponía `None` en BD sin borrar el archivo.
- **Corrección aplicada** en `backend/app/routers/empresas.py`:
  - `subir_logo_empresa`: antes de escribir el nuevo archivo, lee `empresa.logo`, resuelve la ruta con `LOGOS_DIR / Path(logo_anterior).name`, y ejecuta `unlink()` si existe.
  - `eliminar_logo_empresa`: ejecuta `unlink()` del archivo físico antes de poner `empresa.logo = None`.
- **Endpoints verificados:**
  - `POST /empresas/9/logo` → 200 OK, crea archivo, elimina anterior
  - `DELETE /empresas/9/logo` → 200 OK, elimina archivo, BD = None
  - `GET /logos-empresa/{filename}` → 200 OK, sirve imagen (endpoint público)

### Pruebas realizadas
- Upload via Python requests: OK
- Upload via UI (botón "Subir o cambiar logo" + file chooser): OK, mensaje de éxito visible
- Delete via UI (botón "Eliminar logo" + confirm dialog): OK, logo eliminado de tabla
- Logo display en tabla: correcto (test_logo.png cuadrado azul visible)

### Entorno local
- **Backend:** FastAPI en `http://127.0.0.1:8000` (uvicorn, PID 15296)
- **Frontend:** Vite dev server en `http://127.0.0.1:5173` (PID 14472)
- **Base de datos:** PostgreSQL 17 nativo Windows en puerto `5432` (no Docker)

### Hallazgo: Race condition en refresh token
- **Problema:** `AuthInitializer` y el interceptor de axios compiten por el mismo refresh token al recargar la página. El refresh usa rotación single-use, así que el segundo request recibe 401.
- **Causa:** Los links del sidebar usan `<a href>` (recarga completa) en vez de React Router `<Link>`. Al recargar, `accessToken` (en memoria) se pierde y ambos componentes intentan refrescar simultáneamente.
- **Corrección aplicada:** Mutex de refresh en `security.js` (getRefreshPromise/setRefreshPromise). Tanto `AuthInitializer` como el interceptor ahora comparten la misma promise, evitando llamadas duplicadas.
- **Archivos modificados:**
  - `frontend/src/utils/security.js` — agregado `refreshPromise` module-level con getter/setter
  - `frontend/src/api/axios.js` — interceptor usa `getRefreshPromise()` antes de crear nueva llamada
  - `frontend/src/components/auth/AuthInitializer.jsx` — usa `getRefreshPromise()` para reutilizar promise existente

### Módulo Empresa — Revisión funcional completa

#### Datos en BD
| Campo | Valor |
|-------|-------|
| ID | 9 |
| Nombre | Radiologia RAD |
| NIT | 902249656 |
| Dirección | Calle 23 # 11-35 |
| Teléfono | 3105236575 |
| Correo | sst.radiologiarad@gmail.com |
| Representante Legal | Maria Perez |
| ARL | Positiva |
| Trabajadores | 25 |
| Clase Riesgo | III |
| Tipo Empresa | EMPRESA |
| Estándares SST | 21 (empresa 11-50 trabajadores, riesgo I-III) |
| Estado | ACTIVA |
| Logo | /uploads/logos/empresa_9_f359815856b240ef9d8a7df6c752390e.png |

#### Funcionalidades verificadas
| Función | Estado | Notas |
|---------|--------|-------|
| Login | OK | JWT access + refresh tokens, rotación |
| Listar empresas | OK | 1 empresa activa, tabla completa con logo |
| KPIs | OK | Total=1, Activas=1, Inactivas=0, Riesgo IV/V=0, Trabajadores=25 |
| Distribución riesgo | OK | Riesgo I-V, Riesgo III=1 |
| Filtros | OK | Estado, Clase riesgo, Tipo empresa, ARL, búsqueda libre |
| Paginación | OK | 10/20/50/100 registros, navegación páginas |
| Ver detalle | OK | Modal con todos los campos + logo + botones Subir/Cerrar/Editar |
| Editar empresa | OK | 4 tabs (Datos generales, Contacto, SST, Clasificación), campos pre-llenados |
| Nueva empresa | OK | Formulario vacío con 4 tabs |
| Exportar CSV | OK | 16 columnas, encoding correcto, nombre archivo con fecha |
| Actualizar | OK | Recarga datos desde backend |
| Limpiar filtros | OK | Resetea todos los filtros |
| Eliminación inteligente | OK | Botón presente (no ejecutado para preservar datos) |
| Subir logo | OK | Botón presente en tabla y en detalle |
| Eliminar logo | OK | Botón presente en tabla |

### API CRUD verificada (Python requests)
| Endpoint | Método | Status | Notas |
|----------|--------|--------|-------|
| `/auth/login-json` | POST | 200 | JWT tokens retornados |
| `/empresas/` | GET | 200 | Lista 1 empresa |
| `/empresas/9` | GET | 200 | Detalle completo |
| `/empresas/` | POST | 200 | Crear test OK, cálculo automático estándares |
| `/empresas/10` | DELETE | 200 | Eliminación inteligente OK |
| `/auth/refresh` | POST | 200 | Rotación token OK |

### Archivos generados
- `.tmp/empresa-module-overview.png` — screenshot listado completo
- `.tmp/empresa-detalle-modal.png` — screenshot modal detalle
- `.tmp/empresa-edit-form.png` — screenshot formulario edición
- `.tmp/empresa-new-form.png` — screenshot formulario nueva empresa
- `.playwright-mcp/empresas-sst-2026-09-17.csv` — exportación CSV descargada

## 2026-09-12 — Despliegue producción + Guías PDF + Memoria

### Producción desplegada
- Oracle Cloud Always Free (Ubuntu 24.04, ARM64, 2 CPUs, 16GB RAM)
- URL: https://vaner.cloud (HTTPS via Coolify/Traefik)
- Docker: PostgreSQL 17, Redis 8, FastAPI backend, Nginx frontend
- Todos los contenedores ejecutándose y healthchecks OK
- Git pushed a https://github.com/eneldo/Software_ERP_SST.git (main)

### Correcciones durante despliegue
- Frontend Dockerfile: nginxinc/nginx-unprivileged en vez de nginx:alpine (problemas permisos ARM64)
- Redis healthcheck: --appendonly yes falló (permisos), cambiado a --save 60 1000
- Backend healthcheck: agregado -H "Host: vaner.cloud" para TRUSTED_HOSTS
- Redis contraseña: ciertos caracteres especiales causaban errores de URL parsing; se cambió temporalmente por otra credencial, que también requiere rotación
- Backend eliminado import no utilizado require_roles (F401) en empleados_perfil.py
- .env.production.example: agregado TRUSTED_PROXY_NETWORKS=172.16.0.0/12

### Guías PDF generadas
- `.tmp/Guia_cambio_credenciales_PostgreSQL_Redis_vaner.cloud.pdf` — guía para rotar credenciales
- `.tmp/operacion_vaner/Manual_backups_y_pendientes_vaner.cloud.pdf` — 22 páginas, guía completa de operación
- `.tmp/operacion_vaner/backup_vaner.sh` — script de backup con Restic + OCI Object Storage
- `.tmp/operacion_vaner/probar_restore_vaner.sh` — script de prueba de restore aislado
- `.tmp/Paquete_operacion_vaner.cloud.zip` — paquete distribuible con todo lo anterior

### Pendientes críticos
1. **URGENTE:** Rotar contraseña PostgreSQL ([CREDENCIAL_POSTGRES_COMPROMETIDA]) — comprometida en chat
2. **URGENTE:** Verificar/rotar contraseña Redis
3. Instalar timer de backups diarios en el servidor Oracle
4. Ejecutar primer backup manual antes de automatizar
5. Probar restore aislado en el servidor
6. Preservar modificaciones locales en Git (branch ops/vaner-backups)
7. Ejecutar pruebas funcionales (login, CRUD, evidencias, tenant isolation, exports)

### Memoria actualizada
- learnings.md: agregados 3 aprendizajes (despliegue Oracle Cloud, Restic backups, fpdf2 PDFs)
- known_issues.md: agregados ISSUE-013 (credenciales comprometidas), ISSUE-014 (backup sin pausa), ISSUE-015 (Docker no responde)
- project_context.md: actualizado estado de producción con Oracle Cloud
- environment.md: llenado con entorno local y producción
- user_preferences.md: agregadas preferencias de idioma, documentación, despliegue, seguridad, Git

## Sesión anterior

Fecha: 2026-09-11

## Hardening de infraestructura

- Backend productivo multi-stage y no-root (UID 10001); frontend migrado a Nginx unprivileged (UID 101, puerto 8080).
- Gunicorn 23.0.0 quedó fijado como única modificación de dependencias.
- Compose prod/Coolify exige rate limiting Redis, usa healthchecks HTTP/PostgreSQL/Redis reales y aplica límites de CPU, memoria, capacidades y privilegios.
- CI nuevo valida ambos Compose, construye imágenes, inicia PostgreSQL/Redis y ejecuta Alembic con variables ficticias.
- Restore exige SHA-256, valida en base temporal, pausa escrituras, intercambia bases y revierte automáticamente ante healthcheck fallido.
- Validaciones aprobadas: ambos `docker compose config --quiet`, builds backend/frontend, `py_compile`, `git diff --check` y `bash -n` en contenedor Bash 5.2.

## Corrección HTTP 422 en Incidentes

- La página enviaba el marcador `TODOS` en filtros query, incluyendo `empresa_id`, `sede_id` y `area_id`, que FastAPI valida como enteros.
- `incidenteApi.js` ahora elimina `TODOS` antes de cargar listado y dashboard.
- Se añadió una prueba de regresión en `frontend/tests/security.test.mjs`.
- Validaciones: `npm test`, `npm run lint` (0 errores, 232 warnings preexistentes) y `npm run build:clean` aprobadas.
- Build desplegado en `erp_sst_frontend_clean` con `VITE_API_URL=/api`; listado y dashboard respondieron HTTP 200 sin parámetros inválidos.

## Inspecciones SST - Evidencias, Notificaciones y UI

### Bug fix: empresa_id duplicado en crear_inspeccion
- `inspecciones.py:829` pasaba `empresa_id=tenant_id` como kwarg, pero `data.model_dump()` ya lo incluía.
- Solución: asignar `payload["empresa_id"] = tenant_id` antes de crear el modelo.

### Bug fix: evidencias no funcionan para SUPER_ADMIN
- Endpoints `listar_evidencias`, `subir_evidencia`, `eliminar_evidencia` usaban `_empresa_id_autorizada(usuario, None)`.
- Con token `empresa_id=null`, retornaba `None` y la query `empresa_id == None` no encontraba registros.
- Solución: agregar parámetro `empresa_id: int | None = Query(default=None)` a los 3 endpoints.
- Frontend: API ahora envía `empresa_id` como query param en las 3 funciones.

### Notificaciones toast - construirMensajeError undefined
- `construirMensajeError()` se usaba en los bloques `catch` pero no estaba definida.
- Causaba `ReferenceError` dentro del catch, perdiéndose silenciosamente la notificación de error.
- Solución: agregar la función con extracción de `error.response.data.detail`.

### Notificaciones agregadas
- `subirEvidencia()`: success/error toast
- `borrarEvidencia()`: success/error toast
- `eliminar()`: success/error toast
- `guardarHallazgo()`: success toast (antes usaba `alert()`)

### UI mejorada - columna Acciones
- Header con icono `<Settings /> Acciones`
- Botones icon-only 32x32 con colores diferenciados:
  - View: azul `#e0f2fe`
  - Edit: teal `#ccfbf1`
  - PDF: azul medio `#dbeafe`
  - Delete: rojo `#fee2e2`
- Separadores visuales entre grupos
- PDF Platinum: icono `FileText` en vez de texto

### Seed data - 6 inspecciones
- INS-2026-001: GENERAL, CERRADA, CUMPLE, BAJO, 95%
- INS-2026-002: LOCATIVA, EJECUTADA, CUMPLE_PARCIAL, MEDIO, 72%
- INS-2026-003: EPP, PROGRAMADA, PENDIENTE, ALTO, 0%
- INS-2026-004: MAQUINARIA, CERRADA, NO_CUMPLE, CRITICO, 35%
- INS-2026-005: ORDEN_ASEO, EN_PROCESO, PENDIENTE, MEDIO, 60%
- INS-2026-006: SEGURIDAD, EJECUTADA, CUMPLE, BAJO, 88%

### Git
- Commit: `0f387e9` - 56 archivos, +2260/-1016 líneas
- Push: `origin/main` exitoso

## Corrección nombres y extensiones de descargas (data URLs)

- Chrome descargaba exportaciones válidas con nombres UUID sin extensión; retrasar `revokeObjectURL` 60s no resolvió el problema.
- **Causa raíz:** Chrome ignora el atributo `download` en URLs `blob:http://...`; sí lo respeta en URLs `data:...`.
- **Solución:** Convertir toda respuesta blob a base64 y construir `data:${contentType};base64,${base64}`. Para contenido local (CSV/HTML), usar `btoa(unescape(encodeURIComponent(content)))`.
- 29 archivos frontend modificados (17 API + 6 páginas + 3 componentes + 3 helpers).
- Validaciones: `npm test`, `npm run lint` y `npm run build:clean` aprobadas.
- Se reconstruyó `sistema_gestion_sst-frontend:data-url-fix` y se recreó `erp_sst_frontend_clean` en `127.0.0.1:8081`.
- Solo `useReporteAssetUrl.js` conserva `createObjectURL` (previsualización en elemento, no descarga).

## Corrección edición de exámenes médicos

- Editar un examen devolvía 404 para SUPER_ADMIN porque la consulta exigía `Empleado.empresa_id == None`.
- La actualización ahora busca por ID y agrega el filtro tenant solo cuando el usuario tiene una empresa objetivo.
- Se añadió regresión para SUPER_ADMIN global; el archivo conjunto alcanzó `17 passed`.
- Se validó desde la interfaz la actualización de médico, IPS y observaciones, confirmada en PostgreSQL.

## Corrección creación de exámenes médicos

- Crear un examen fallaba con HTTP 500 porque `empleado_id` llegaba duplicado al constructor `ExamenMedico`.
- Se eliminó `empleado_id` del payload limpio antes de reasignar el empleado validado.
- Se añadió una prueba de regresión; el archivo conjunto alcanzó `16 passed` y compilación Python correcta.
- Se validó desde la interfaz y PostgreSQL el examen de ingreso APTO/VIGENTE de Edna Valcarcel.
- Ruff reporta nueve hallazgos preexistentes en el router y test histórico.

## Corrección creación y listado de catálogo EPP

- Se corrigió el listado vacío para SUPER_ADMIN: cuando no seleccionaba empresa, el backend filtraba incorrectamente `empresa_id IS NULL`; ahora omite el filtro y lista todas las empresas.
- Se validó visualmente que la tabla muestra `EPP-001` y `EPP-002`.
- Se añadió regresión para SUPER_ADMIN sin empresa; el archivo de auditoría EPP alcanza `15 passed`.
- Se reprodujo el error HTTP 500 al crear un EPP: `EPPCatalogo()` recibía `empresa_id` dos veces.
- Se corrigió `crear_catalogo()` excluyendo `empresa_id` de `model_dump()` y asignando únicamente el tenant autorizado.
- Se añadió una prueba de regresión; `14 passed` en `test_auditoria_p0_epp_insp_med.py` y compilación Python correcta.
- Se validó desde la interfaz y en PostgreSQL la creación de `EPP-001`, Casco de seguridad industrial, para la empresa 1.
- Ruff conserva cuatro hallazgos preexistentes: tres imports sin uso en `epp.py` y una variable sin uso en el test histórico.
- Como el contenedor backend no monta el código fuente, el archivo corregido se copió al contenedor en ejecución y se reinició; una recreación futura requiere reconstruir la imagen para conservar el fix en runtime.

## Sesión anterior

Fecha: 2026-09-08

## Ejecución Docker local y login

- Se cerraron todos los procesos locales en los puertos `8000` y `5173`.
- Se inspeccionaron las bases Docker SST sin eliminar ni modificar volúmenes.
- `sst_backup_inspect_data` contiene 7 empresas, 2 sedes y 15 empleados; se dejó detenido.
- Para una ejecución limpia se seleccionó `sst_db_data`, con 0 empresas, 0 sedes y 0 empleados.
- La base limpia corre en `sst_db_local`, PostgreSQL publicado en `5433`, conectada a `sistema_gestion_sst_erp_sst_net` con alias `db`.
- El stack activo usa `erp_sst_backend`, `erp_sst_redis` y `erp_sst_frontend_clean`.
- La aplicación está disponible en `http://127.0.0.1:8081`; se usó `8081` porque `8080` estaba ocupado por otra aplicación.
- El backend Docker se ejecuta en modo `development` para aceptar hosts locales; se verificó el login real y la redirección a `/admin/dashboard`.
- Existe un usuario `SUPER_ADMIN` activo en la base limpia. Su contraseña fue restablecida, pero no se almacena aquí por seguridad.

## Sesión anterior

Fecha: 2026-09-06

## Commits de la sesión (14 commits)

| Commit | Hallazgo | Descripción |
|--------|----------|-------------|
| `e9175d6` | H-013a/b/c | JWT blocklist + MFA TOTP + matriz roles normativos |
| `599ea70` | H-014 | Tipos normativos capacitación (INDUCCION, REINDUCCION, RIESGO_ESPECIFICO) |
| `9d8dde8` | H-016 | Indicadores oficiales SST (TF/TG/TI/Mortalidad/Ausentismo) |
| `52a4f85` | H-018 | Alertas vencimiento matriz legal + servicio notificaciones |
| `de9e008` | H-017 | Estándares mínimos CRUD + historial + vinculación plan mejora |
| `9e3dd96` | H-019 | Fix tenant seguimientos y evidencias plan mejoramiento |
| `7e95dbe` | H-020 | Alertas 11 dominios + plantillas notificación |
| `ab1ba4c` | H-021 | CSV endpoints faltantes + periodo metadata |
| `9d5d4ef` | H-007 | Seed 60 numerales reales Resolución 0312 de 2019 |
| `6346090` | H-011 | Evaluación psicosocial (Res. 2646/2008) + Historia clínica ocupacional |
| `d5559b2` | H-022 | Verificación plan mejoramiento frontend + responsable_id FK |
| `nuevo` | H-036 | **Módulo Informe de Gestión SG-SST - Backend + Frontend** |

## Estado actual

- **Tests:** 188/188 GREEN, 2 warnings
- **Backend:** compilación OK
- **Migraciones:** 25+ (20260904_0001 a 20260906_0002)
- **Branch:** main, pushed

## Hallazgos P0 — Estado (TODOS RESUELTOS)

| ID | Hallazgo | Estado |
|---|---|---|
| H-001 | Historia clínica permisos | RESUELTO |
| H-002 | CAPA schema↔modelo | RESUELTO |
| H-003/4/5 | Tenant EPP/Inspecciones/Exámenes | RESUELTO |
| H-006 | Baseline vs migraciones | RESUELTO |
| H-007 | Criterios Res.0312 (60 numerales) | RESUELTO |
| H-008 | Exportaciones ownership | RESUELTO |
| H-009 | Políticas obligatorias | RESUELTO |
| H-010 | Archivos tenant/hash | RESUELTO |
| H-011 | Psicosocial + HCO | RESUELTO |
| H-012 | Dashboard datos reales | RESUELTO |
| H-013 | RBAC/MFA/tokens | RESUELTO |
| H-021b/c/d/e | Exportaciones tenant | RESUELTO |
| H-022/23 | Cierre plan + verificación | RESUELTO |
| H-024/25 | Notificaciones/Planes tenant | RESUELTO |

## Hallazgos P1 — Estado (TODOS RESUELTOS)

| ID | Hallazgo | Estado |
|---|---|---|
| H-014 | Plan anual capacitación/inducción | RESUELTO |
| H-015 | Plan Anual tenant/dashboard | RESUELTO |
| H-016 | Indicadores fórmulas oficiales | RESUELTO |
| H-017 | Estándares plan mejora + RBAC | RESUELTO |
| H-018 | Matriz legal exportaciones/alertas | RESUELTO |
| H-019 | Planes mejora origen/verificación | RESUELTO |
| H-020 | Alertas 11 dominios + canales | RESUELTO |
| H-021 | Reportes CSV + metadatos | RESUELTO |

## Hallazgos P2 — Estado (TODOS VERIFICADOS/RESUELTOS)

| ID | Hallazgo | Estado |
|---|---|---|
| H-027 | Auditoría de cambios | YA IMPLEMENTADO |
| H-028 | Logs aplicación estructurados | YA IMPLEMENTADO |
| H-029 | Rate-limit API | YA IMPLEMENTADO |
| H-030 | Perfiles de usuario | RESUELTO (mi-perfil endpoint) |
| H-034 | Historial acciones usuario | YA IMPLEMENTADO |

## Hallazgos P3 — Estado (TODOS RESUELTOS)

| ID | Hallazgo | Estado |
|---|---|---|
| H-031 | Exportación datos personales (RGPD) | RESUELTO |
| H-032 | Follow-up planes de acción | YA IMPLEMENTADO |
| H-033 | Certificados digitales con QR | RESUELTO |
| H-035 | Notificaciones push | RESUELTO |

## Archivos nuevos (esta sesión - P3)

- `backend/app/models/push_subscription.py`
- `backend/app/services/notificaciones_push_service.py`
- `backend/app/routers/notificaciones_push.py`

## Archivos nuevos (esta sesión - Informe Gestión)

### Backend
- `backend/app/models/informe_gestion.py` — 8 modelos SQLAlchemy
- `backend/app/schemas/informe_gestion_schema.py` — Schemas Pydantic
- `backend/app/services/informe_gestion_service.py` — Servicio consolidación
- `backend/app/routers/informe_gestion.py` — 25 endpoints REST
- `backend/alembic/versions/20260906_0003_informe_gestion.py` — Migración

### Frontend
- `frontend/src/api/informeGestionApi.js` — API cliente
- `frontend/src/pages/verificar/InformeGestionPage.jsx` — Página principal

### Archivos modificados
- `backend/app/main.py` — Registro modelo + router
- `frontend/src/App.jsx` — Ruta /verificar/informe-gestion

## Archivos modificados (esta sesión - P3)

- `backend/app/routers/capacitacion_certificados.py` — QR en PDF + verificación
- `backend/app/routers/usuarios_sistema.py` — mi-perfil + mis-datos (RGPD)
- `backend/app/main.py` — registro notificaciones_push router

## Archivos nuevos (esta sesión - actualización)

- `backend/app/services/alertas_11_dominios_service.py` — 11 dominios de alertas
- `backend/app/routers/alertas_11_dominios.py` — router consolidador

## Archivos modificados (esta sesión - actualización)

- `backend/app/routers/plan_anual.py` — validador fechas + dashboard endpoint
- `backend/app/routers/matriz_legal.py` — exportaciones Excel/PDF
- `backend/app/main.py` — registro alertas_11_dominios router

## DB Fixes (2026-09-06 - session extension)

| Tabla | Columna agregada | Causa |
|-------|-----------------|-------|
| `planes_mejoramiento_sst` | `responsable_id INTEGER` | Dashboard `/dashboard-sst/resumen` 500 |
| `politicas_sst` | `tipo_politica VARCHAR(50)` | Política SST `/planear/politica-sst/` 500 |
| `archivos_sst` | `hash_sha256 VARCHAR(64)`, `fecha_descarga TIMESTAMP` | Evaluación Inicial `/planear/evaluacion-inicial/` 500 |

## Producción - Estado final (2026-09-11)

### Gates verificados

| Gate | Resultado |
|------|-----------|
| Backend tests | 205 passed, 0 failed, 2 warnings |
| Ruff lint | All checks passed (0 errors) |
| pip-audit | No known vulnerabilities |
| Frontend lint | 0 errors, 232 warnings (preexistentes) |
| npm audit | 0 vulnerabilities |
| Frontend build | OK (12.67s) |
| Docker compose prod | config --quiet OK |
| Backend import | OK |

### Correcciones finales

- `backend/app/routers/empleados_perfil.py`: eliminado import `require_roles` no utilizado (F401)
- `.env.production.example`: agregado `TRUSTED_PROXY_NETWORKS=172.16.0.0/12` para validación Docker Compose prod

### Limitaciones residuales conocidas (no bloqueantes)

- Alembic: DB en `h8i9j0k1l2m3`, código en `k3l4m5n6o7p8` — necesita `alembic upgrade head` en producción
- Frontend: 232 warnings ESLint preexistentes (react-hooks/exhaustive-deps, no-alert)
- Coolify: requiere `APP_DOMAIN` variable (Coolify-specific, no es bug)
- Backend ejecuta como root en Dockerfile.prod (harden pendiente)
- CI workflow: docker job necesita env vars completas para validar

## Próximos pasos

- **Producción:** Ejecutar `alembic upgrade head` para sincronizar DB
- P2: evaluación Kirkpatrick, validaciones fechas/enums, índices BD
- P3: QR certificados, plantillas PDF, firma pAdES
- **Informe Gestión:** PDF/Excel export, dashboard completo, alertas automáticas
- **Migraciones:** Crear migración unificada para todas las columnas agregadas manualmente
