# Última sesión

Fecha: 2026-09-03

## Trabajo más reciente — Módulo Profesiograma/Exámenes Médicos (Resolución 1843/2025) + EPP Multi-entrega + Plan Anual mejoras

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
- BD local: PostgreSQL en `localhost:5432` (BD `sst_erp`, user `sst_user`, password `Sst_ERP_2026*`)
- GitHub: **pushed to main** (commit 29d2dd7)
- Docker: pendiente (requiere Docker Desktop corriendo)
- DB: tablas profesiograma* creadas + cargo.requiere_vigilancia_medica + seed data

## Próximos pasos
- Ejecutar `docker-compose build backend` + `docker-compose up -d` (con Docker Desktop)
- Testear flujo completo: Cargo → Profesiograma → Empleado cambio cargo → Exámenes auto-generados → Historial
