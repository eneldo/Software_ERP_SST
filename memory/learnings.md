# Aprendizajes del Agente

Los aprendizajes más recientes deben agregarse arriba.

Formato:

- **YYYY-MM-DD — Tema:**
  **Contexto:** qué ocurrió.
  **Aprendizaje:** qué se descubrió.
  **Aplicación futura:** cómo aplicar este conocimiento.

---

- **2026-09-10 — Chrome ignora `download` en Blob URLs: usar data URLs para preservar nombre:**
  **Contexto:** Las exportaciones mostraban nombres UUID sin extensión aunque `link.download` estuviera bien configurado y la revocación se retrasara 60 segundos.
  **Aprendizaje:** Chrome (servidor de archivos interno) no respeta el atributo `download` en URLs `blob:http://...`. Sí lo respeta en URLs `data:...`. La solución es convertir la respuesta a base64 y construir una data URL `data:${contentType};base64,${base64}`. Para contenido local (CSV/HTML), usar `btoa(unescape(encodeURIComponent(content)))`.
  **Aplicación futura:** En descargas, NUNCA usar `URL.createObjectURL()`. Siempre construir `data:` URLs. No se necesita `revokeObjectURL` para data URLs. Solo `useReporteAssetUrl.js` (previsualización en elemento) puede seguir usando `createObjectURL` porque no es descarga.

- **2026-09-10 — Consultas de detalle tenant deben omitir filtro para SUPER_ADMIN global:**
  **Contexto:** La edición de exámenes médicos devolvía 404 para SUPER_ADMIN porque buscaba el examen con `Empleado.empresa_id == None`.
  **Aprendizaje:** El patrón de acceso global aplica tanto a listados como a consultas de detalle y actualización: construir primero la consulta por ID y añadir el filtro tenant solo si `tenant_id is not None`.
  **Aplicación futura:** Revisar GET/PUT/PATCH/DELETE que combinen ID con tenant; probar SUPER_ADMIN sin empresa y usuarios de empresa por separado.

- **2026-09-10 — Helpers intermedios de payload también conservan claves reasignadas:**
  **Contexto:** Crear un examen médico fallaba porque `_payload_limpio(data)` conservaba `empleado_id` y el constructor `ExamenMedico(**payload, empleado_id=data.empleado_id)` lo recibía dos veces.
  **Aprendizaje:** No basta revisar `model_dump()` directo; cualquier helper que retorne un diccionario puede conservar campos que después se reasignan explícitamente.
  **Aplicación futura:** Antes de construir el ORM, usar `payload.pop("campo", None)` para cada campo validado y reasignado, y cubrir el flujo con una prueba de creación.

- **2026-09-10 — SUPER_ADMIN sin filtro tenant debe listar todos los registros:**
  **Contexto:** El catálogo EPP permanecía vacío para SUPER_ADMIN aunque PostgreSQL tenía registros, porque `empresa_id=None` se convertía en un filtro SQL `empresa_id IS NULL`.
  **Aprendizaje:** Si el helper tenant devuelve `None` para representar acceso global, la consulta no debe aplicar el filtro de empresa; solo debe añadirlo cuando el tenant autorizado no sea `None`.
  **Aplicación futura:** En listados multi-tenant, probar explícitamente SUPER_ADMIN sin empresa, SUPER_ADMIN con empresa y usuario empresarial; evitar `filter(Model.empresa_id == tenant_id)` incondicional.

- **2026-09-10 — Pydantic `model_dump()` puede duplicar argumentos tenant en constructores ORM:**
  **Contexto:** Crear un EPP fallaba con `TypeError: EPPCatalogo() got multiple values for keyword argument 'empresa_id'` porque el schema incluía `empresa_id` y el router también lo asignaba explícitamente tras autorizar el tenant.
  **Aprendizaje:** Cuando un valor autorizado se reemplaza explícitamente al construir un modelo, excluirlo del payload con `model_dump(exclude={"empresa_id"})` para evitar duplicidad y garantizar que prevalezca el tenant validado.
  **Aplicación futura:** Revisar constructores con patrón `Model(**data.model_dump(), campo=valor_validado)` y excluir del dump cualquier campo reasignado explícitamente; añadir una prueba de regresión del endpoint.

- **2026-09-08 — Docker local: `TRUSTED_HOSTS` puede bloquear el login detrás de Nginx:**
  **Contexto:** El frontend Docker en `127.0.0.1:8081` cargaba, pero `/api/auth/login-json` respondía HTTP 400 con `Invalid host header` porque el backend de producción solo aceptaba el dominio público configurado.
  **Aprendizaje:** Para pruebas Docker exclusivamente locales, ejecutar el backend con `ENVIRONMENT=development`, `TRUSTED_HOSTS=127.0.0.1,localhost,backend`, `CORS_ORIGINS` apuntando al frontend local, `HTTPS_REDIRECT_ENABLED=false` y `REFRESH_COOKIE_SECURE=false`. Mantener `AUTO_CREATE_TABLES=false` cuando el esquema ya existe.
  **Aplicación futura:** Si el login falla con HTTP 400 antes de validar credenciales, inspeccionar primero el cuerpo de la respuesta y la configuración de hosts. No cambiar ni debilitar la configuración de producción persistente para resolver pruebas locales.

- **2026-09-08 — Selección segura de una base Docker existente:**
  **Contexto:** Había varios volúmenes PostgreSQL SST con contenidos distintos y se necesitaba iniciar la aplicación con datos limpios sin eliminar información histórica.
  **Aprendizaje:** Comparar bases mediante consultas de solo lectura a tablas de dominio, identificar el volumen por sus montajes y conectar temporalmente el contenedor elegido a la red del stack con alias `db`. `sst_db_data` estaba limpio; `sst_backup_inspect_data` conservaba información histórica.
  **Aplicación futura:** Nunca asumir qué volumen corresponde al entorno deseado ni ejecutar `docker compose down -v`. Inventariar contenedores, volúmenes y conteos antes de iniciar o recrear servicios.

- **2026-09-06 — Columnas faltantes en DB: patrón diagnóstico `sa.inspect` + `model.__table__.columns`:**
  **Contexto:** Múltiples endpoints retornaban 500 sin body visible: Dashboard SST, Política SST, Evaluación Inicial.
  **Aprendizaje:** Cuando un endpoint retorna 500 con body vacío y las columnas del modelo parecen correctas, usar `sqlalchemy.inspect` para comparar columnas de DB vs columnas del modelo: `db_cols = set(c['name'] for c in inspector.get_columns('tabla'))` vs `model_cols = set(c.key for c in Model.__table__.columns)`. Las columnas faltantes causan errores crypticos en SQLAlchemy ORM. Ejemplo此次: `planes_mejoramiento_sst.falta responsable_id`, `politicas_sst.falta tipo_politica`, `archivos_sst.falta hash_sha256/fecha_descarga`.
  **Aplicación futura:** Siempre ejecutar diagnóstico de columnas faltantes después de agregar nuevos modelos o modificar existentes. Mantener script de verificación de integridad DB.

- **2026-09-06 — Módulo Informe de Gestión SG-SST: Arquitectura de consolidación de datos:**
  **Contexto:** El prompt maestro requería un módulo integral que consolidara datos de 15+ módulos existentes del SG-SST para generar el informe anual.
  **Aprendizaje:** En lugar de crear tablas de datos duplicadas, se implementó un patrón de "snapshot histórico" donde el servicio de consolidación consulta todos los módulos origen y almacena un JSON con los datos consolidados en el momento de generación. Esto garantiza que los datos históricos no cambien cuando se modifiquen datos operativos posteriores.
  **Aplicación futura:** Para módulos de reportes que requieren "fotografía" de datos en un momento dado: 1) crear servicio que consulte módulos origen, 2) almacenar snapshot como JSON, 3) versionar cada consolidación, 4) nunca modificar datos ya consolidados.

- **2026-09-06 — Migraciones Alembic: Usar down_revision con revision_id, no con nombre de archivo:**
  **Contexto:** La migración del Informe de Gestión fallaba porque usaba `down_revision = "20260906_0002"` (nombre de archivo) en lugar de `down_revision = "d9e0f1a2b3c4"` (revision_id real).
  **Aprendizaje:** El campo `down_revision` en Alembic debe contener el `revision` ID del archivo anterior, NO el nombre del archivo. Ejemplo: si el archivo anterior tiene `revision = "d9e0f1a2b3c4"`, entonces `down_revision = "d9e0f1a2b3c4"`.
  **Aplicación futura:** Siempre verificar el `revision` ID del archivo anterior antes de crear una nueva migración. Usar `alembic history` para ver la cadena correcta.

- **2026-09-04 — Aislamiento tenant sistemático en routers EPP, Inspecciones y Evaluaciones Médicas:**
  **Contexto:** Auditoría P0 reveló que 27+ endpoints en EPP, 35+ en Inspecciones/Seguimientos y 25+ en Evaluaciones Médicas solo validaban RBAC (`require_roles`) pero no filtraban por `usuario.empresa_id`, permitiendo acceso cross-tenant.
  **Aprendizaje:** Implementar helper `_empresa_id_autorizada(usuario, empresa_id)` que derive el tenant del usuario (o valide el solicitado para SUPER_ADMIN) y aplicarlo en: (1) queries base, (2) validación de recursos padre antes de hijos, (3) exportaciones, (4) endpoints de evidencias/archivos, (5) generation desde profesiograma. Centralizar en helper reutilizable evita duplicación y olvidos.
  **Aplicación futura:** Para cualquier router nuevo: 1) crear `_empresa_id_autorizada`, 2) aplicarlo al inicio de cada endpoint, 3) pasar tenant a queries base, 4) validar recursos padre antes de acceder a hijos, 5) añadir test de aislamiento cross-tenant.

- **2026-09-04 — Migraciones aditivas con guardas `sa.inspect` para baseline dinámico:**
  **Contexto:** El baseline `0001_initial_schema` usa `Base.metadata.create_all()` con metadata actual. Migraciones posteriores (IPER, Política SST, Exámenes Médicos, Historial Legal, Perfil Sociodemográfico, Indicadores) fallaban en instalación limpia por tablas/columnas ya creadas por el baseline.
  **Aprendizaje:** Toda migración `op.add_column`, `op.create_table`, `op.alter_column` posterior al baseline debe inspeccionar estado actual con `sa.inspect(op.get_bind())` y omitir operación si el elemento ya existe con especificación correcta. Guardas simétricas en `upgrade()` y `downgrade()`.
  **Aplicación futura:** Plantilla estándar para migraciones aditivas: `columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("tabla")}` + `if "col" not in columnas: op.add_column(...)`. Aplicar a tablas, índices, FKs y tipos de columna.

- **2026-09-04 — Instalación limpia completa como validación obligatoria:**
  **Contexto:** Aunque `alembic upgrade head` pasaba en base existente, la cadena completa fallaba en base temporal por colisiones no detectadas (Política SST, Indicadores).
  **Aprendizaje:** Validar SIEMPRE la cadena Alembic completa en una base temporal vacía propiedad del usuario de migración (`sst_user`). Crear BD → `alembic upgrade head` → verificar tablas/columnas → dropear BD. Solo así se detectan colisiones del baseline dinámico.
  **Aplicación futura:** Script automatizado post-migración: `create db temp owner sst_user → alembic upgrade head → drop db temp`. Integrar en CI/CD.

- **2026-09-04 — Propiedad de tabla para Alembic (no solo privilegios DML):**
  **Contexto:** `sst_user` tenía permisos DML en `capas_sst` pero PostgreSQL rechazó `ALTER TABLE` porque el owner era `postgres`.
  **Aprendizaje:** Permisos DML (SELECT/INSERT/UPDATE/DELETE) no bastan para DDL. El usuario que ejecuta migraciones debe ser owner de las tablas que modificará, o usar rol DDL dedicado. Verificar `pg_tables.tableowner` antes de diagnosticar fallos de migración.
  **Aplicación futura:** Normalizar ownership solo en tablas afectadas (`ALTER TABLE ... OWNER TO sst_user`) tras crear nuevas tablas vía baseline o migración inicial.

- **2026-09-04 — Validar la cadena Alembic en una base realmente limpia:**
  **Contexto:** El baseline usa `Base.metadata.create_all()` con la metadata actual. Aunque las migraciones IPER se protegieron, la prueba completa encontró nuevas colisiones en Política SST y migraciones aditivas posteriores.
  **Aprendizaje:** No basta con probar `alembic upgrade head` sobre una base existente. Toda migración que crea o agrega elementos posteriores al baseline debe inspeccionar tablas, columnas, claves y tipos, y la cadena completa debe ejecutarse en una base temporal vacía.
  **Aplicación futura:** Después de agregar migraciones, crear una base temporal propiedad del usuario de migración, ejecutar desde revisión inicial hasta `head` y eliminarla solo después de verificar el resultado.

- **2026-09-04 — Alembic necesita propiedad de tabla, no solo privilegios DML:**
  **Contexto:** `sst_user` podía usar las tablas CAPA, pero PostgreSQL rechazó `ALTER TABLE` porque `capas_sst` y `capas_seguimientos_sst` pertenecían a `postgres`.
  **Aprendizaje:** Conceder permisos de lectura/escritura no permite modificar el esquema; el rol que ejecuta Alembic debe ser propietario de la tabla o las migraciones deben ejecutarse con un rol DDL controlado.
  **Aplicación futura:** Verificar `pg_tables.tableowner` antes de atribuir un fallo de migración al código y normalizar la propiedad solo sobre las tablas afectadas.

- **2026-09-03 — Ficha técnica EPP: upload PDF + compresión + view modal:**
  **Contexto:** Usuario pidió agregar ficha técnica PDF al catálogo EPP, con upload, compresión automática, vista en modal y opción de ver desde la tabla (siempre visible, con mensaje si no existe).
  **Aprendizaje:**
  1. Modelo: 3 columnas (`ficha_tecnica_url`, `ficha_tecnica_nombre`, `ficha_tecnica_archivo_id` FK → archivos_sst SET NULL). No necesita schema Create/Update porque se maneja por endpoint dedicado.
  2. Router: endpoints `POST /catalogo/{id}/ficha-tecnica` y `DELETE /catalogo/{id}/ficha-tecnica` separados del CRUD principal. Upload reutiliza `_guardar_archivo_epp_upload()` que ya maneja pikepdf compression.
  3. Frontend: `guardarCatalogo()` primero crea/actualiza el registro, luego sube la ficha si hay archivo seleccionado (necesita el ID del registro creado).
  4. Botón siempre visible en tabla: cuando no hay ficha, el modal muestra "No cuenta con ficha técnica" con icono y guidance.
  5. iframe para previsualizar PDF en modal + botón descargar en footer.
  **Aplicación futura:** Para documentos adjuntos a catálogos: modelo con URL+nombre+FK, endpoint dedicado upload/delete, frontend con file picker en formulario + modal de vista. Patrón reutilizable.

- **2026-09-03 — create_all() no agrega columnas a tablas existentes:**
  **Contexto:** Las 7 columnas nuevas de Plan Anual (Decreto 1072) se agregaron al modelo SQLAlchemy pero `Base.metadata.create_all()` solo crea tablas nuevas, no modifica existentes.
  **Aprendizaje:** Cuando se agregan columnas a un modelo existente y NO se usa Alembic para la migración, ejecutar `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` manualmente. Conectar como superuser (postgres) si el usuario de la app no tiene permisos DDL.
  **Aplicación futura:** Para desarrollo rápido sin Alembic: script temporal `_add_cols.py` con ALTER TABLEs. Verificar con `SELECT column_name FROM information_schema.columns`. Limpiar script después de ejecutar.

- **2026-09-03 — PDF export con campos dinámicos (encabezado + firmas personalizadas):**
  **Contexto:** El servicio compartido `generar_pdf_corporativo()` tenía firmas genéricas ("Representante Legal", "Responsable SST"). Para Plan Anual Decreto 1072 se necesitaban nombres/cargos reales.
  **Aprendizaje:** Agregar parámetros opcionales al servicio compartido (`encabezado_extra: list`, `firma_representante: dict`, `firmar_responsable: dict`) en lugar de crear un servicio duplicado. El primer item de los datos (`items[0]`) contiene los metadatos del plan.
  **Aplicación futura:** Para exportaciones con metadatos del plan/cabecera: pasar datos como parámetros opcionales al servicio PDF genérico. Evitar duplicar lógica de generación PDF.

- **2026-09-03 — Toggle panel: patrón reutilizable en módulos Planear:**
  **Contexto:** Se implementó toggle de panel en PlanAnualPage siguiendo el patrón de PoliticaSSTPage.
  **Aprendizaje:** El patrón es: (1) estado `sidebarVisible`, (2) botón en hero toolbar, (3) botón en header del panel, (4) clase `X-panel-collapsed` en grid principal, (5) clase `X-panel-hidden` en aside, (6) CSS con `grid-template-columns: minmax(0, 1fr)` para collapsed y `width/min-width/max-width: 0 + opacity:0 + visibility:hidden + pointer-events:none` para hidden.
  **Aplicación futura:** Copiar bloques CSS de `.pol-panel-collapsed` / `.pol-panel-hidden` / `.pol-sidebar-toggle-btn` y renombrar prefijo para nuevos módulos.

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