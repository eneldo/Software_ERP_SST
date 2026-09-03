# Problemas Conocidos

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
