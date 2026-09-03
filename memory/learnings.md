# Aprendizajes del Agente

Los aprendizajes más recientes deben agregarse arriba.

Formato:

- **YYYY-MM-DD — Tema:**
  **Contexto:** qué ocurrió.
  **Aprendizaje:** qué se descubrió.
  **Aplicación futura:** cómo aplicar este conocimiento.

---

- **2026-09-03 — Toggle de divulgación COPASST y acta en módulo Política SST:**
  **Contexto:** Usuario pidió agregar dos botones toggle en la tabla histórico (columna Acciones): "Divulgada al COPASST" y "Acta de divulgación", solo para políticas APROBADA, con modal de confirmación.
  **Aprendizaje:** 
  1. Backend: Agregar columnas booleanas `divulgada_copasst` y `tiene_acta_divulgacion` al modelo + schemas + migración Alembic limpia (solo `op.add_column`).
  2. Frontend: Botones condicionales `p.estado === "APROBADA"`. Modales con `dangerouslySetInnerHTML` para HTML en párrafos. Render condicional en JSX (no early return) para que ambos modales convivan.
  3. CSS: Clase `.active` distinta por acción (azul COPASST, verde acta) usando selector `[title*="acta"]`.
  4. El backend `PUT` con `exclude_unset=True` ya soporta actualización parcial sin tocar router.
  5. **Crítico:** Reiniciar backend tras migración para limpiar cache de modelos SQLAlchemy.
  **Aplicación futura:** Para toggles booleanos en tabla histórica: modelo + schema + migración + botones condicionales + modales inline + CSS diferenciado. Probar ciclo completo toggle on/off antes de entregar.

- **2026-09-03 — Early return en modales rompe renderizado condicional:**
  **Contexto:** Usé `if (modal.open) return <Modal />` antes del JSX principal, lo que impedía que el segundo modal se renderizara y rompía el flujo normal.
  **Aprendizaje:** Nunca usar early return para modales. Renderizar condicionalmente dentro del JSX: `{modal.open && <Modal />}`. Esto permite múltiples modales y mantiene el flujo de renderizado React normal.
  **Aplicación futura:** Modales siempre como condicionales en JSX principal, no early returns.

- **2026-09-03 — Interlineado PDF Política SST — Selector CSS specificity:**
  **Contexto:** `.document-card p` (línea 291) sobreescribía `.print-company p` por misma especificidad y orden en CSS.
  **Aprendizaje:** Aumentar especificidad con selector padre: `.print-header-pro .print-company p` (2 clases + 1 elemento). Para print media query, usar misma especificidad y `!important` para forzar `line-height: 1.0`, `margin: 0`, `text-align: left`.
  **Aplicación futura:** Al ajustar estilos en componentes impresos, siempre verificar cascada CSS y aumentar especificidad si hay conflicto.

- **2026-09-03 — Título PDF en una línea — white-space: nowrap + font-size reducido:**
  **Contexto:** Título "POLÍTICA DE SEGURIDAD Y SALUD EN EL TRABAJO – SG-SST" se envolvía en 2 líneas.
  **Aprendizaje:** En `.document-card h4`: reducir `font-size: 22px → 16px` (pantalla) y `18pt → 14pt` (print), agregar `white-space: nowrap`. Funciona para títulos conocidos que deben caber en una línea.
  **Aplicación futura:** Para títulos de documento que deben ser una sola línea: `white-space: nowrap` + font-size ajustado + `text-align: center`.

- **2026-09-02 — Logo upload empresas — Content-Type multipart boundary:**
  **Contexto:** Subida de logo fallaba con 422. El interceptor axios forzaba `Content-Type: application/json` sobreescribiendo el boundary que FormData necesita.
  **Aprendizaje:** En interceptor request, detectar `config.data instanceof FormData` y `delete config.headers["Content-Type"]` para que axios ponga el boundary correcto automáticamente.
  **Aplicación futura:** Siempre limpiar Content-Type en requests con FormData. Patrón reutilizable en axios interceptor.

- **2026-09-02 — File input hidden — sr-only pattern para .click():**
  **Contexto:** `display: none` impedía `.click()` en algunos navegadores. `position: absolute; opacity: 0` causaba loop infinito de file choosers.
  **Aprendizaje:** Usar patrón sr-only estándar: `position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0`. Permite `.click()` y es accesible.
  **Aplicación futura:** Para inputs file ocultos que se disparan por botón, siempre usar patrón sr-only, nunca `display: none` ni `opacity: 0`.

- **2026-09-02 — Tabla separada para perfil extenso vs columnas en tabla principal:**
  **Contexto:** El PDF "Perfil Sociodemográfico" tiene 65+ campos. En lugar de agregar todas las columnas a la tabla `empleados`, se creó una tabla separada `empleado_perfil_sociodemografico` con relación 1:1 (UNIQUE constraint en `empleado_id`).
  **Aprendizaje:** Para formularios extensos (encuestas, perfiles), crear tabla separada con JSON para listas anidadas (hijos, servicios). Las columnas básicas en la tabla principal (genero, estado_civil, etc.) se mantienen para acceso rápido en listados/dashboard, pero el formulario completo usa la tabla separada.
  **Aplicación futura:** Cuando un módulo tenga un formulario tipo encuesta con 30+ campos, crear tabla dedicada. Usar JSON para arrays simples y constraint UNIQUE para relaciones 1:1.

- **2026-09-02 — Longitud máxima de revision_id en Alembic:**
  **Contexto:** La migración `0003_empleado_perfil_sociodemografico` falló porque `version_num` es `VARCHAR(32)` y el ID tenía 41 caracteres.
  **Aprendizaje:** El `revision_id` en Alembic debe ser ≤ 32 caracteres. Usar abreviaciones (`0003_perfil_sociodemo` en lugar de `0003_empleado_perfil_sociodemografico`).
  **Aplicación futura:** Siempre acortar los revision IDs a máximo 28-30 caracteres para margen de seguridad.

- **2026-09-02 — Migraciones con baseline dinámico `create_all`:**
  **Contexto:** La migración inicial crea tablas desde la metadata actual, por lo que una instalación nueva puede crear una tabla añadida recientemente antes de alcanzar su migración explícita.
  **Aprendizaje:** En este proyecto, las migraciones que crean tablas deben consultar `sa.inspect(bind).get_table_names()` y omitir la creación si el baseline dinámico ya la materializó.
  **Aplicación futura:** Incluir guardas simétricas en `upgrade()` y `downgrade()` para toda tabla nueva mientras el baseline inicial siga dependiendo de `Base.metadata.create_all()`.

- **2026-09-01 — Campo en schema pero no en modelo + eliminación en router:**
  **Contexto:** El schema `CargoBase` tenía `riesgos_asociados` y el frontend lo enviaba, pero el modelo `Cargo` no tenía la columna y el router `_payload_compatible()` hacía `payload.pop("riesgos_asociados")` explícitamente.
  **Aprendizaje:** Tres puntos de fallo simultáneos: (1) modelo sin columna, (2) router elimina el campo, (3) frontend no lo incluye en payload builder. Para que un campo funcione end-to-end: modelo + schema + router + frontend payload builder deben alinearse.
  **Aplicación futura:** Checklist para nuevo campo: modelo (columna), schema (campo), router (no pop), frontend (construirPayload), migración BD. Probar CRUD completo antes de declarar listo.

- **2026-09-01 — Toggle sidebar con grid-template-columns dinámico:**
  **Contexto:** El layout usa CSS Grid `grid-template-columns: minmax(0, 1fr) 330px`. Para ocultar sidebar sin romper layout, cambiar a `1fr` y usar clase `.sidebar-hidden` con `opacity/visibility/width=0` para animación suave.
  **Aprendizaje:** CSS Grid permite transiciones suaves de layout cambiando `grid-template-columns` con `transition`. Para ocultar completamente un elemento sidebar sticky, combinar `opacity: 0`, `visibility: hidden`, `width: 0`, `max-height: 0`, `padding: 0` con `transition`.
  **Aplicación futura:** Al hacer toggle de paneles laterales, usar grid + clases CSS en lugar de `display: none` para mantener animaciones fluidas y evitar reflow brusco.

- **2026-09-01 — Múltiples botones toggle para misma acción:**
  **Contexto:** Usuario pidió botón en toolbar Y en header del sidebar. Ambos llaman a `setSidebarVisible(!sidebarVisible)` compartiendo el mismo estado.
  **Aprendizaje:** Colocar controles de toggle donde el usuario los espera naturalmente. Un toggle en toolbar (acción global) + otro en header del panel (acción contextual) mejora UX sin duplicar lógica.
  **Aplicación futura:** Cuando un panel lateral sea importante, poner toggle en la toolbar principal y en el header del panel. Ambos usan el mismo estado React.

- **2026-09-01 — Filtro Estado removido pero KPIs siguen filtrando:**
  **Contexto:** Se quitó el dropdown "Estado" del grid de filtros, pero las KPI cards (Total/Activos) usan `setFiltros({...p, estado: "ACTIVO"})` programático.
  **Aprendizaje:** Mantener `estado` en el estado inicial y en `limpiarFiltros` permite filtrado programático desde UI cards sin exponer dropdown al usuario. El backend sigue aceptando `estado` como query param.
  **Aplicación futura:** Si un filtro es útil para acciones programáticas pero confuso en UI manual, quitar el control visual pero mantener el estado y lógica de filtrado.

- **2026-08-31 — NameError por función no definida en inspecciones.py:**
  **Contexto:** `_archivo_variant_url` se usaba en `_archivo_to_dict()` pero nunca estaba definida ni importada en `inspecciones.py`. Causaba `NameError` cada vez que se subía o listaba evidencia.
  **Aprendizaje:** Las funciones auxiliares usadas dentro de un módulo deben estar definidas en ese mismo módulo o importarse explícitamente. El error solo se manifestaba al ejecutar (no al importar), por lo que pasaría desapercibido en un linting básico.
  **Aplicación futura:** Verificar que todas las funciones helper estén definidas o importadas en cada router. Un grep por `def ` y por uso de funciones auxiliares ayuda a detectar estos problemas.

- **2026-08-31 — Rutas /uploads/ no existen en FastAPI:**
  **Contexto:** El frontend usaba `${API_URL}${url}` directamente (ej: `http://localhost:8000/uploads/matriz-legal/file.webp`), pero FastAPI no tiene ruta registrada para `/uploads/`. Solo existe `/archivos-protegidos/`.
  **Aprendizaje:** NUNCA construir URLs de archivos con `${API_URL}${url}` directamente. Siempre usar `resolveFileUrl(url)` de `fileUrl.js` que convierte `/uploads/` → `/archivos-protegidos/`. La función también maneja rutas absolutas de Windows y rutas relativas.
  **Aplicación futura:** En cualquier componente frontend que muestre o abra evidencias, verificar que use `resolveFileUrl()` y no concatenación directa de URLs.

- **2026-08-31 — Motor de compresión: upload_service.py no comprime PDFs:**
  **Contexto:** El servicio centralizado `upload_service.py` tenía `guardar_documento_sin_comprimir()` que guardaba PDFs tal cual, mientras que `inspecciones.py` tenía `_optimizar_pdf_bytes()` con pikepdf.
  **Aprendizaje:** Cuando se crea un servicio centralizado de uploads, debe manejar TODOS los tipos de archivo (imágenes + PDFs + otros). pikepdf puede reducir PDFs eliminando objetos duplicados, comprimiendo streams y linearizando.
  **Aplicación futura:** Al agregar soporte para nuevos tipos de archivo en el servicio centralizado, verificar que la optimización esté implementada para cada tipo.

- **2026-08-31 — Variantes de imagen en subdirectorios vs sufijos:**
  **Contexto:** `capa.py` guarda variantes con sufijo (`{uid}_preview.webp`, `{uid}_thumb.webp`) en el mismo directorio, mientras que `inspecciones.py` usa subdirectorios (`previews/{uid}.webp`, `thumbs/{uid}.webp`). La función `_archivo_variant_url` debe buscar en la ubicación correcta para cada módulo.
  **Aprendizaje:** No asumir que todos los módulos usan la misma estructura de directorios para variantes. Cada módulo con optimización de imágenes puede tener su propia convención.
  **Aplicación futura:** Al implementar `_archivo_variant_url` en un módulo, verificar primero dónde se guardan las variantes (mismo directorio con sufijo o subdirectorios separados).

- **2026-08-31 — Mapeo de riesgos GTC45 en backend:**
  **Contexto:** Los valores calculados (np, nr, interpretacion, nivel_riesgo) debían guardarse en la BD en lugar de calcularse en el frontend.
  **Aprendizaje:** El modelo `MatrizIPER` necesitaba una columna `nivel_riesgo` (String(10)) para almacenar el número romano. La migración Alembic fue directa porque es solo añadir columna nullable.
  **Aplicación futura:** Cuando un cálculo debe ser consistente entre vistas (lista, dashboard, exportación), almacenar el resultado en la BD en lugar de recalcularlo en cada componente.

- **2026-08-31 — Conflicto de rutas PUT en FastAPI:**
  **Contexto:** El endpoint `PUT /recalcular/{empresa_id}` lanzaba 422 porque FastAPI lo interpretaba como `PUT /{item_id}` y "recalcular" no era un int válido.
  **Aprendizaje:** En FastAPI, los endpoints con path variables dinámicas deben declararse ANTES de los endpoints con path variables fijas del mismo método HTTP. FastAPI prueba las rutas en orden de declaración.
  **Aplicación futura:** Siempre declarar endpoints específicos (como `/recalcular/{id}`) ANTES de endpoints genéricos (`/{id}`) en routers FastAPI.

- **2026-08-31 — Exportar Excel con openpyxl:**
  **Contexto:** Se necesita generar un Excel que coincida con una plantilla existente (encabezados de dos niveles, celdas combinadas, colores específicos).
  **Aprendizaje:** La función `generar_excel_corporativo` genérica no sirve para plantillas complejas. Se necesita una función específica con `openpyxl` que use `merge_cells`, `PatternFill`, `Font`, `Alignment`, `Border` y anchos de columna personalizados.
  **Aplicación futura:** Para exportaciones que deben coincidir con una plantilla específica, crear una función dedicada en lugar de usar la genérica.
