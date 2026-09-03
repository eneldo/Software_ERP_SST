# Última sesión

Fecha: 2026-09-03

## Trabajo más reciente — Módulo Política SST: Divulgación COPASST + Acta

- **Backend**: Modelo `PoliticaSST` + campos `divulgada_copasst`, `tiene_acta_divulgacion` (Boolean, default=False). Schemas actualizados (Create/Update/Response). Migración Alembic `97753b8ecb11` aplicada.
- **Frontend `PoliticaSSTPage.jsx`**: 
  - Columnas "Acciones" condicionales solo si `estado === "APROBADA"`
  - Botón 👥 **Divulgada al COPASST** (Users icon) + botón 📋 **Acta de divulgación** (ClipboardCheck icon)
  - Modales de confirmación inline (render condicional en JSX, no early return)
  - Handlers: `abrirModalDivulgada`, `confirmarToggleDivulgada`, `abrirModalActa`, `confirmarToggleActa`
  - `dangerouslySetInnerHTML` para HTML en párrafos de modal
- **CSS `politica-sst.css`**: 
  - `.modal-overlay`, `.modal-card`, `.modal-actions` (animación fadeIn/slideUp)
  - `.table-actions button.active` azul (COPASST) / verde (acta) via `[title*="acta"]`
- **Pruebas manuales**: Toggle on/off funciona en ambos (API PUT parcial con `exclude_unset=True` ya soportado)

## Anterior — Perfil Sociodemográfico Empleado (2026-09-02)

- **Tabla `empleado_perfil_sociodemografico`**: modelo con 65+ columnas organizadas en 7 secciones del PDF "Encuesta Integral de Perfil Sociodemográfico, Salud y Actualización de Hoja de Vida" (Ley 1581 de 2012).
- **Migración `0003_perfil_sociodemo`**: crea la tabla con JSON para `hijos` y `servicios_vivienda`, constraint único `empleado_id`, relaciones FK a `empresas` y `empleados` con CASCADE.
- **Router `empleados_perfil.py`**: CRUD completo (`GET/POST/PUT/DELETE` por empleado, lista masiva filtrable, exportación Excel con headers azules y formato profesional).
- **Schemas `empleado_perfil_schema.py`**: `Create`, `Update`, `Response` + `HijoInfo` para hijos anidados como lista de objetos JSON.
- **Frontend API `empleadoPerfilApi.js`**: cliente con funciones para CRUD + export Excel.
- **Pestaña "Demográfico" rediseñada** en `EmpleadosSSTPage.jsx`:
  - 7 sub-pestañas: Identificación, Sociodemográficas, Vivienda, Laboral, Salud, Referencias, Consentimiento.
  - Aviso Ley 1581 de 2012 de protección de datos.
  - Sección de hijos dinámica (agregar/eliminar filas).
  - Checkboxes de servicios de vivienda.
  - Sección de tallas para dotación.
  - Consentimiento informado con checkbox y fecha.
  - Botón guardar/actualizar con feedback visual.
  - Auto-carga del perfil al abrir modal de edición.
- **CSS `empleados-sst.css`**: estilos completos para `.emp-perfil-*` con responsive.
- **Registro en `main.py`**: modelo `EmpleadoPerfilSociodemografico` y router `empleados_perfil`.
- **Columnas demográficas básicas** en tabla `empleados` (migration `0002`): `genero`, `grupo_etnico`, `discapacidad`, `rango_edad`, `nivel_escolaridad`, `estado_civil`, `tipo_sangre` — se mantienen para acceso rápido pero el formulario completo usa la tabla separada.

## Trabajo anterior — Cargos/EPP y UI

- Módulo Cargos/EPP: asociación persistente muchos-a-muchos mediante `cargo_epp_catalogo`.
- Formulario Cargos conectado al catálogo EPP con selección múltiple.
- Pruebas TDD Cargo-EPP: 20 tests pasando.
- Módulos Áreas, Empleados, EPP: dashboards laterales con toggle.
- Módulo EPP: catálogo como tabla compacta.
- Validación: lint, build, compilación Python, Alembic cabeza única.

## Objetivo trabajado anteriormente
Módulo Cargos: campo riesgos_asociados, toggle sidebar, filtro Estado; Motor de evidencias: compresión PDFs/imágenes en todos los módulos; Rutas de archivos corregidas.

## Cambios realizados

### Backend — Módulo Cargos
1. **`cargo.py` (model)**: Agregado campo `riesgos_asociados = Column(String(700), nullable=True)`
2. **`cargos.py` (router)**: Eliminado `payload.pop("riesgos_asociados")` en `_payload_compatible()` — el campo ya no se descarta

### Frontend — Módulo Cargos
3. **`CargosSSTPage.jsx`**: Agregado `riesgos_asociados` en `construirPayload()` para que se envíe al backend
4. **`CargosSSTPage.jsx`**: Estado `sidebarVisible` + botón toggle en toolbar (Sidebar/LayoutDashboard)
5. **`CargosSSTPage.jsx`**: Botón toggle en header del sidebar (junto a icono BriefcaseBusiness)
6. **`cargos-sst.css`**: Clases `.sidebar-collapsed` (layout 1fr) + `.sidebar-hidden` (animación 0.3s)
7. **`CargosSSTPage.jsx`**: Eliminado filtro "Estado" del grid de filtros

### Backend — Motor de compresión evidencias (todos los módulos)
8. **`upload_service.py`**: Función `_optimizar_pdf_bytes()` con pikepdf (compress_streams, linearize)
9. **`capa.py` / `incidentes.py` / `inspeccion_seguimientos.py` / `medidas_correctivas.py` / `portal_empleado.py`**: Llamada a `_optimizar_pdf_bytes()` en `_guardar_upload()` para PDFs
10. **`archivos_sst.py`**: Agregado `import os` faltante
11. **`inspecciones.py`**: Agregada `_archivo_variant_url()` para corregir NameError

### Frontend — Rutas de archivos
12. **`MatrizLegalPage.jsx` / `MatrizPeligrosPage.jsx` / `PlanAnualPage.jsx` / `PlanMejoramientoPage.jsx`**: `abrirArchivo()` usa `resolveFileUrl()` en lugar de concatenación directa

### Docker / Git
13. **Commit + Push a GitHub**: `bb1eb97`
14. **Docker build**: `sistema_gestion_sst-backend:latest` + `sistema_gestion_sst-frontend:latest` (docker-compose.prod.yml)

## Archivos modificados (sesión 2026-09-03)
- `backend/app/models/politica_sst.py`
- `backend/app/schemas/politica_sst_schema.py`
- `backend/alembic/versions/97753b8ecb11_add_divulgada_copasst_and_tiene_acta_to_politica_sst.py`
- `frontend/src/pages/planear/PoliticaSSTPage.jsx`
- `frontend/src/styles/politica-sst.css`

## Archivos modificados (sesión 2026-09-02)
- `backend/app/models/cargo.py`
- `backend/app/routers/cargos.py`
- `backend/app/routers/inspecciones.py`
- `backend/app/routers/archivos_sst.py`
- `backend/app/services/upload_service.py`
- `backend/app/routers/capa.py`
- `backend/app/routers/incidentes.py`
- `backend/app/routers/inspeccion_seguimientos.py`
- `backend/app/routers/medidas_correctivas.py`
- `backend/app/routers/portal_empleado.py`
- `frontend/src/pages/organizacion/CargosSSTPage.jsx`
- `frontend/src/styles/cargos-sst.css`
- `frontend/src/pages/planear/MatrizLegalPage.jsx`
- `frontend/src/pages/planear/MatrizPeligrosPage.jsx`
- `frontend/src/pages/planear/PlanAnualPage.jsx`
- `frontend/src/pages/planear/PlanMejoramientoPage.jsx`

## Estado actual
- Backend local: `http://127.0.0.1:8000` (--reload, AUTO_CREATE_TABLES=true)
- Frontend local: `http://127.0.0.1:5173`
- BD local: PostgreSQL `vaner_asset_postgres` en `localhost:5432` (BD `sst_erp`, user `sst_user`)
- GitHub: push completado (`bb1eb97`)
- Docker images: `sistema_gestion_sst-backend:latest`, `sistema_gestion_sst-frontend:latest` (docker-compose.prod.yml)
- Prod compose: falla por credenciales BD mismatch (se usará solo local por ahora)

## Próximos pasos
- Testear módulos completos en local
- Cuando todo validado → ajustar credenciales prod + deploy
