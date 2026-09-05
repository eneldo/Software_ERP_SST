# Última sesión

Fecha: 2026-09-05 (actualización post-commit)

## Commit más reciente

`f3fc5a6` — feat: auditoría integral SG-SST — módulos, seguridad, tests TDD, migraciones

137 archivos, 8366 insertiones, 313 eliminaciones.

## Estado actual

- **Tests:** 85/85 GREEN
- **Backend:** compilación OK, `git diff --check` OK
- **Migraciones:** 14 nuevas (20260904_0001 a 20260904_0014)
- **Branch:** main, pushed

## Hallazgos P0 — Estado

| ID | Hallazgo | Estado |
|---|---|---|
| H-001 | Historia clínica permisos | RESUELTO |
| H-002 | CAPA schema↔modelo | RESUELTO |
| H-003/4/5 | Tenant EPP/Inspecciones/Exámenes | RESUELTO |
| H-006 | Baseline vs migraciones | RESUELTO |
| H-007 | Criterios Res.0312 | PARCIAL (falta seed) |
| H-008 | Exportaciones ownership | PARCIAL |
| H-009 | Políticas obligatorias | **ABIERTO** |
| H-010 | Archivos tenant/hash | PARCIAL |
| H-011 | Psicosocial + HCO | PARCIAL |
| H-012 | Dashboard datos reales | PARCIAL |
| H-013 | RBAC/MFA/tokens | PARCIAL |
| H-021b/c/d/e | Exportaciones tenant | PARCIAL |
| H-022/23 | Cierre plan + origen | PARCIAL |
| H-024/25 | Notificaciones/Planes tenant | PARCIAL |

## Hallazgos P1 — Estado

| ID | Hallazgo | Estado |
|---|---|---|
| H-014 | Plan anual capacitación/inducción | **ABIERTO** |
| H-015 | Plan Anual tenant/dashboard | PARCIAL |
| H-016 | Indicadores fórmulas oficiales | **ABIERTO** |
| H-017 | Estándares plan mejora + RBAC | **ABIERTO** |
| H-018 | Matriz legal exportaciones/alertas | **ABIERTO** |
| H-019 | Planes mejora origen/verificación | **ABIERTO** |
| H-020 | Alertas 11 dominios + canales | **ABIERTO** |

## Trabajo previo — Auditoría P0 CAPA, Incidentes, IPER y migraciones

- CAPA/Medidas Correctivas quedó alineado entre schemas, modelos y base de datos:
  - `ishikawa_json`, costos, aprobación y fecha de aprobación.
  - `proxima_accion` y `fecha_proximo_seguimiento` en seguimientos.
  - Migración `e1f2a3b4c5d6` aplicada; base local en `head`.
- Incidentes valida el recurso padre y su empresa antes de listar o modificar lesionados, testigos y evidencias.
- IPER aplica aislamiento tenant a CRUD, lotes, dashboard, recálculo y exportaciones.
- IPER conserva `nd`, `ne` y `nc` persistidos durante actualizaciones parciales y valida lotes mediante Pydantic para evitar asignación masiva.
- Las rutas dinámicas IPER usan convertidor entero y ya no capturan `/lote` ni `/exportar/*`.
- Las migraciones aditivas posteriores al baseline dinámico incorporan guardas de tablas, columnas y tipos.
- Se validó una instalación Alembic completa sobre una base temporal nueva hasta `e1f2a3b4c5d6`; la base temporal fue eliminada.
- Pruebas backend: 13/13 OK. Compilación Python y `git diff --check`: OK.
- La propiedad de `capas_sst` y `capas_seguimientos_sst` se transfirió de `postgres` a `sst_user` para que Alembic pueda administrar el esquema.

## Trabajo más reciente — Auditoría P0 EPP, Inspecciones y Evaluaciones Médicas (Bloque 2)

- **EPP SST Enterprise** (`backend/app/routers/epp.py`): aislamiento tenant en 27 endpoints:
  - Catálogo CRUD, ficha técnica, entregas CRUD + lote, consolidado, evidencias, firma, dashboard, exportaciones.
  - Helper `_empresa_id_autorizada` + validación en `_query_entregas`, `_validar_*`, listados y mutaciones.
  - Exportaciones de reposiciones, firmas pendientes y ficha individual ahora filtran por tenant.
- **Inspecciones y Seguimientos** (`backend/app/routers/inspecciones.py`, `inspeccion_seguimientos.py`): aislamiento tenant en ~35 endpoints:
  - Listados, dashboard, CRUD inspecciones, hallazgos, firmas, cierre digital, anulación, exportaciones.
  - Hallazgos y seguimientos validan cadena completa `Inspección → Hallazgo → Seguimiento` por tenant.
  - Evidencias validan inspección padre + `ArchivoSST.empresa_id` antes de listar/subir/eliminar.
  - Exportaciones (Excel, PDF general, hallazgos, seguimientos, dashboard, acta, individual) requieren tenant.
- **Evaluaciones Médicas** (`backend/app/routers/examenes_medicos.py`): aislamiento tenant + privacidad:
  - `_empresa_id_autorizada` + validación en `_validar_empleado`, `_query_examenes_filtrada`.
  - Listados, dashboard, exportaciones (Excel, PDF general, vencimientos, restricciones, ficha individual), evidencias, CRUD, generar-desde-profesiograma.
  - Profesiograma filtrado por `empresa_id` del cargo; evita cross-tenant en auto-generación.
- **Migraciones históricas IPER, Política SST, Exámenes Médicos, Historial Legal, Perfil Sociodemográfico, Indicadores** actualizadas con guardas de existencia (`sa.inspect`) para coexistir con baseline dinámico `create_all()`.
- **Instalación limpia completa validada** en base temporal propietaria de `sst_user` → 21 migraciones hasta `e1f2a3b4c5d6 (head)` sin errores; base temporal eliminada tras éxito.
- **Base local en `head`** (`e1f2a3b4c5d6`). `git diff --check`: OK. `python -m compileall`: OK.
- **Suite backend**: 20 tests core pasan (CAPA, Incidentes, IPER, Comités, Emergencias, Organización). Tests de tenant isolation nuevos: 4/4 críticos GREEN (listar_catalogo, crear_entregas_lote, listar_examenes, listar_inspecciones).

### Profesiograma / Evaluaciones Médicas (Resolución 1843/2025)
- **Backend - 4 nuevas tablas** (`profesiograma.py`):
  - `TipoEvaluacionMedica` — catálogo 7 tipos: Pre-Ingreso, Periódica, Por cambio ocupación, Egreso, Post-incapacidad, Retorno, Seguimiento
  - `ExamenEvaluacionCatalogo` — catálogo 13 exámenes: Visiometría, Espirometría, Audiometría, etc.
  - `Profesiograma` — vincula Cargo + Empresa + Riesgos (JSON) + Evaluaciones
  - `ProfesiogramaEvaluacion` — vincula Profesiograma + Tipo Evaluación + Exámenes requeridos (JSON)
- **Backend - Router `profesiograma.py`**: CRUD completo + endpoints catálogos
- **Backend - Endpoint auto-generación** `POST /examenes-medicos/empleado/{id}/generar-desde-profesiograma`:
  - Lee profesiograma del cargo del empleado
  - Crea exámenes por cada tipo de evaluación con exámenes del catálogo
  - Evita duplicados (no crea si existe similar en últimos 30 días)
- **Backend - Cargo**: campo `requiere_vigilancia_medica` BOOLEAN
- **Frontend - `ProfesiogramaPage.jsx`**: gestión catálogos + lista profesiogramas por cargo
- **Frontend - `CargosSSTPage.jsx`**: checkbox "Requiere vigilancia médica" → sección Profesiograma (riesgos checklist + evaluaciones por tipo con exámenes)
- **Frontend - `ExamenesMedicosSSTPage.jsx`**: 
  - "Recomendación médica" (Sin Restricciones / **Con Restricciones Médicas**)
  - Botón historial 🕐 → modal agrupado por tipo evaluación (Resolución 1843)
- **Frontend - `EmpleadosSSTPage.jsx`**: al cambiar cargo del empleado → auto-genera exámenes requeridos
- **DB**: CREATE TABLE 4 tablas + ALTER TABLE cargos + seed data (7 tipos, 13 exámenes)

### EPP — Entrega Múltiple + Consolidado
- **Backend `epp.py` (schemas)**: `EPPEntregaItemLote`, `EPPEntregaLoteCreate`, `EPPEntregaLoteResponse`, `EPPConsolidadoEmpleado`
- **Backend `epp.py` (router)**: 
  - `POST /epp/entregas/lote` — batch create (1 empleado + N EPP + 1 fecha)
  - `GET /epp/entregas/consolidado` — agrupado por empleado
- **Frontend `EPPPage.jsx`**:
  - Botón "Entrega múltiple" + formulario dinámico (agregar/quitar filas EPP)
  - Sub-tabs: "Tabla entregas" / "Consolidado por empleado"
  - Consolidado: tarjetas por empleado con todos sus EPP, badges, metadata
- **CSS `epp-sst.css`**: estilos `.epp-lote-*`, `.epp-consolidado-*`, `.epp-subtabs`

### Plan Anual — Decreto 1072/2015 + Toggle Panel
- 7 columnas nuevas: `alcance`, `objetivo_general`, `vigencia`, `representante_legal_nombre`, `representante_legal_cargo`, `responsable_sst_nombre`, `responsable_sst_cargo`
- PDF exporta vigencia, alcance, objetivo en header + firmas con nombres/cargos reales
- Panel colapsable: estado `sidebarVisible`, botón toggle en hero + header panel
- CSS: `.pa-panel-collapsed`, `.pa-panel-hidden`, `.pa-toggle-sidebar`, `.pa-sidebar-toggle-btn`

### CIIU Autocomplete
- 500 códigos CIIU Rev 4 en `backend/app/data/ciiu_rev4.json`
- Endpoint `GET /ciiu?q=` (búsqueda por código/nombre/descripción)
- Componente `AutocompleteCIIU.jsx` reutilizable

## Archivos nuevos (esta sesión)
- `backend/app/models/profesiograma.py`
- `backend/app/schemas/profesiograma_schema.py`
- `backend/app/routers/profesiograma.py`
- `backend/app/routers/ciiu.py`
- `backend/app/data/ciiu_rev4.json`
- `frontend/src/api/profesiogramaApi.js`
- `frontend/src/pages/hacer/ProfesiogramaPage.jsx`
- `frontend/src/styles/profesiograma.css`
- `frontend/src/components/common/AutocompleteCIIU.jsx`

## Archivos modificados (esta sesión)
- `backend/app/main.py` — registro router profesiograma
- `backend/app/models/cargo.py` — campo requiere_vigilancia_medica
- `backend/app/schemas/cargo_schema.py` — campo en schemas
- `backend/app/routers/cargos.py` — payload/serialización vigilancia médica
- `backend/app/routers/epp.py` — batch delivery + consolidado
- `backend/app/routers/examenes_medicos.py` — endpoint generar-desde-profesiograma
- `backend/app/routers/exportaciones_sst.py` — PDF mejorado
- `backend/app/routers/plan_anual.py` — serializar 7 campos
- `backend/app/services/export_pdf_service.py` — parámetros opcionales
- `backend/app/schemas/epp_schema.py` — schemas lote/consolidado
- `backend/app/schemas/plan_anual.py` — campos 7 nuevos
- `frontend/src/App.jsx` — ruta /hacer/profesiograma
- `frontend/src/layouts/AdminLayout.jsx` — menú Profesiograma
- `frontend/src/api/eppApi.js` — crearEntregaLote, consolidadoEntregas
- `frontend/src/api/examenMedicoSstApi.js` — generarExamenesDesdeProfesiograma
- `frontend/src/api/profesiogramaApi.js` — nuevo
- `frontend/src/pages/hacer/EPPPage.jsx` — multi-entrega + consolidado
- `frontend/src/pages/hacer/ExamenesMedicosSSTPage.jsx` — recomendación médica + historial
- `frontend/src/pages/organizacion/CargosSSTPage.jsx` — checkbox vigilancia + profesiograma
- `frontend/src/pages/organizacion/EmpleadosSSTPage.jsx` — auto-generar exámenes al cambiar cargo
- `frontend/src/pages/planear/PlanAnualPage.jsx` — 7 campos + toggle panel
- `frontend/src/styles/epp-sst.css` — estilos lote + consolidado
- `frontend/src/styles/examenes-medicos-sst.css` — modal historial
- `frontend/src/styles/plan-anual.css` — secciones + toggle
- `frontend/src/styles/profesiograma.css` — nuevo
- `frontend/src/styles/cargos-sst.css` — estilos profesiograma en modal

## Estado actual
- Backend local: `http://127.0.0.1:8000` (--reload, AUTO_CREATE_TABLES=true)
- Frontend local: `http://127.0.0.1:5173`
- BD local: PostgreSQL en `localhost:5432` (BD `sst_erp`, usuario de aplicación `sst_user`; credenciales solo en variables de entorno)
- GitHub: **pushed to main** (commit 29d2dd7)
- Docker: pendiente (requiere Docker Desktop corriendo)
- DB: tablas profesiograma* creadas + cargo.requiere_vigilancia_medica + seed data

## Próximos pasos
- Ejecutar `docker-compose build backend` + `docker-compose up -d` (con Docker Desktop)
- Testear flujo completo: Cargo → Profesiograma → Empleado cambio cargo → Exámenes auto-generados → Historial
