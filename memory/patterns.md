# Patrones Reutilizables

Registrar patrones técnicos verificados.

---

## Toggle Booleanos en Tabla Histórica (Política SST, Cargos, etc.)

### Backend
1. **Modelo:** Agregar `Column(Boolean, default=False)` al modelo SQLAlchemy
2. **Schemas:** Campo opcional en `Create` (`bool = False`), `Update` (`Optional[bool] = None`), obligatorio en `Response` (`bool`)
3. **Router:** **No tocar** — `PUT` con `exclude_unset=True` ya soporta actualización parcial de un solo campo
4. **Migración:** `op.add_column('tabla', sa.Column('campo', sa.Boolean(), nullable=False, server_default=sa.false()))`

### Frontend
1. **Botones condicionales:** Solo visible si estado permitido (ej: `p.estado === "APROBADA"`)
2. **Iconos diferenciados:** `Users` (COPASST), `ClipboardCheck` (acta), etc.
3. **Modal confirmación inline:** Render condicional en JSX (`{modal.open && <Modal />}`) — **nunca early return**
4. **Handlers:**
   - `abrirModalX(p)`: set state `{open: true, politica: p, accion: p.campo ? "quitar" : "poner"}`
   - `confirmarToggleX()`: `await api.put(url, { campo: accion === "poner" })` + `cargarDatos()`
5. **CSS:**
   - `.table-actions button.active` estilo base
   - Diferenciar por `title`: `[title*="acta"]` → verde, resto → azul

### Prueba manual
- Toggle on → off → on
- Solo visible en estado correcto
- Modal con HTML en párrafo (`dangerouslySetInnerHTML`)

---

## Modal Confirmación Inline (Patrón React)

**Problema:** Early return `if (modal.open) return <Modal />` rompe renderizado de múltiples modales.

**Solución:** Render condicional dentro del JSX principal:
```jsx
return (
  <AdminLayout>
    ...
    {modalDivulgada.open && (
      <div className="modal-overlay" onClick={() => setModalDivulgada({ open: false, ... })}>
        <div className="modal-card" onClick={e => e.stopPropagation()}>
          <h3>...</h3>
          <p dangerouslySetInnerHTML={{ __html: ... }} />
          <div className="modal-actions">
            <button className="btn-secondary" onClick={close}>Cancelar</button>
            <button className="btn-primary" onClick={confirm}>Confirmar</button>
          </div>
        </div>
      </div>
    )}
    {modalActa.open && ( ... )}
  </AdminLayout>
);
```

---

## Interlineado PDF (ReportLab / CSS Print)

### CSS @media print
- Selector con **mayor especificidad**: `.print-header-pro .print-company p` (2 clases + 1 elemento)
- Forzar con `!important`: `line-height: 1.0; margin: 0; padding: 0; text-align: left; white-space: normal;`

### ReportLab
- `ParagraphStyle(..., leading=valor)` donde `leading = font_size * line_height_deseado`
- Para title compacto: `font_size` reducido + `white-space: nowrap` en CSS

---

## File Input Oculto — Patrón SR-Only (Accesible)

**NO usar:** `display: none` (bloquea `.click()` en algunos navegadores)
**NO usar:** `opacity: 0; pointer-events: none` (causa loop infinito file choosers)

**SÍ usar — Patrón SR-Only estándar:**
```css
.hidden-file-input-sst {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```
- Permite `.click()` en todos los navegadores
- Accesible para screen readers
- Sin efectos visuales ni side effects

---

## Axios Interceptor — Content-Type para FormData

```javascript
api.interceptors.request.use((config) => {
  // ... auth headers ...
  if (config.data instanceof FormData) {
    delete config.headers["Content-Type"]; // axios pone boundary correcto
  }
  return config;
});
```
**Regla:** Siempre limpiar `Content-Type` cuando `config.data instanceof FormData`.

---

## Motor de Evidencias — Arquitectura completa

### Flujo de upload
1. Frontend envía archivo a endpoint del módulo (ej: `/inspecciones/{id}/evidencias`)
2. Backend valida con `validate_upload()` (extensiones permitidas, tamaño max)
3. Si es imagen → `_optimizar_imagen_bytes()` → WEBP (max 1920x1080, quality 80→50)
4. Si es PDF → `_optimizar_pdf_bytes()` → pikepdf (compress_streams, object_stream, linearize)
5. Archivo guardado en `UPLOAD_ROOT / {modulo}/` (+ subdirectorios `previews/` y `thumbs/` para imágenes)
6. Registro en `ArchivoSST` con `url = /uploads/{modulo}/{filename}`
7. Retorno de `_archivo_to_dict()` con url, preview_url, thumbnail_url

### Flujo de acceso
1. Frontend recibe URL: `/uploads/{modulo}/{filename}`
2. `resolveFileUrl(url)` convierte → `http://localhost:8000/archivos-protegidos/{modulo}/{filename}`
3. Browser solicita `/archivos-protegidos/{relative_path}`
4. `archivos_protegidos.py` resuelve: `Path(settings.UPLOAD_DIR) / relative_path`
5. Retorna `FileResponse` con Content-Disposition inline

### Caché de variantes
- **Original:** `UPLOAD_ROOT / {modulo} / {filename}.webp`
- **Preview:** `UPLOAD_ROOT / {modulo} / previews / {filename}.webp` (inspecciones) o `{uid}_preview.webp` (capa)
- **Thumb:** `UPLOAD_ROOT / {modulo} / thumbs / {filename}.webp` (inspecciones) o `{uid}_thumb.webp` (capa)

### Módulos y su método de upload
| Módulo | Servicio | Imágenes | PDFs |
|---|---|---|---|
| capacitaciones | upload_service.py (centralizado) | ✅ WEBP | ✅ pikepdf |
| evaluacion_inicial | upload_service.py (centralizado) | ✅ WEBP | ✅ pikepdf |
| matriz_legal | upload_service.py (centralizado) | ✅ WEBP | ✅ pikepdf |
| matriz_peligros | upload_service.py (centralizado) | ✅ WEBP | ✅ pikepdf |
| plan_anual | upload_service.py (centralizado) | ✅ WEBP | ✅ pikepdf |
| capa | _guardar_upload local | ✅ WEBP 1920x1080 | ✅ pikepdf |
| incidentes | _guardar_upload local | ✅ WEBP | ✅ pikepdf |
| inspecciones | _guardar_upload local | ✅ WEBP 1920x1080 | ✅ pikepdf |
| inspeccion_seguimientos | _guardar_upload local | ✅ WEBP | ✅ pikepdf |
| medidas_correctivas | _guardar_upload local | ✅ WEBP 1920x1080 | ✅ pikepdf |
| portal_empleado | _guardar_upload local | ✅ WEBP | ✅ pikepdf |

---

## Patrón: resolveFileUrl en Frontend

**Regla:** NUNCA usar `${API_URL}${url}` para archivos. SIEMPRE usar `resolveFileUrl(url)`.

```javascript
// MAL
window.open(`${API_URL}${item.archivo_url}`, "_blank");
<a href={`${API_URL}${item.archivo_url}`}>

// BIEN
import { resolveFileUrl } from "../../utils/fileUrl";
window.open(resolveFileUrl(item.archivo_url), "_blank");
<a href={resolveFileUrl(item.archivo_url)}>
<img src={resolveFileUrl(ev.url)} />
```

**Ubicación:** `frontend/src/utils/fileUrl.js`

---

## Módulo Matriz IPER (GTC45)

### Columna `nivel_riesgo` (romano)
- **Tipo:** `Column(String(10), nullable=True)`
- **Valores:** "I", "II", "III", "IV"
- **Mapeo:**
  - I: NR ≥ 600 (No Aceptable)
  - II: 150 ≤ NR < 600 (No Aceptable / Control Específico)
  - III: 40 ≤ NR < 150 (Aceptable Mejorable)
  - IV: NR < 40 (Aceptable)

### Cálculo automático en backend
- **Función:** `_calcular_campos_riesgo(item)` en `matriz_iper.py`
- **Campos calculados:** np, nr, interpretacion_np, interpretacion_nr, nivel_riesgo, aceptabilidad
- **Trigger:** Se ejecuta en crear, actualizar y recalcular

### KPIs en frontend
- Total peligros, por interpretación NP, por nivel de riesgo (I-IV), por aceptabilidad

### Exportación Excel
- **Plantilla:** `Modelo_Matriz IPER 2026.xlsx`
- **Hojas:** ADMINISTRATIVA y OPERATIVO
- **Función:** `exportar_excel_iper` con openpyxl directo
