# Soluciones Verificadas

Soluciones técnicas reutilizables comprobadas.

---

## Solución: NameError por función no definida en router

**Problema:** `_archivo_variant_url` se usaba en `_archivo_to_dict()` pero no estaba definida en `inspecciones.py`.

**Solución:** Agregar la función directamente en el router con la lógica correcta para subdirectorios:

```python
def _archivo_variant_url(archivo: ArchivoSST, suffix: str) -> str | None:
    if not archivo.nombre_archivo or not str(archivo.mime_type or "").startswith("image/"):
        return None
    stem = Path(archivo.nombre_archivo).stem
    if suffix == "preview":
        variant = INSPECCIONES_PREVIEW_DIR / f"{stem}.webp"
    elif suffix == "thumb":
        variant = INSPECCIONES_THUMB_DIR / f"{stem}.webp"
    else:
        return None
    if variant.exists():
        return _public_upload_url(variant)
    return None
```

**Nota:** Diferentes módulos guardan variantes en ubicaciones distintas:
- `capa.py`: `{uid}_preview.webp` (mismo directorio)
- `inspecciones.py`: `previews/{uid}.webp` (subdirectorio)

---

## Solución: Frontend no puede acceder archivos /uploads/

**Problema:** `${API_URL}${url}` genera `http://localhost:8000/uploads/...` pero no existe ruta `/uploads/` en FastAPI.

**Solución:** Usar `resolveFileUrl(url)` de `fileUrl.js`:

```javascript
import { resolveFileUrl } from "../../utils/fileUrl";

// Para abrir en nueva pestaña
window.open(resolveFileUrl(item.archivo_url), "_blank");

// Para enlace de descarga
<a href={resolveFileUrl(item.archivo_url)}>

// Para imagen
<img src={resolveFileUrl(ev.url)} />
```

---

## Solución: PDFs sin comprimir en upload_service.py

**Problema:** `guardar_documento_sin_comprimir()` guardaba PDFs sin optimizar.

**Solución:** Agregar `_optimizar_pdf_bytes()` y llamarla antes de escribir:

```python
def _optimizar_pdf_bytes(content: bytes) -> bytes:
    try:
        import pikepdf
        src = io.BytesIO(content)
        out = io.BytesIO()
        with pikepdf.Pdf.open(src) as pdf:
            pdf.save(out, compress_streams=True,
                     object_stream_mode=pikepdf.ObjectStreamMode.generate,
                     linearize=True)
        optimized = out.getvalue()
        return optimized if len(optimized) < len(content) else content
    except Exception:
        return content

def guardar_documento_sin_comprimir(...):
    ...
    content = validado.content
    if extension == ".pdf":
        content = _optimizar_pdf_bytes(content)
    ruta.write_bytes(content)
```

---

## Solución: Conflicto de rutas PUT en FastAPI

**Problema:** `PUT /recalcular/{empresa_id}` lanzaba 422 porque FastAPI lo interpretaba como `PUT /{item_id}`.

**Solución:** Declarar endpoints específicos ANTES de endpoints genéricos del mismo método HTTP.

---

## Solución: Calcular y almacenar valores derivados en BD

**Problema:** Los valores np, nr, nivel_riesgo se calculaban en el frontend, causando inconsistencias.

**Solución:** Calcular en el backend y almacenar en la BD:

```python
def _calcular_campos_riesgo(item):
    item.np = (item.nd or 0) * (item.ne or 0)
    item.nr = item.np * (item.nc or 0)
    item.nivel_riesgo = _nivel_riesgo_romano(item.nr)
```

---

## Solución: KPIs con conteo por categoría

**Problema:** Los KPIs mostraban solo el total, sin desglose por categorías de riesgo.

**Solución:** Agrupar items por cada campo y contar:

```javascript
const riskCounts = {};
items.forEach(item => {
  const key = item.nivel_riesgo || '-';
  riskCounts[key] = (riskCounts[key] || 0) + 1;
});
```
