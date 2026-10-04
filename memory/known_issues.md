# Problemas Conocidos

### ISSUE-019 — Respuestas 429 del rate limiter sin cabeceras CORS (login/logout durante módulos)

**Estado:** RESUELTO Y VALIDADO (2026-09-21)

**Síntoma:** Al recorrer módulos rápido, el navegador mostraba errores CORS opacos en `/planear/plan-anual` y `auth/refresh` fallaba, devolviendo al usuario al login en medio de la sesión.

**Causa:** `RateLimitMiddleware` estaba registrado FUERA de `CORSMiddleware`. La respuesta 429 no atravesaba CORS → sin `access-control-allow-origin`, el navegador ocultaba status/body. Sobre `auth/refresh`, el 429 del CORS-rotativo expulsaba al usuario.

**Solución:** Movido `CORSMiddleware` a ser el middleware MÁS EXTERNO (registrado después de `AuditMiddleware`, al final del bloque en `backend/app/main.py`). Verificado: preflight OPTIONS y respuestas GET de plan-anual con cabeceras CORS presentes (todas 200).

**Validación 2026-09-21:** 429 real reproducido con `Origin: http://127.0.0.1:5173` → respuesta trae `Access-Control-Allow-Origin: http://127.0.0.1:5173`. Axios lee el status (no opaco), la UI muestra "Demasiadas solicitudes…" y se recupera tras 60s; `auth/refresh` sigue 200, la sesión sobrevive.

---

### ISSUE-020 — Plan Anual: DELETE de actividades 403 para RESPONSABLE_SST + conteos engañosos

**Estado:** MITIGADO (2026-10-04; conteos/huérfanos corregidos, decisión RBAC DELETE pendiente)

**Síntoma:**
1. `DELETE /planear/plan-anual/actividades/{id}` retorna 403 para RESPONSABLE_SST, pero el frontend le muestra el botón Eliminar en la fila (error UX). En cambio SÍ puede eliminar la CABECERA (y sus actividades en cascada).
2. `actividades_count` de la cabecera cuenta actividades `activo=False` (soft-deleted): después de eliminar todas, dice "1 actividad" con lista vacía.
3. Actividades huérfanas legacy (`plan_anual_cabecera_id=NULL`, ids 11-13 en empresa 9) inflan `resumen/` y `dashboard/` (total, presupuesto) sin aparecer en el módulo por cabecera.

**Causa:**
1. `eliminar_actividad` usa `require_roles(["SUPER_ADMIN","ADMIN_EMPRESA"])` mientras `eliminar_cabecera` usa `ROLES_ESCRITURA` (incluye RESPONSABLE_SST). ECM local: frontend no condiciona el botón por rol.
2. `serializar_cabecera` usa `len(item.actividades)` sin filtrar `activo`.
3. Legacy: actividades creadas vía endpoints/etapas anteriores sin cabecera; `eliminar_cabecera` borra solo las que apuntan a esa cabecera.

**Actualización 2026-10-04:** Las actividades/conteo se migraron y excluyen `activo=False`/huérfanos; resumen/dashboard filtran por cabecera o vigencia válida. **Pendiente:** alinear permiso DELETE de actividad y el botón frontend.

---

**Estado:** RESUELTO

**Síntoma:** Múltiples endpoints permitían acceso cross-tenant: listados, CRUD, exportaciones, evidencias y generación desde profesiograma no validaban `usuario.empresa_id`.

**Causa:** Solo se usaba `require_roles()` para autorización RBAC, sin filtrar por `usuario.empresa_id` en queries ni validar recursos padre antes de acceder a hijos.

**Solución:** Helper `_empresa_id_autorizada` aplicado a 87+ endpoints en EPP, Inspecciones/Seguimientos y Evaluaciones Médicas. Validación de recursos padre (inspección, examen, entrega) antes de listar/crear/modificar hijos (hallazgos, seguimientos, evidencias, firmas). Exportaciones filtran por tenant. Profesiograma filtrado por `empresa_id` del cargo.

---

### ISSUE-012 — Migraciones Alembic colisionaban con baseline dinámico en instalación limpia

**Estado:** RESUELTO

**Síntoma:** `alembic upgrade head` en base temporal vacía fallaba por tablas/columnas duplicadas en IPER, Política SST, Exámenes Médicos, Historial Legal, Perfil Sociodemográfico, Indicadores.

**Causa:** Baseline `0001_initial_schema` usa `Base.metadata.create_all()` con metadata actual, pero migraciones posteriores intentaban crear/alterar elementos ya materializados.

**Solución:** Guardas de existencia y tipo (`sa.inspect`) en 10 migraciones históricas + nueva migración CAPA. Validación completa en base temporal propietaria de `sst_user` hasta `head` (21 migraciones) sin errores.

---

### ISSUE-009 — CAPA producía HTTP 500 por deriva entre schema y modelo

**Estado:** RESUELTO

**Síntoma:** La creación, aprobación y el seguimiento de medidas correctivas enviaban campos inexistentes en los modelos SQLAlchemy.

**Causa:** Los schemas y routers usaban `ishikawa_json`, costos, campos de aprobación, `proxima_accion` y `fecha_proximo_seguimiento`, pero las tablas y modelos no los definían.

**Solución:** Alinear modelos y base mediante la migración `e1f2a3b4c5d6`, y cubrir los constructores con pruebas de regresión.

---

### ISSUE-010 — Instalación limpia Alembic colisionaba con el baseline dinámico

**Estado:** RESUELTO

**Síntoma:** Una base vacía fallaba por tablas o columnas duplicadas al ejecutar migraciones posteriores a `0001_initial_schema`.

**Causa:** El baseline usa la metadata actual con `create_all()`, pero varias migraciones históricas intentaban crear de nuevo elementos ya presentes.

**Solución:** Agregar guardas de existencia y tipo a las migraciones IPER, Política SST, exámenes médicos, historial legal, perfil sociodemográfico e indicadores. La cadena completa fue validada desde una base vacía hasta `head`.

---

### ISSUE-001 — Exportación Excel IPER no coincide con plantilla

**Estado:** RESUELTO

**Síntoma:** La exportación Excel actual usa la función genérica `generar_excel_corporativo` que genera encabezados simples, mientras que la plantilla oficial tiene encabezados de dos niveles con celdas combinadas, formato verde, y dos hojas (ADMINISTRATIVA/OPERATIVO).

**Causa:** No existía una función específica de exportación para IPER que replicara la estructura de la plantilla.

**Solución:** Crear función específica `exportar_excel_iper` en `matriz_iper.py` que use openpyxl directamente con celdas combinadas, fondo verde #A8D08D, Times New Roman bold, bordes medios, y hojas ADMINISTRATIVA/OPERATIVO.

---

### ISSUE-002 — Registros existentes con valores np=0, nr=0

**Estado:** MITIGADO

**Síntoma:** Registros creados antes de implementar el cálculo automático tienen valores np=0, nr=0, interpretacion_np="", nivel_riesgo="".

**Causa:** El cálculo automático no existía al momento de crear esos registros.

**Solución:** Endpoint `PUT /recalcular/{empresa_id}` implementado para recalcular todos los registros de una empresa.

---

### ISSUE-007 — Campo riesgos_asociados en Cargos no se guardaba (3 fallos simultáneos)

**Estado:** RESUELTO

**Síntoma:** Al crear/editar un cargo, el campo "Riesgos asociados" se llenaba pero se guardaba vacío en BD.

**Causa:** Tres fallos simultáneos:
1. Modelo `Cargo` sin columna `riesgos_asociados`
2. Router `_payload_compatible()` hacía `payload.pop("riesgos_asociados")` explícitamente
3. Frontend `construirPayload()` no incluía `riesgos_asociados` en el payload enviado

**Solución:**
1. Modelo `cargo.py`: agregado `riesgos_asociados = Column(String(700))`
2. Router `cargos.py`: eliminado `payload.pop("riesgos_asociados")`
3. Frontend `CargosSSTPage.jsx`: agregado `riesgos_asociados` en `construirPayload()`

---

### ISSUE-008 — Filtro Estado en Cargos no necesario, pero KPIs lo usan programáticamente

**Estado:** RESUELTO (mejora UX)

**Síntoma:** Dropdown "Estado" en grid de filtros confundía al usuario, pero las KPI cards (Total/Activos) usan filtrado programático.

**Solución:** Eliminado dropdown "Estado" del grid visual. Mantenido `estado` en estado inicial y `limpiarFiltros` para que KPI cards (Total/Activos) sigan filtrando programáticamente. Backend sigue aceptando `estado` como query param.

---

### ISSUE-003 — NameError en inspecciones.py: _archivo_variant_url no definida

**Estado:** RESUELTO

**Síntoma:** Upload de evidencias en inspecciones retornaba 500. Listado de evidencias también fallaba con 500. El error en logs era `NameError: name '_archivo_variant_url' is not defined`.

**Causa:** `_archivo_variant_url` se usaba en `_archivo_to_dict()` pero nunca estaba definida ni importada en `inspecciones.py`.

**Solución:** Agregada función `_archivo_variant_url()` en `inspecciones.py` que busca variantes en `INSPECCIONES_PREVIEW_DIR` y `INSPECCIONES_THUMB_DIR`.

---

### ISSUE-004 — Frontend usa /uploads/ en lugar de /archivos-protegidos/

**Estado:** RESUELTO

**Síntoma:** Botón "Ver" evidencia en Matriz Legal, Matriz Peligros, Plan Anual, Plan Mejoramiento mostraba "Recurso no encontrado" (404).

**Causa:** `abrirArchivo()` usaba `${API_URL}${url}` directamente (ej: `http://localhost:8000/uploads/matriz-legal/file.webp`), pero no existe ruta `/uploads/` en FastAPI.

**Solución:** Cambiar a `resolveFileUrl(url)` que convierte `/uploads/` → `/archivos-protegidos/` automáticamente.

**Módulos afectados:** MatrizLegalPage, MatrizPeligrosPage, PlanAnualPage, PlanMejoramientoPage.

---

### ISSUE-005 — upload_service.py no comprime PDFs

**Estado:** RESUELTO

**Síntoma:** PDFs subidos a módulos que usan `upload_service.py` (matriz-legal, matriz-peligros, plan-anual, capacitaciones, evaluacion-inicial) se guardaban sin optimizar.

**Causa:** `guardar_documento_sin_comprimir()` guardaba el contenido tal cual sin pasar por pikepdf.

**Solución:** Agregada función `_optimizar_pdf_bytes()` en `upload_service.py` y llamada en `guardar_documento_sin_comprimir()` cuando extensión es `.pdf`.

---

### ISSUE-006 — Módulos con _guardar_upload local sin compresión PDF

**Estado:** RESUELTO

**Síntoma:** capa.py, incidentes.py, inspeccion_seguimientos.py, medidas_correctivas.py, portal_empleado.py guardaban PDFs sin optimizar.

**Causa:** Estos módulos tenían `_optimizar_imagen_bytes()` para imágenes pero no para PDFs.

**Solución:** Agregada `_optimizar_pdf_bytes()` + llamada en `_guardar_upload()` de cada módulo.

---

### ISSUE-013 — Credenciales de PostgreSQL/Redis comprometidas en chat

**Estado:** PENDIENTE (rotación y limpieza de historial requeridas)

**Síntoma:** Las contraseñas de PostgreSQL (`[CREDENCIAL_POSTGRES_COMPROMETIDA]`) y Redis (`[CREDENCIAL_REDIS_ANTERIOR_COMPROMETIDA]`) se discutieron abiertamente en el chat de la sesión de 2026-09-11.

**Causa:** Durante el despliegue a producción, el usuario compartió las credenciales en el chat para resolver problemas de configuración.

**Solución:** Las contraseñas deben rotarse inmediatamente en el servidor de Oracle Cloud. Se generó una guía PDF (`Guia_cambio_credenciales_PostgreSQL_Redis_vaner.cloud.pdf`) con los pasos exactos para rotar PostgreSQL y Redis. La contraseña de Redis fue cambiada a `[CREDENCIAL_REDIS_COMPROMETIDA]` después de que la anterior causara errores de URL parsing. **La contraseña de PostgreSQL no fue rotada y debe hacerse urgente.**

**Riesgo:** Si el chat fue archivado o es accesible por terceros, las credenciales están comprometidas. PostgreSQL expone toda la base de datos del ERP SST (datos de empresas, empleados, historiales clínicos).

**Actualización 2026-10-04:** Se sanitizaron los archivos versionados (placeholders neutros), se añadió `scripts/scan_tracked_secrets.py`, test estático `tests/test_secret_scan.py` y workflow `.github/workflows/secret-scanning.yml`. **Sigue pendiente:** rotar credenciales en producción y limpiar el historial Git; ambas son operaciones externas no realizadas.

---

### ISSUE-014 — Backup sin pausa de escritores y restore sin rollback coordinado

**Estado:** MITIGADO (2026-10-04)

**Síntoma:** El script `backup_vaner.sh` toma SQL dump y archivos subidos sin pausar las escrituras del backend, lo que puede causar inconsistencia entre la base y los archivos si hay operaciones concurrentes durante el backup.

**Causa:** No hay mecanismo para pausar el backend o las escrituras durante el backup. El restore no revierte uploads junto con la base ante un fallo del backend.

**Solución aplicada (2026-10-04):** `scripts/backup_postgres.sh` ahora detiene el backend (`BACKUP_WRITER_MODE=stop-backend`, único modo soportado), genera dump+uploads+sha256 y reanuda el backend por trap. `scripts/restore_postgres.sh` valida checksum, restaura en base temporal y volumen de staging, intercambia DB primero y luego uploads, y revierte ambos conjuntamente ante fallo de uploads o de healthcheck del backend. `VALIDATE_ONLY=true` permite validar sin Docker. CI (`infrastructure.yml`, job `shell-scripts`) ejecuta bash -n, shellcheck y fixture VALIDATE_ONLY.

---

### ISSUE-015 — Docker Compose local no responde en 120 segundos

**Estado:** DOCUMENTADO

**Síntoma:** Al intentar verificar Docker localmente durante la generación de scripts, el comando `docker compose -f docker-compose.prod.yml version` no respondió dentro de 120 segundos.

**Causa:** Docker Desktop no estaba ejecutándose o el demonio Docker no respondía. Los scripts requieren Docker funcionando en el servidor para ejecutarse.

**Solución:** Los scripts de backup/restore deben ejecutarse directamente en el servidor Oracle Cloud, no localmente. La guía documenta cómo copiar el paquete al servidor y ejecutarlo allí.

---

### ISSUE-016 — Soft delete + UniqueConstraint bloqueaba recrear cabecera Plan Anual

**Estado:** RESUELTO

**Síntoma:** Al eliminar una cabecera del Plan Anual (soft delete `activo=False`) y luego intentar crear una nueva con la misma vigencia (ej. 2028), el backend devolvía error de llave duplicada por `UniqueConstraint(empresa_id, vigencia)`.

**Causa:** Soft delete mantiene la fila en BD ocupando la llave única de negocio. Re-crear la misma vigencia colisiona.

**Solución:** El DELETE de cabecera ahora es hard delete (`/cabecera/{cabecera_id}`) con cascade de las actividades `plan_anual_sst` relacionadas, permitiendo recrear cualquier vigencia.

---

### ISSUE-017 — Rutas FastAPI paramétricas capturaban rutas específicas de actividades

**Estado:** RESUELTO

**Síntoma:** Al cargar actividades del Plan Anual, el frontend mostraba "Cabecera del Plan Anual no encontrada" (404). `/cabecera/1/actividades/` devolvía 404.

**Causa:** `GET /cabecera/{empresa_id}/{vigencia}` estaba definida ANTES que `GET /cabecera/{cabecera_id}/actividades/`. FastAPI matcheaba `/cabecera/1/actividades/` contra la primera (empresa_id=1, vigencia="actividades").

**Solución:** Reordenadas las rutas en `plan_anual.py`: rutas de actividades ANTES que la ruta de búsqueda por empresa/vigencia. Además, `/cabecera/{id}/completo` fue renombrada a `/detalle/{cabecera_id}` porque colisionaba (mismo # de segmentos paramétricos).

---

### ISSUE-018 — Tabla plan_anual_cabecera creada manualmente (sin migración Alembic)

**Estado:** RESUELTO

**Síntoma:** Al abrir Plan Anual, el backend devolvía 500 DATABASE_ERROR porque la tabla `plan_anual_cabecera` no existía y `plan_anual_sst` no tenía la columna `plan_anual_cabecera_id`.

**Causa:** El módulo Plan Anual con cabeceras fue implementado y registrado en models/main.py pero las migraciones Alembic no se generaron/aplicaron (alembic upgrade falló antes por error de permisos no relacionado).

**Solución (temporal):** Creada la tabla `plan_anual_cabecera` directamente en PostgreSQL y añadida la columna FK `plan_anual_cabecera_id` a `plan_anual_sst`. `create_all()` no agrega columnas a tablas existentes.

**Solución definitiva:** La migración `h8i9j0k1l2m3` crea `plan_anual_cabecera`, agrega la FK y migra datos. La cadena local fue aplicada hasta `l4m5n6o7p8q9 (head)` el 2026-09-18.

---

### ISSUE-021 — Ficha técnica EPP abría el dashboard o era bloqueada en iframe

**Estado:** RESUELTO

**Síntoma:** La ficha técnica cargada se visualizaba como el Dashboard Ejecutivo; tras corregir la URL, el navegador bloqueaba el iframe por CSP.

**Causa:** `EPPPage.jsx` usaba directamente `/uploads/epp/...`, por lo que Vite devolvía el SPA. Al resolver a `/archivos-protegidos/...`, `frame-ancestors 'self'` bloqueaba el origen frontend en otro puerto.

**Solución:** Aplicar `resolveFileUrl()` al iframe y enlace de descarga. `SecurityHeadersMiddleware` construye `frame-ancestors` con `'self'` y `settings.CORS_ORIGINS`.

---

### ISSUE-022 — Profesiograma sin aislamiento tenant y generador clínico incompatible

**Estado:** RESUELTO

**Síntoma:** El generador desde profesiograma asignaba `APTO`/`VIGENTE` automáticamente sin valoración médica. El frontend no validaba permisos para botones de edición/eliminación. Los códigos de evaluación no mapeaban a enums válidos.

**Causa:** Falta validación `usuario.empresa_id`; `examenes_requeridos` es JSON en texto sin FK; códigos `PRE_INGRESO/PERIODICA/EGRESO/RETORNO` difieren de `INGRESO/PERIODICO/RETIRO/RETORNO_LABORAL`.

**Solución aplicada:**
1. Observaciones del generador ahora incluyen `[GENERADO DESDE PROFESIOGRAMA] Requiere valoración médica ocupacional`.
2. `MAPEO_TIPO_EVALUACION` convierte códigos legacy a enums válidos (`PRE_INGRESO→INGRESO`, `PERIODICA→PERIODICO`, `EGRESO→RETIRO`, `RETORNO→RETORNO_LABORAL`).
3. Frontend: botones Editar/Evidencias/Eliminar condicionados por rol.
4. Validación `fecha_vencimiento >= fecha_examen` agregada a schemas.
5. Dashboard ahora calcula métricas reales de empleados activos y cobertura.

**Pendiente:** `examenes_requeridos` sigue como JSON sin FK; revisar normalización futura.

---

### ISSUE-023 — Alembic local requiere propietario por ownership mixto

**Estado:** DOCUMENTADO

**Síntoma:** `alembic upgrade head` con `sst_user` falló al crear índices: `debe ser dueño de la tabla auditorias_sst`.

**Causa:** Algunas tablas locales pertenecen a `postgres` y otras al usuario de la aplicación.

**Solución aplicada:** Ejecutar la cadena como propietario PostgreSQL. La migración transaccional fallida se revirtió y luego la cadena avanzó limpiamente hasta `head`.

**Pendiente:** Normalizar ownership de tablas para que las futuras migraciones puedan ejecutarse con el rol operativo definido.

---

### ISSUE-024 — Smart Delete no validaba tenant ownership para exámenes médicos

**Estado:** RESUELTO

**Síntoma:** Un usuario de empresa 1 podía eliminar exámenes médicos de empresa 2 usando `/integridad/eliminacion/examen_medico/{id}`.

**Causa:** `ejecutar_eliminacion_inteligente()` ejecutaba `execute_smart_delete()` sin validar que el registro pertenece al tenant del usuario. Solo validaba RBAC.

**Solución:** `_validar_tenant_ownership()` agregada antes de `execute_smart_delete()`. Valida `empresa_id` del registro contra `usuario.empresa_id` usando query SQL directa. `SUPER_ADMIN` se excluye de la validación. Entidades cubiertas: `examen_medico`, `epp_catalogo`, `epp_entrega`, `inspeccion`, `capa`, `incidente`, `comite`.

---

### ISSUE-025 — Evidencias médicas podían quedar con empresa_id=NULL

**Estado:** RESUELTO

**Síntoma:** Cuando `SUPER_ADMIN` subía evidencia sin enviar `empresa_id`, el archivo se guardaba con `empresa_id=NULL`.

**Causa:** `subir_evidencia_examen_medico()` usaba `tenant_id` del parámetro de autorización, que podía ser `None` para `SUPER_ADMIN`.

**Solución:** Ahora obtiene `empresa_id` del empleado asociado al examen (`examen.empleado.empresa_id`), garantizando que siempre tenga un valor válido.

---

### ISSUE-026 — Profesiograma: ROLES_SST incompleto y códigos de evaluación no mapeados

**Estado:** RESUELTO

**Síntoma:** `profesiograma.py` solo aceptaba `SUPER_ADMIN/ADMIN_EMPRESA/RESPONSABLE_SST`. El generador de exámenes usaba `tipo_eval.codigo` directamente (ej: `PRE_INGRESO`) que no es un enum válido de exámenes médicos.

**Solución:**
1. `ROLES_SST` en `profesiograma.py` ampliado con `COORDINADOR_SST`, `TECNICO_SST`, `TALENTO_HUMANO`, `MEDICO_OCUPACIONAL`.
2. `MAPEO_TIPO_EVALUACION` en `examenes_medicos.py` convierte códigos legacy a enums válidos.
3. Dashboard ahora envía `por_area`, `tendencia_mensual`, `vencimientos_mensuales` al frontend.

---

### ISSUE-027 — Smart Delete: endpoint de validación no validaba tenant

**Estado:** RESUELTO

**Síntoma:** `GET /integridad/eliminacion/{entidad}/{id}` devolvía información de dependencias de registros de otros tenants para `SUPER_ADMIN` sin empresa asignada.

**Solución:** `_validar_tenant_ownership()` ahora se ejecuta tanto en `validar_eliminacion` (GET) como en `ejecutar_eliminacion_inteligente` (DELETE).
