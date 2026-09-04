# Última sesión

Fecha: 2026-09-03

## Trabajo más reciente — Módulo EPP: Ficha Técnica PDF + Módulo Plan Anual: Decreto 1072/2015 + Toggle Panel

### EPP — Ficha Técnica PDF
- **Backend `epp.py` (model)**: Agregado 3 columnas a `EPPCatalogo`: `ficha_tecnica_url` (VARCHAR 500), `ficha_tecnica_nombre` (VARCHAR 255), `ficha_tecnica_archivo_id` (FK → archivos_sst, SET NULL)
- **Backend `epp.py` (router)**: 
  - `POST /epp/catalogo/{id}/ficha-tecnica` — upload PDF con compresión pikepdf vía `_guardar_archivo_epp_upload()`
  - `DELETE /epp/catalogo/{id}/ficha-tecnica` — eliminar ficha técnica + desactivar archivo_sst
  - Almacena en `archivos_sst` con `tipo="FICHA_TECNICA"`, `modulo="EPP"`, `referencia_id=catalogo.id`
- **Backend `epp_schema.py`**: Agregado `ficha_tecnica_url`, `ficha_tecnica_nombre`, `ficha_tecnica_archivo_id` a `EPPCatalogoResponse`
- **Frontend `eppApi.js`**: Nuevas funciones `subirFichaTecnicaEPP(id, formData)` y `eliminarFichaTecnicaEPP(id)`
- **Frontend `EPPPage.jsx`**:
  - Estado `fichaTecnicaFile`, `fichaTecnicaPreview`, `fichaTecnicaModal`
  - Formulario catálogo: sección "Ficha Técnica (PDF)" con file picker, preview nombre, botones Ver/Eliminar si ya existe
  - `guardarCatalogo()`: si hay archivo seleccionado, sube después de crear/actualizar el catálogo
  - Tabla catálogo: botón `FileText` siempre visible en columna Acciones
  - Modal ficha técnica: iframe para PDF + botón Descargar, o mensaje "No cuenta con ficha técnica" si no hay PDF
- **CSS `epp-sst.css`**: Estilos `.epp-ficha-*` (upload, existing, btn, modal, iframe, empty state)

### Plan Anual — Decreto 1072 de 2015
- **Backend `plan_anual.py` (model)**: 7 columnas nuevas: `alcance`, `objetivo_general`, `vigencia`, `representante_legal_nombre`, `representante_legal_cargo`, `responsable_sst_nombre`, `responsable_sst_cargo`
- **Backend `plan_anual.py` (schemas)**: Campos agregados a Create, Update, Response
- **Backend `plan_anual.py` (router)**: `serializar()` retorna los 7 campos nuevos
- **Backend `exportaciones_sst.py`**: PDF exporta vigencia, alcance, objetivo general en header + firmas con nombres/cargos reales
- **Backend `export_pdf_service.py`**: Parámetros opcionales `encabezado_extra`, `firma_representante`, `firma_responsable` en `generar_pdf_corporativo()`
- **Frontend `PlanAnualPage.jsx`**: 
  - Estado `sidebarVisible` + botón toggle en hero + en header del panel
  - Sección "Información del Plan" (vigencia, alcance, objetivo_general)
  - Sección "Firmas" (Rep. Legal + Responsable SST con nombre/cargo)
  - CSS: `.pa-panel-collapsed`, `.pa-panel-hidden`, `.pa-toggle-sidebar`, `.pa-sidebar-toggle-btn`
- **DB**: 7 columnas agregadas via ALTER TABLE (no Alembic, `create_all` no agrega columnas a tablas existentes)

### Toggle Panel en Plan Anual
- Patrón identical a PoliticaSSTPage: estado `sidebarVisible`, botón en hero + en header del panel, clases CSS `pa-panel-collapsed` y `pa-panel-hidden`

## Archivos modificados (esta sesión)

### EPP Ficha Técnica
- `backend/app/models/epp.py` — 3 columnas nuevas
- `backend/app/schemas/epp_schema.py` — campos en Response
- `backend/app/routers/epp.py` — 2 endpoints nuevos (upload/delete ficha)
- `frontend/src/api/eppApi.js` — 2 funciones nuevas
- `frontend/src/pages/hacer/EPPPage.jsx` — upload form, view modal, actions
- `frontend/src/styles/epp-sst.css` — estilos ficha técnica

### Plan Anual Decreto 1072
- `backend/app/models/plan_anual.py` — 7 columnas nuevas
- `backend/app/schemas/plan_anual.py` — campos en schemas
- `backend/app/routers/plan_anual.py` — serializar() actualizado
- `backend/app/routers/exportaciones_sst.py` — PDF con nuevos campos
- `backend/app/services/export_pdf_service.py` — parámetros opcionales
- `frontend/src/pages/planear/PlanAnualPage.jsx` — form + toggle panel
- `frontend/src/styles/plan-anual.css` — estilos secciones + toggle

### Anterior — Módulo Política SST (2026-09-03)
- `backend/app/models/politica_sst.py`
- `backend/app/schemas/politica_sst_schema.py`
- `backend/alembic/versions/97753b8ecb11_add_divulgada_copasst_and_tiene_acta_to_politica_sst.py`
- `frontend/src/pages/planear/PoliticaSSTPage.jsx`
- `frontend/src/styles/politica-sst.css`

## Estado actual
- Backend local: `http://127.0.0.1:8000` (--reload, AUTO_CREATE_TABLES=true)
- Frontend local: `http://127.0.0.1:5173`
- BD local: PostgreSQL en `localhost:5432` (BD `sst_erp`, user `sst_user`, password `Sst_ERP_2026*`)
- GitHub: push pendiente
- DB columns: epp_catalogo tiene 17 columnas (3 nuevas ficha técnica), plan_anual_sst tiene 29 columnas (7 nuevas Decreto 1072)

## Próximos pasos
- Testear módulo EPP ficha técnica completa (upload → view → delete)
- Testear Plan Anual con campos Decreto 1072 (crear → persistir → exportar PDF)
- Cuando todo validado → commit + push
