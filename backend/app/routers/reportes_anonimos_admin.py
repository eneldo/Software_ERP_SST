# ============================================================
# ROUTER GESTIÓN ADMINISTRATIVA REPORTES ANÓNIMOS SST
# ERP SST PRO
# FASE 1.1.25.6 — Evidencias Inteligentes Reportes SST
# Archivo: backend/app/routers/reportes_anonimos_admin.py
# ============================================================

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.archivo_sst import ArchivoSST
from app.models.area import Area
from app.models.cargo import Cargo
from app.models.capa import CapaSST
from app.models.empleado import Empleado
from app.models.empresa import Empresa
from app.models.inspeccion import InspeccionHallazgoSST, InspeccionSST
from app.models.notificacion_sst import NotificacionSST
from app.models.reporte_inseguridad import ReporteInseguridadSST
from app.models.reporte_evidencia_sst import ReporteEvidenciaSST
from app.models.sede import Sede
from app.schemas.reporte_inseguridad_admin_schema import (
    ConvertirReporteResponse,
    MisCasosQueryResponse,
    ReporteAsignacionRequest,
    ReporteCierreRequest,
    ReporteInseguridadAdminResponse,
    ReporteInseguridadAdminUpdate,
    ReportesAnonimosDashboardResponse,
    ResponsableSSTResponse,
    WorkflowReporteRequest,
)

router = APIRouter(prefix="/reportes-anonimos", tags=["Gestión Reportes Anónimos SST"])

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]
ROLES_ADMIN = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]
ESTADOS_CIERRE = {"CERRADO", "ANULADO"}


# ============================================================
# HELPERS
# ============================================================

def _upper(value: Any, default: str | None = None) -> str | None:
    if value is None:
        return default
    txt = str(value).strip().upper()
    return txt if txt else default


def _today() -> date:
    return date.today()


def _now_line(texto: str) -> str:
    return f"[{datetime.utcnow().isoformat()}] {texto}"


def _append_traza(actual: str | None, texto: str) -> str:
    line = _now_line(texto)
    return f"{actual}\n{line}" if actual else line


def _base_query(db: Session):
    return db.query(ReporteInseguridadSST).options(
        joinedload(ReporteInseguridadSST.empresa),
        joinedload(ReporteInseguridadSST.sede),
        joinedload(ReporteInseguridadSST.area),
        joinedload(ReporteInseguridadSST.cargo),
        joinedload(ReporteInseguridadSST.empleado),
    )


def _nombre_empleado(emp: Empleado | None) -> str | None:
    if not emp:
        return None
    return " ".join([str(emp.nombres or "").strip(), str(emp.apellidos or "").strip()]).strip() or None


def _to_response(item: ReporteInseguridadSST) -> ReporteInseguridadAdminResponse:
    data = ReporteInseguridadAdminResponse.model_validate(item)
    data.empresa_nombre = item.empresa.nombre if item.empresa else None
    data.sede_nombre = item.sede.nombre if item.sede else None
    data.area_nombre = item.area.nombre if item.area else None
    data.cargo_nombre = item.cargo.nombre if item.cargo else None
    data.empleado_nombre = _nombre_empleado(item.empleado)
    evidencias = [ev for ev in getattr(item, "evidencias", []) if getattr(ev, "activo", True)]
    data.evidencias = evidencias
    data.total_evidencias = len(evidencias)
    return data


def _validar_area(db: Session, empresa_id: int, area_id: int | None):
    if not area_id:
        return None
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    if area.empresa_id != empresa_id:
        raise HTTPException(status_code=400, detail="El área no pertenece a la empresa del reporte")
    return area


def _riesgo_desde_prioridad(prioridad: str | None) -> str:
    p = _upper(prioridad, "MEDIA")
    if p in {"CRITICA", "CRÍTICA"}:
        return "CRITICO"
    if p == "ALTA":
        return "ALTO"
    if p == "BAJA":
        return "BAJO"
    return "MEDIO"


def _codigo(prefijo: str) -> str:
    return f"{prefijo}-{datetime.utcnow().strftime('%y%m%d%H%M%S')}"


def _crear_notificacion_gestion(
    db: Session,
    reporte: ReporteInseguridadSST,
    titulo: str,
    descripcion: str,
    prioridad: str = "MEDIA",
    tipo: str = "SEGUIMIENTO",
):
    noti = NotificacionSST(
        empresa_id=reporte.empresa_id,
        sede_id=reporte.sede_id,
        area_id=reporte.area_id,
        modulo="REPORTE_ANONIMO_SST",
        referencia_id=reporte.id,
        clave_unica=f"REP-ANON-{reporte.id}-{tipo}-{int(datetime.utcnow().timestamp())}",
        tipo=tipo,
        prioridad=_upper(prioridad, "MEDIA"),
        estado="PENDIENTE",
        titulo=titulo,
        descripcion=descripcion,
        accion_recomendada="Revisar el reporte anónimo SST, asignar responsable y definir si requiere inspección, hallazgo o CAPA.",
        url_destino="/verificar/reportes-anonimos",
        leida=False,
        archivada=False,
        activa=True,
        origen_generacion="REPORTE_ANONIMO",
        fecha_evento=datetime.utcnow().date(),
    )
    db.add(noti)


def _obtener_reporte(db: Session, reporte_id: int) -> ReporteInseguridadSST:
    item = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Reporte anónimo SST no encontrado")
    return item




def _nombre_archivo_desde_url(url: str | None, fallback: str = "evidencia") -> str:
    if not url:
        return fallback
    clean = str(url).split("?", 1)[0].rstrip("/")
    name = clean.rsplit("/", 1)[-1] if "/" in clean else clean
    return name or fallback


def _extension_desde_nombre(nombre: str | None) -> str | None:
    if not nombre or "." not in nombre:
        return None
    return nombre.rsplit(".", 1)[-1].lower().strip() or None


def _tipo_archivo_sst_para_modulo(modulo: str) -> str:
    modulo = (modulo or "").upper().strip()
    if modulo == "CAPA":
        return "EVIDENCIA_CAPA"
    if modulo == "HALLAZGOS":
        return "EVIDENCIA_HALLAZGO"
    if modulo == "INSPECCIONES":
        return "EVIDENCIA"
    return "EVIDENCIA"


def _copiar_evidencias_reporte_a_modulo(
    db: Session,
    reporte: ReporteInseguridadSST,
    modulo: str,
    referencia_id: int,
    usuario_id: int | None = None,
    descripcion_extra: str | None = None,
) -> int:
    """
    Enlaza las evidencias inteligentes del Reporte SST al módulo destino usando ArchivoSST.

    Importante:
    - No duplica físicamente el archivo; reutiliza la URL optimizada/WEBP ya creada.
    - Evita duplicados por módulo + referencia + URL.
    - Permite que los endpoints existentes de Inspecciones y CAPA las muestren sin cambiar frontend:
        GET /inspecciones/{id}/evidencias  -> modulo INSPECCIONES
        GET /capa/{id}/evidencias          -> modulo CAPA
    """
    modulo = (modulo or "").upper().strip()
    if not referencia_id or not modulo:
        return 0

    evidencias = (
        db.query(ReporteEvidenciaSST)
        .filter(
            ReporteEvidenciaSST.reporte_id == reporte.id,
            ReporteEvidenciaSST.activo.is_(True),
        )
        .order_by(ReporteEvidenciaSST.id.asc())
        .all()
    )

    # Compatibilidad con reportes antiguos que solo tenían archivo_url en reportes_inseguridad_sst.
    if not evidencias and reporte.archivo_url:
        nombre = reporte.archivo_nombre or _nombre_archivo_desde_url(reporte.archivo_url)
        exists = db.query(ArchivoSST.id).filter(
            ArchivoSST.modulo == modulo,
            ArchivoSST.referencia_id == referencia_id,
            ArchivoSST.url == reporte.archivo_url,
            ArchivoSST.activo.is_(True),
        ).first()
        if exists:
            return 0
        registro = ArchivoSST(
            empresa_id=reporte.empresa_id,
            usuario_id=usuario_id,
            tipo=_tipo_archivo_sst_para_modulo(modulo),
            nombre_original=nombre,
            nombre_archivo=_nombre_archivo_desde_url(reporte.archivo_url, nombre),
            ruta=reporte.archivo_url,
            url=reporte.archivo_url,
            extension=_extension_desde_nombre(nombre),
            mime_type=reporte.archivo_mime_type,
            tamano_bytes=reporte.archivo_tamano_bytes,
            modulo=modulo,
            referencia_id=referencia_id,
            descripcion=(descripcion_extra or f"Evidencia heredada desde reporte SST {reporte.codigo}"),
            activo=True,
        )
        db.add(registro)
        return 1

    creadas = 0
    for ev in evidencias:
        url = ev.archivo_url or ev.archivo_original_url
        if not url:
            continue

        exists = db.query(ArchivoSST.id).filter(
            ArchivoSST.modulo == modulo,
            ArchivoSST.referencia_id == referencia_id,
            ArchivoSST.url == url,
            ArchivoSST.activo.is_(True),
        ).first()
        if exists:
            continue

        nombre_original = ev.archivo_nombre or _nombre_archivo_desde_url(ev.archivo_original_url or url)
        nombre_archivo = _nombre_archivo_desde_url(url, nombre_original)
        descripcion = (
            f"Evidencia copiada desde reporte SST {reporte.codigo}. "
            f"Categoría IA: {ev.categoria_ia or 'SIN_CLASIFICAR'}. "
            f"{descripcion_extra or ''}"
        ).strip()

        registro = ArchivoSST(
            empresa_id=reporte.empresa_id,
            usuario_id=usuario_id,
            tipo=_tipo_archivo_sst_para_modulo(modulo),
            nombre_original=nombre_original,
            nombre_archivo=nombre_archivo,
            ruta=url,
            url=url,
            extension=ev.extension or _extension_desde_nombre(nombre_archivo),
            mime_type=ev.mime_type,
            tamano_bytes=ev.peso_optimizado_bytes or ev.peso_original_bytes,
            modulo=modulo,
            referencia_id=referencia_id,
            descripcion=descripcion[:500],
            activo=True,
        )
        db.add(registro)
        creadas += 1

    return creadas

def _responsable_desde_request(db: Session, data: ReporteAsignacionRequest) -> str:
    if data.responsable_empleado_id:
        emp = db.query(Empleado).filter(Empleado.id == data.responsable_empleado_id, Empleado.activo.is_(True)).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Empleado responsable no encontrado o inactivo")
        return _nombre_empleado(emp) or f"Empleado ID {emp.id}"

    if data.responsable_asignado and data.responsable_asignado.strip():
        return data.responsable_asignado.strip()

    raise HTTPException(status_code=422, detail="Debe seleccionar o escribir un responsable SST")


# ============================================================
# ENDPOINTS CATÁLOGO / RESPONSABLES
# ============================================================

@router.get("/responsables-sst", response_model=list[ResponsableSSTResponse])
def listar_responsables_sst(
    empresa_id: int | None = Query(default=None),
    area_sst_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = db.query(Empleado).options(
        joinedload(Empleado.empresa),
        joinedload(Empleado.sede),
        joinedload(Empleado.area),
        joinedload(Empleado.cargo),
    ).filter(Empleado.activo.is_(True))

    if empresa_id:
        query = query.filter(Empleado.empresa_id == empresa_id)

    empleados = query.order_by(Empleado.nombres.asc(), Empleado.apellidos.asc()).all()

    def es_sst(emp: Empleado) -> bool:
        area = _upper(getattr(emp.area, "nombre", ""), "") or ""
        cargo = _upper(getattr(emp.cargo, "nombre", ""), "") or ""
        texto = f"{area} {cargo}"
        claves = ["SST", "SEGURIDAD", "SALUD", "HSE", "SG-SST", "OCUPACIONAL"]
        return any(c in texto for c in claves)

    filtrados = [emp for emp in empleados if es_sst(emp)] if area_sst_only else empleados
    if area_sst_only and not filtrados:
        filtrados = empleados

    return [
        ResponsableSSTResponse(
            id=emp.id,
            nombre=_nombre_empleado(emp) or f"Empleado {emp.id}",
            documento=emp.documento,
            correo=emp.correo,
            telefono=emp.telefono,
            empresa_id=emp.empresa_id,
            sede_id=emp.sede_id,
            area_id=emp.area_id,
            cargo_id=emp.cargo_id,
            empresa_nombre=emp.empresa.nombre if emp.empresa else None,
            sede_nombre=emp.sede.nombre if emp.sede else None,
            area_nombre=emp.area.nombre if emp.area else None,
            cargo_nombre=emp.cargo.nombre if emp.cargo else None,
        )
        for emp in filtrados
    ]


# ============================================================
# LISTADO / DASHBOARD
# ============================================================

@router.get("/", response_model=list[ReporteInseguridadAdminResponse])
def listar_reportes_anonimos(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    tipo_reporte: str | None = Query(default=None),
    prioridad: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    responsable: str | None = Query(default=None),
    con_evidencia: bool | None = Query(default=None),
    buscar: str | None = Query(default=None),
    activo: bool | None = Query(default=True),
    limit: int = Query(default=300, ge=1, le=1000),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = _base_query(db)

    if empresa_id:
        query = query.filter(ReporteInseguridadSST.empresa_id == empresa_id)
    if sede_id:
        query = query.filter(ReporteInseguridadSST.sede_id == sede_id)
    if area_id:
        query = query.filter(ReporteInseguridadSST.area_id == area_id)
    if tipo_reporte:
        query = query.filter(func.upper(ReporteInseguridadSST.tipo_reporte) == tipo_reporte.upper())
    if prioridad:
        query = query.filter(func.upper(ReporteInseguridadSST.prioridad) == prioridad.upper())
    if estado:
        query = query.filter(func.upper(ReporteInseguridadSST.estado) == estado.upper())
    if responsable:
        query = query.filter(func.lower(ReporteInseguridadSST.responsable_asignado).like(f"%{responsable.strip().lower()}%"))
    if activo is not None:
        query = query.filter(ReporteInseguridadSST.activo == activo)
    if con_evidencia is True:
        query = query.filter(or_(
            ReporteInseguridadSST.archivo_url.isnot(None),
            ReporteInseguridadSST.evidencias.any(ReporteEvidenciaSST.activo.is_(True)),
        ))
    if con_evidencia is False:
        query = query.filter(
            ReporteInseguridadSST.archivo_url.is_(None),
            ~ReporteInseguridadSST.evidencias.any(ReporteEvidenciaSST.activo.is_(True)),
        )
    if buscar:
        like = f"%{buscar.strip().lower()}%"
        query = query.filter(or_(
            func.lower(ReporteInseguridadSST.codigo).like(like),
            func.lower(ReporteInseguridadSST.titulo).like(like),
            func.lower(ReporteInseguridadSST.descripcion).like(like),
            func.lower(ReporteInseguridadSST.ubicacion).like(like),
            func.lower(ReporteInseguridadSST.responsable_asignado).like(like),
        ))

    items = query.order_by(ReporteInseguridadSST.fecha_reporte.desc(), ReporteInseguridadSST.id.desc()).limit(limit).all()
    return [_to_response(item) for item in items]


@router.get("/mis-casos", response_model=MisCasosQueryResponse)
def listar_mis_casos_sst(
    responsable: str | None = Query(default=None),
    empresa_id: int | None = Query(default=None),
    incluir_cerrados: bool = Query(default=False),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = _base_query(db).filter(ReporteInseguridadSST.activo.is_(True))
    if empresa_id:
        query = query.filter(ReporteInseguridadSST.empresa_id == empresa_id)
    if responsable:
        query = query.filter(func.lower(ReporteInseguridadSST.responsable_asignado).like(f"%{responsable.strip().lower()}%"))
    if not incluir_cerrados:
        query = query.filter(func.upper(ReporteInseguridadSST.estado).notin_(["CERRADO", "ANULADO"]))
    items = query.order_by(ReporteInseguridadSST.fecha_reporte.desc()).limit(500).all()
    return MisCasosQueryResponse(total=len(items), casos=[_to_response(i) for i in items])


@router.get("/dashboard", response_model=ReportesAnonimosDashboardResponse)
def dashboard_reportes_anonimos(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.activo.is_(True))
    if empresa_id:
        query = query.filter(ReporteInseguridadSST.empresa_id == empresa_id)
    if sede_id:
        query = query.filter(ReporteInseguridadSST.sede_id == sede_id)
    if area_id:
        query = query.filter(ReporteInseguridadSST.area_id == area_id)

    items = query.all()

    def count(attr: str):
        data: dict[str, int] = {}
        for item in items:
            key = _upper(getattr(item, attr, None), "SIN_DATO") or "SIN_DATO"
            data[key] = data.get(key, 0) + 1
        return data

    por_tipo = count("tipo_reporte")
    por_prioridad = count("prioridad")
    por_estado = count("estado")
    por_responsable = count("responsable_asignado")

    por_area: dict[str, int] = {}
    area_ids = {i.area_id for i in items if i.area_id}
    areas = {a.id: a.nombre for a in db.query(Area).filter(Area.id.in_(area_ids)).all()} if area_ids else {}
    for item in items:
        key = areas.get(item.area_id, "Sin área")
        por_area[key] = por_area.get(key, 0) + 1

    reportados = por_estado.get("REPORTADO", 0)
    asignados = por_estado.get("ASIGNADO", 0)
    en_proceso = por_estado.get("EN_PROCESO", 0)
    cerrados = por_estado.get("CERRADO", 0)
    anulados = por_estado.get("ANULADO", 0)
    criticos = por_prioridad.get("CRITICA", 0) + por_prioridad.get("CRÍTICA", 0)
    altos = por_prioridad.get("ALTA", 0)
    medios = por_prioridad.get("MEDIA", 0)
    bajos = por_prioridad.get("BAJA", 0)
    evidencia_rows = db.query(ReporteEvidenciaSST).join(ReporteInseguridadSST, ReporteEvidenciaSST.reporte_id == ReporteInseguridadSST.id).filter(ReporteEvidenciaSST.activo.is_(True))
    if empresa_id:
        evidencia_rows = evidencia_rows.filter(ReporteInseguridadSST.empresa_id == empresa_id)
    if sede_id:
        evidencia_rows = evidencia_rows.filter(ReporteInseguridadSST.sede_id == sede_id)
    if area_id:
        evidencia_rows = evidencia_rows.filter(ReporteInseguridadSST.area_id == area_id)
    evidencias = evidencia_rows.all()
    reportes_con_evidencias = {e.reporte_id for e in evidencias}
    con_evidencia = sum(1 for i in items if i.archivo_url or i.id in reportes_con_evidencias)
    sin_evidencia = max(len(items) - con_evidencia, 0)
    total_evidencias = len(evidencias)
    evidencias_imagen = sum(1 for e in evidencias if e.tipo_archivo == "IMAGEN")
    evidencias_video = sum(1 for e in evidencias if e.tipo_archivo == "VIDEO")
    evidencias_pdf = sum(1 for e in evidencias if e.tipo_archivo == "PDF")
    peso_original = sum(int(e.peso_original_bytes or 0) for e in evidencias)
    peso_optimizado = sum(int(e.peso_optimizado_bytes or 0) for e in evidencias)
    ahorro_evidencias_mb = round(max(peso_original - peso_optimizado, 0) / (1024 * 1024), 2)
    por_categoria_ia: dict[str, int] = {}
    for ev in evidencias:
        key = _upper(ev.categoria_ia, "SIN_CLASIFICAR") or "SIN_CLASIFICAR"
        por_categoria_ia[key] = por_categoria_ia.get(key, 0) + 1
    pendientes = reportados + asignados + en_proceso
    sin_asignar = sum(1 for i in items if not i.responsable_asignado and _upper(i.estado) not in ESTADOS_CIERRE)
    gestionados_inspeccion = sum(1 for i in items if i.convertido_a_inspeccion or i.inspeccion_id)
    gestionados_capa = sum(1 for i in items if i.capa_id)

    recomendaciones = []
    if criticos:
        recomendaciones.append("Atender de inmediato los reportes críticos y documentar acciones de control.")
    if sin_asignar:
        recomendaciones.append("Asignar responsable SST a los reportes nuevos sin gestión.")
    if con_evidencia:
        recomendaciones.append("Revisar evidencias adjuntas y convertir los casos aplicables en inspección, hallazgo o CAPA.")
    if not recomendaciones:
        recomendaciones.append("Gestión de reportes anónimos estable. Mantener seguimiento preventivo.")

    return ReportesAnonimosDashboardResponse(
        total=len(items),
        reportados=reportados,
        asignados=asignados,
        en_proceso=en_proceso,
        cerrados=cerrados,
        anulados=anulados,
        criticos=criticos,
        altos=altos,
        medios=medios,
        bajos=bajos,
        con_evidencia=con_evidencia,
        sin_evidencia=sin_evidencia,
        total_evidencias=total_evidencias,
        evidencias_imagen=evidencias_imagen,
        evidencias_video=evidencias_video,
        evidencias_pdf=evidencias_pdf,
        ahorro_evidencias_mb=ahorro_evidencias_mb,
        pendientes=pendientes,
        sin_asignar=sin_asignar,
        gestionados_inspeccion=gestionados_inspeccion,
        gestionados_capa=gestionados_capa,
        por_tipo=por_tipo,
        por_prioridad=por_prioridad,
        por_estado=por_estado,
        por_area=por_area,
        por_responsable=por_responsable,
        por_categoria_ia=por_categoria_ia,
        recomendaciones=recomendaciones,
    )


@router.get("/{reporte_id}", response_model=ReporteInseguridadAdminResponse)
def obtener_reporte_anonimo(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _base_query(db).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Reporte anónimo SST no encontrado")
    return _to_response(item)


# ============================================================
# ACCIONES DE WORKFLOW
# ============================================================

@router.put("/{reporte_id}", response_model=ReporteInseguridadAdminResponse)
def actualizar_reporte_anonimo(
    reporte_id: int,
    data: ReporteInseguridadAdminUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _obtener_reporte(db, reporte_id)
    update = data.model_dump(exclude_unset=True)
    if "area_id" in update:
        _validar_area(db, item.empresa_id, update.get("area_id"))

    cambios = []
    for key, value in update.items():
        setattr(item, key, value)
        cambios.append(key)

    if "estado" in update and update["estado"] == "CERRADO" and not item.fecha_cierre:
        item.fecha_cierre = datetime.utcnow()

    if cambios:
        item.trazabilidad = _append_traza(item.trazabilidad, f"Reporte actualizado. Campos: {', '.join(cambios)}")

    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.put("/{reporte_id}/asignar", response_model=ReporteInseguridadAdminResponse)
def asignar_reporte_anonimo(
    reporte_id: int,
    data: ReporteAsignacionRequest,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _obtener_reporte(db, reporte_id)
    responsable = _responsable_desde_request(db, data)

    item.responsable_asignado = responsable
    item.estado = "ASIGNADO"
    if data.observaciones:
        item.observaciones = f"{item.observaciones or ''}\n{data.observaciones}".strip()
    item.trazabilidad = _append_traza(item.trazabilidad, f"Asignado a {item.responsable_asignado}")

    _crear_notificacion_gestion(
        db,
        item,
        titulo=f"Reporte anónimo asignado: {item.codigo}",
        descripcion=f"Responsable: {item.responsable_asignado}. Reporte: {item.titulo}",
        prioridad=item.prioridad,
    )

    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.put("/{reporte_id}/en-proceso", response_model=ReporteInseguridadAdminResponse)
def marcar_en_proceso(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _obtener_reporte(db, reporte_id)
    item.estado = "EN_PROCESO"
    item.trazabilidad = _append_traza(item.trazabilidad, "Reporte marcado EN_PROCESO")
    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.put("/{reporte_id}/cerrar", response_model=ReporteInseguridadAdminResponse)
def cerrar_reporte_anonimo(
    reporte_id: int,
    data: ReporteCierreRequest,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _obtener_reporte(db, reporte_id)
    item.estado = "CERRADO"
    item.fecha_cierre = datetime.utcnow()
    if data.accion_cierre:
        item.accion_inmediata = f"{item.accion_inmediata or ''}\nCierre: {data.accion_cierre}".strip()
    if data.observaciones:
        item.observaciones = f"{item.observaciones or ''}\n{data.observaciones}".strip()
    item.trazabilidad = _append_traza(item.trazabilidad, "Reporte cerrado por gestión SST")

    _crear_notificacion_gestion(
        db,
        item,
        titulo=f"Reporte anónimo cerrado: {item.codigo}",
        descripcion=f"Reporte cerrado. Acción: {data.accion_cierre or 'No especificada'}",
        prioridad="BAJA",
        tipo="CUMPLIMIENTO",
    )

    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.put("/{reporte_id}/anular", response_model=ReporteInseguridadAdminResponse)
def anular_reporte_anonimo(
    reporte_id: int,
    motivo: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ADMIN)),
):
    item = _obtener_reporte(db, reporte_id)
    item.estado = "ANULADO"
    item.activo = False
    item.fecha_cierre = datetime.utcnow()
    item.trazabilidad = _append_traza(item.trazabilidad, f"Reporte anulado. Motivo: {motivo or 'No especificado'}")
    db.commit()
    db.refresh(item)
    return _to_response(item)


# ============================================================
# CONVERSIÓN REAL A INSPECCIÓN / HALLAZGO / CAPA
# ============================================================

@router.post("/{reporte_id}/convertir/inspeccion", response_model=ConvertirReporteResponse)
def crear_inspeccion_desde_reporte(
    reporte_id: int,
    data: WorkflowReporteRequest | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _obtener_reporte(db, reporte_id)
    responsable = (data.responsable if data and data.responsable else item.responsable_asignado) or "Responsable SST"
    hoy = _today()

    if item.inspeccion_id:
        return ConvertirReporteResponse(ok=True, mensaje="El reporte ya tiene inspección asociada.", reporte_id=item.id, destino_id=item.inspeccion_id)

    inspeccion = InspeccionSST(
        empresa_id=item.empresa_id,
        sede_id=item.sede_id,
        area_id=item.area_id,
        cargo_id=item.cargo_id,
        empleado_id=None,
        usuario_id=getattr(usuario, "id", None),
        codigo=_codigo("INSP-REP"),
        tipo_inspeccion="REPORTE_ANONIMO_SST",
        titulo=f"Gestión reporte anónimo: {item.titulo}"[:255],
        descripcion=f"Reporte origen {item.codigo}.\n\n{item.descripcion}",
        lugar=item.ubicacion,
        responsable=responsable,
        fecha_programada=hoy,
        fecha_inspeccion=hoy,
        estado="PROGRAMADA",
        resultado="PENDIENTE",
        nivel_riesgo=_riesgo_desde_prioridad(item.prioridad),
        cumplimiento=0,
        observaciones=f"Generada automáticamente desde reporte anónimo SST {item.codigo}. Evidencias: {len(getattr(item, 'evidencias', []) or []) or ('1' if item.archivo_url else '0')}",
        activo=True,
        trazabilidad=_now_line(f"Inspección creada desde reporte anónimo {item.codigo}"),
    )
    db.add(inspeccion)
    db.flush()

    evidencias_copiadas = _copiar_evidencias_reporte_a_modulo(
        db=db,
        reporte=item,
        modulo="INSPECCIONES",
        referencia_id=inspeccion.id,
        usuario_id=getattr(usuario, "id", None),
        descripcion_extra=f"Inspección generada automáticamente desde reporte {item.codigo}.",
    )

    item.convertido_a_inspeccion = True
    item.inspeccion_id = inspeccion.id
    item.estado = "EN_PROCESO"
    item.trazabilidad = _append_traza(
        item.trazabilidad,
        f"Inspección SST creada automáticamente. ID: {inspeccion.id}. Evidencias copiadas: {evidencias_copiadas}",
    )

    _crear_notificacion_gestion(
        db,
        item,
        titulo=f"Inspección creada desde reporte: {item.codigo}",
        descripcion=f"Se creó la inspección {inspeccion.codigo} para gestionar el reporte anónimo SST.",
        prioridad=item.prioridad,
    )

    db.commit()
    return ConvertirReporteResponse(ok=True, mensaje="Inspección SST creada correctamente desde el reporte.", reporte_id=item.id, destino_id=inspeccion.id)


@router.post("/{reporte_id}/convertir/hallazgo", response_model=ConvertirReporteResponse)
def crear_hallazgo_desde_reporte(
    reporte_id: int,
    data: WorkflowReporteRequest | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _obtener_reporte(db, reporte_id)
    dias = data.fecha_compromiso_dias if data else 15
    responsable = (data.responsable if data and data.responsable else item.responsable_asignado) or "Responsable SST"

    if not item.inspeccion_id:
        crear_inspeccion_desde_reporte(reporte_id, data, db, usuario)
        db.refresh(item)

    inspeccion = db.query(InspeccionSST).filter(InspeccionSST.id == item.inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="No se encontró la inspección asociada al reporte")

    hallazgo = InspeccionHallazgoSST(
        inspeccion_id=inspeccion.id,
        empresa_id=item.empresa_id,
        descripcion=f"{item.titulo}. {item.descripcion}",
        tipo_hallazgo=item.tipo_reporte,
        nivel_riesgo=_riesgo_desde_prioridad(item.prioridad),
        accion_recomendada="Verificar condición reportada, controlar el riesgo y documentar evidencia de cierre.",
        responsable=responsable,
        fecha_compromiso=_today() + timedelta(days=dias),
        estado="ABIERTO",
        observaciones=f"Hallazgo generado desde reporte anónimo SST {item.codigo}. Ubicación: {item.ubicacion or 'No especificada'}. Evidencias: {len(getattr(item, 'evidencias', []) or []) or ('1' if item.archivo_url else '0')}",
        activo=True,
    )
    db.add(hallazgo)
    db.flush()

    evidencias_hallazgo = _copiar_evidencias_reporte_a_modulo(
        db=db,
        reporte=item,
        modulo="HALLAZGOS",
        referencia_id=hallazgo.id,
        usuario_id=getattr(usuario, "id", None),
        descripcion_extra=f"Hallazgo generado automáticamente desde reporte {item.codigo}.",
    )

    # También garantiza que la inspección asociada conserve las evidencias del reporte.
    evidencias_inspeccion = _copiar_evidencias_reporte_a_modulo(
        db=db,
        reporte=item,
        modulo="INSPECCIONES",
        referencia_id=inspeccion.id,
        usuario_id=getattr(usuario, "id", None),
        descripcion_extra=f"Hallazgo #{hallazgo.id} generado desde reporte {item.codigo}.",
    )

    item.estado = "EN_PROCESO"
    item.trazabilidad = _append_traza(
        item.trazabilidad,
        f"Hallazgo SST creado automáticamente. ID: {hallazgo.id}. Evidencias hallazgo: {evidencias_hallazgo}. Evidencias inspección: {evidencias_inspeccion}",
    )

    _crear_notificacion_gestion(
        db,
        item,
        titulo=f"Hallazgo creado desde reporte: {item.codigo}",
        descripcion=f"Se creó el hallazgo #{hallazgo.id} asociado a la inspección {inspeccion.codigo}.",
        prioridad=item.prioridad,
    )

    db.commit()
    return ConvertirReporteResponse(ok=True, mensaje="Hallazgo SST creado correctamente desde el reporte.", reporte_id=item.id, destino_id=inspeccion.id, hallazgo_id=hallazgo.id)


@router.post("/{reporte_id}/convertir/capa", response_model=ConvertirReporteResponse)
def crear_capa_desde_reporte(
    reporte_id: int,
    data: WorkflowReporteRequest | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = _obtener_reporte(db, reporte_id)
    responsable = (data.responsable if data and data.responsable else item.responsable_asignado) or "Responsable SST"
    dias = data.fecha_compromiso_dias if data else 15

    if item.capa_id:
        return ConvertirReporteResponse(ok=True, mensaje="El reporte ya tiene CAPA asociada.", reporte_id=item.id, capa_id=item.capa_id, destino_id=item.capa_id)

    capa = CapaSST(
        empresa_id=item.empresa_id,
        sede_id=item.sede_id,
        area_id=item.area_id,
        cargo_id=item.cargo_id,
        empleado_id=None,
        usuario_id=getattr(usuario, "id", None),
        inspeccion_id=item.inspeccion_id,
        hallazgo_id=None,
        codigo=_codigo("CAPA-REP"),
        titulo=f"CAPA por reporte anónimo: {item.titulo}"[:255],
        descripcion=item.descripcion,
        tipo_accion="CORRECTIVA" if _upper(item.tipo_reporte) in {"INCIDENTE", "ACCIDENTE", "CONDICION_INSEGURA"} else "PREVENTIVA",
        origen="REPORTE_ANONIMO_SST",
        prioridad=_upper(item.prioridad, "MEDIA"),
        estado="ABIERTA",
        responsable=responsable,
        fecha_apertura=_today(),
        fecha_compromiso=_today() + timedelta(days=dias),
        avance=0,
        causa_raiz="Pendiente por análisis del responsable SST.",
        accion_inmediata=item.accion_inmediata,
        accion_correctiva="Definir e implementar acción correctiva sobre la condición reportada.",
        accion_preventiva="Socializar condición y prevenir recurrencia en áreas similares.",
        observaciones=f"CAPA generada desde reporte anónimo SST {item.codigo}. Ubicación: {item.ubicacion or 'No especificada'}. Evidencias: {len(getattr(item, 'evidencias', []) or []) or ('1' if item.archivo_url else '0')}",
        trazabilidad=_now_line(f"CAPA creada desde reporte anónimo {item.codigo}"),
        activo=True,
    )
    db.add(capa)
    db.flush()

    evidencias_capa = _copiar_evidencias_reporte_a_modulo(
        db=db,
        reporte=item,
        modulo="CAPA",
        referencia_id=capa.id,
        usuario_id=getattr(usuario, "id", None),
        descripcion_extra=f"CAPA generada automáticamente desde reporte {item.codigo}.",
    )

    item.capa_id = capa.id
    item.estado = "EN_PROCESO"
    item.trazabilidad = _append_traza(
        item.trazabilidad,
        f"CAPA creada automáticamente. ID: {capa.id}. Evidencias copiadas: {evidencias_capa}",
    )

    _crear_notificacion_gestion(
        db,
        item,
        titulo=f"CAPA creada desde reporte: {item.codigo}",
        descripcion=f"Se creó la CAPA {capa.codigo} para gestionar el reporte anónimo SST.",
        prioridad=item.prioridad,
    )

    db.commit()
    return ConvertirReporteResponse(ok=True, mensaje="CAPA creada correctamente desde el reporte.", reporte_id=item.id, destino_id=capa.id, capa_id=capa.id)


@router.delete("/{reporte_id}")
def eliminar_reporte_anonimo(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ADMIN)),
):
    item = _obtener_reporte(db, reporte_id)
    item.activo = False
    item.estado = "ANULADO"
    item.fecha_cierre = datetime.utcnow()
    item.trazabilidad = _append_traza(item.trazabilidad, "Reporte desactivado desde administración")
    db.commit()
    return {"ok": True, "mensaje": "Reporte anónimo SST desactivado correctamente"}
