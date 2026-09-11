# Última sesión

Fecha: 2026-09-11

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

## Próximos pasos

- P2: evaluación Kirkpatrick, validaciones fechas/enums, índices BD
- P3: QR certificados, plantillas PDF, firma pAdES
- **Informe Gestión:** PDF/Excel export, dashboard completo, alertas automáticas
- **Migraciones:** Crear migración unificada para todas las columnas agregadas manualmente
