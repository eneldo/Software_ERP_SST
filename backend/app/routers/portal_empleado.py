# ============================================================
# ROUTER PORTAL DEL EMPLEADO SST - ERP SST PRO
# FASE 1.1.25.1 — BACKEND PORTAL DEL EMPLEADO SST
# Archivo: backend/app/routers/portal_empleado.py
# ============================================================

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_roles
from app.core.file_security import validate_upload
from app.database import get_db
from app.models.capacitacion import CapacitacionAsistenteSST, CapacitacionSST
from app.models.empleado import Empleado
from app.models.epp import EPPEntrega
from app.models.examen_medico import ExamenMedico
from app.models.reporte_inseguridad import ReporteInseguridadSST
from app.schemas.reporte_inseguridad_schema import (
    PortalEmpleadoDashboardResponse,
    PortalEmpleadoResumenResponse,
    ReporteInseguridadCreate,
    ReporteInseguridadEstadoUpdate,
    ReporteInseguridadResponse,
    ReporteInseguridadUpdate,
)

router = APIRouter(prefix="/portal-empleado", tags=["Portal del Empleado SST"])

ROLES_PORTAL = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "EMPLEADO", "TRABAJADOR"]
ROLES_GESTION = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]

UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()
REPORTES_UPLOAD_DIR = UPLOAD_ROOT / "portal-empleado" / "reportes"
REPORTES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {"pdf", "jpg", "jpeg", "png", "webp", "mp4", "mov"}
ALLOWED_MIME_PREFIX = ("image/", "application/pdf", "video/")
MAX_UPLOAD_MB = 25


def _public_upload_url(file_path: Path) -> str:
    try:
        rel = file_path.resolve().relative_to(UPLOAD_ROOT)
        return "/uploads/" + rel.as_posix()
    except Exception:
        return "/uploads/portal-empleado/reportes/" + file_path.name


def _guardar_upload(upload: UploadFile) -> dict[str, Any]:
    validation = validate_upload(upload, allowed_extensions={f".{item}" for item in ALLOWED_EXT}, max_size_mb=MAX_UPLOAD_MB)
    original = validation.safe_filename or "evidencia_reporte"
    extension = validation.extension.lstrip(".")
    content = validation.content
    mime_type = validation.mime_type

    filename = f"{uuid.uuid4().hex}.{extension}"
    path = REPORTES_UPLOAD_DIR / filename
    path.write_bytes(content)

    return {
        "archivo_url": _public_upload_url(path),
        "archivo_nombre": original,
        "archivo_mime_type": mime_type,
        "archivo_tamano_bytes": len(content),
    }

def _codigo_reporte() -> str:
    return f"REP-SST-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def _usuario_id(usuario) -> int | None:
    return getattr(usuario, "id", None) or getattr(usuario, "user_id", None)


def _usuario_correo(usuario) -> str | None:
    return getattr(usuario, "correo", None) or getattr(usuario, "email", None)


def _usuario_empresa_id(usuario) -> int | None:
    return getattr(usuario, "empresa_id", None)


def _buscar_empleado_contexto(db: Session, usuario, empleado_id: int | None = None) -> Empleado | None:
    if empleado_id:
        return db.query(Empleado).filter(Empleado.id == empleado_id).first()

    correo = _usuario_correo(usuario)
    if correo:
        empleado = db.query(Empleado).filter(func.lower(Empleado.correo) == correo.lower()).first()
        if empleado:
            return empleado

    empresa_id = _usuario_empresa_id(usuario)
    if empresa_id:
        # Fallback seguro para pruebas: primer empleado activo de la empresa.
        return db.query(Empleado).filter(Empleado.empresa_id == empresa_id, Empleado.activo == True).order_by(Empleado.id.asc()).first()

    return None


def _empleado_dict(empleado: Empleado | None) -> dict:
    if not empleado:
        return {}
    return {
        "id": empleado.id,
        "nombres": empleado.nombres,
        "apellidos": empleado.apellidos,
        "nombre_completo": f"{empleado.nombres or ''} {empleado.apellidos or ''}".strip(),
        "documento": empleado.documento,
        "correo": empleado.correo,
        "empresa_id": empleado.empresa_id,
        "sede_id": empleado.sede_id,
        "area_id": empleado.area_id,
        "cargo_id": empleado.cargo_id,
        "empresa_nombre": empleado.empresa.nombre if empleado.empresa else None,
        "sede_nombre": empleado.sede.nombre if empleado.sede else None,
        "area_nombre": empleado.area.nombre if empleado.area else None,
        "cargo_nombre": empleado.cargo.nombre if empleado.cargo else None,
    }


def _reporte_to_response(item: ReporteInseguridadSST) -> ReporteInseguridadResponse:
    empleado_nombre = None
    empleado_documento = None
    empleado_correo = None
    if item.empleado:
        empleado_nombre = f"{item.empleado.nombres or ''} {item.empleado.apellidos or ''}".strip()
        empleado_documento = item.empleado.documento
        empleado_correo = item.empleado.correo

    return ReporteInseguridadResponse(
        id=item.id,
        empresa_id=item.empresa_id,
        sede_id=item.sede_id,
        area_id=item.area_id,
        cargo_id=item.cargo_id,
        empleado_id=item.empleado_id,
        usuario_id=item.usuario_id,
        codigo=item.codigo,
        tipo_reporte=item.tipo_reporte,
        prioridad=item.prioridad,
        estado=item.estado,
        titulo=item.titulo,
        descripcion=item.descripcion,
        ubicacion=item.ubicacion,
        responsable_asignado=item.responsable_asignado,
        accion_inmediata=item.accion_inmediata,
        observaciones=item.observaciones,
        origen=item.origen,
        genera_notificacion=item.genera_notificacion,
        activo=item.activo,
        archivo_url=item.archivo_url,
        archivo_nombre=item.archivo_nombre,
        archivo_mime_type=item.archivo_mime_type,
        archivo_tamano_bytes=item.archivo_tamano_bytes,
        convertido_a_inspeccion=item.convertido_a_inspeccion,
        inspeccion_id=item.inspeccion_id,
        capa_id=item.capa_id,
        incidente_id=item.incidente_id,
        fecha_reporte=item.fecha_reporte,
        fecha_cierre=item.fecha_cierre,
        fecha_creacion=item.fecha_creacion,
        fecha_actualizacion=item.fecha_actualizacion,
        empresa_nombre=item.empresa.nombre if item.empresa else None,
        sede_nombre=item.sede.nombre if item.sede else None,
        area_nombre=item.area.nombre if item.area else None,
        cargo_nombre=item.cargo.nombre if item.cargo else None,
        empleado_nombre=empleado_nombre,
        empleado_documento=empleado_documento,
        empleado_correo=empleado_correo,
    )


def _crear_notificacion_segura(db: Session, reporte: ReporteInseguridadSST) -> None:
    """
    Integra con la FASE 1.1.24 si la tabla notificaciones_sst existe.
    Si el módulo de notificaciones no está instalado o tiene otra estructura,
    no rompe el Portal del Empleado.
    """
    if not reporte.genera_notificacion:
        return

    prioridad = "CRITICA" if reporte.tipo_reporte == "ACCIDENTE" else reporte.prioridad
    try:
        db.execute(
            text(
                """
                INSERT INTO notificaciones_sst
                (empresa_id, modulo, tipo, prioridad, titulo, descripcion, url_destino, leida, fecha_evento, fecha_creacion)
                VALUES
                (:empresa_id, :modulo, :tipo, :prioridad, :titulo, :descripcion, :url_destino, false, NOW(), NOW())
                """
            ),
            {
                "empresa_id": reporte.empresa_id,
                "modulo": "PORTAL_EMPLEADO",
                "tipo": reporte.tipo_reporte,
                "prioridad": prioridad,
                "titulo": f"Nuevo reporte SST: {reporte.titulo}",
                "descripcion": f"{reporte.codigo} · {reporte.tipo_reporte} · {reporte.descripcion[:450]}",
                "url_destino": f"/portal-empleado/reportes/{reporte.id}",
            },
        )
    except Exception:
        # No interrumpe el flujo si no está el módulo 1.1.24 o la estructura cambió.
        pass


def _asegurar_contexto_reporte(db: Session, usuario, payload: dict) -> dict:
    empleado = _buscar_empleado_contexto(db, usuario, payload.get("empleado_id"))

    if empleado:
        payload["empleado_id"] = payload.get("empleado_id") or empleado.id
        payload["empresa_id"] = payload.get("empresa_id") or empleado.empresa_id
        payload["sede_id"] = payload.get("sede_id") or empleado.sede_id
        payload["area_id"] = payload.get("area_id") or empleado.area_id
        payload["cargo_id"] = payload.get("cargo_id") or empleado.cargo_id

    payload["empresa_id"] = payload.get("empresa_id") or _usuario_empresa_id(usuario)
    if not payload.get("empresa_id"):
        raise HTTPException(status_code=400, detail="No fue posible identificar la empresa del reporte")

    payload["usuario_id"] = _usuario_id(usuario)
    payload["codigo"] = payload.get("codigo") or _codigo_reporte()
    payload["estado"] = payload.get("estado") or "REPORTADO"
    payload["origen"] = payload.get("origen") or "PORTAL_EMPLEADO"
    return payload


@router.get("/mi-perfil")
def mi_perfil(
    empleado_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    empleado = _buscar_empleado_contexto(db, usuario, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no asociado al usuario actual")
    return _empleado_dict(empleado)


@router.get("/dashboard", response_model=PortalEmpleadoDashboardResponse)
def dashboard_portal_empleado(
    empleado_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    empleado = _buscar_empleado_contexto(db, usuario, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no asociado al usuario actual")

    reportes_q = db.query(ReporteInseguridadSST).filter(
        ReporteInseguridadSST.empleado_id == empleado.id,
        ReporteInseguridadSST.activo == True,
    )
    reportes = reportes_q.order_by(ReporteInseguridadSST.id.desc()).limit(5).all()

    capacitaciones = db.query(CapacitacionAsistenteSST).filter(
        CapacitacionAsistenteSST.empleado_id == empleado.id,
        CapacitacionAsistenteSST.activo == True,
    ).count()
    epp = db.query(EPPEntrega).filter(
        EPPEntrega.empleado_id == empleado.id,
        EPPEntrega.activo == True,
    ).count()
    examenes = db.query(ExamenMedico).filter(
        ExamenMedico.empleado_id == empleado.id,
        ExamenMedico.activo == True,
    ).count()
    reportes_abiertos = reportes_q.filter(ReporteInseguridadSST.estado != "CERRADO").count()

    alertas = []
    if reportes_abiertos:
        alertas.append(f"Tienes {reportes_abiertos} reporte(s) SST pendiente(s) de cierre.")
    if not capacitaciones:
        alertas.append("No tienes capacitaciones registradas en el portal.")
    if not epp:
        alertas.append("No tienes entregas EPP registradas.")
    if not alertas:
        alertas.append("Tu portal SST está al día. Mantén participación preventiva.")

    return PortalEmpleadoDashboardResponse(
        empleado=_empleado_dict(empleado),
        kpis={
            "capacitaciones": capacitaciones,
            "epp_entregados": epp,
            "examenes": examenes,
            "reportes": reportes_q.count(),
            "reportes_abiertos": reportes_abiertos,
        },
        reportes_recientes=[_reporte_to_response(r) for r in reportes],
        alertas=alertas,
    )


@router.get("/mis-capacitaciones")
def mis_capacitaciones(
    empleado_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    empleado = _buscar_empleado_contexto(db, usuario, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no asociado al usuario actual")

    items = db.query(CapacitacionAsistenteSST).options(joinedload(CapacitacionAsistenteSST.capacitacion)).filter(
        CapacitacionAsistenteSST.empleado_id == empleado.id,
        CapacitacionAsistenteSST.activo == True,
    ).order_by(CapacitacionAsistenteSST.id.desc()).all()

    return [
        {
            "id": i.id,
            "capacitacion_id": i.capacitacion_id,
            "codigo": i.capacitacion.codigo if i.capacitacion else None,
            "nombre": i.capacitacion.nombre if i.capacitacion else None,
            "tema": i.capacitacion.tema if i.capacitacion else None,
            "fecha_programada": i.capacitacion.fecha_programada.isoformat() if i.capacitacion and i.capacitacion.fecha_programada else None,
            "fecha_ejecucion": i.capacitacion.fecha_ejecucion.isoformat() if i.capacitacion and i.capacitacion.fecha_ejecucion else None,
            "asistio": i.asistio,
            "evaluacion": float(i.evaluacion or 0),
            "certificado_generado": i.certificado_generado,
        }
        for i in items
    ]


@router.get("/mis-epp")
def mis_epp(
    empleado_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    empleado = _buscar_empleado_contexto(db, usuario, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no asociado al usuario actual")

    items = db.query(EPPEntrega).options(joinedload(EPPEntrega.epp)).filter(
        EPPEntrega.empleado_id == empleado.id,
        EPPEntrega.activo == True,
    ).order_by(EPPEntrega.id.desc()).all()

    return [
        {
            "id": i.id,
            "epp_id": i.epp_id,
            "codigo": i.epp.codigo if i.epp else None,
            "nombre": i.epp.nombre if i.epp else None,
            "categoria": i.epp.categoria if i.epp else None,
            "cantidad": i.cantidad,
            "fecha_entrega": i.fecha_entrega.isoformat() if i.fecha_entrega else None,
            "fecha_reposicion": i.fecha_reposicion.isoformat() if i.fecha_reposicion else None,
            "estado": i.estado,
            "recibido_por_empleado": i.recibido_por_empleado,
            "fecha_firma": i.fecha_firma.isoformat() if i.fecha_firma else None,
        }
        for i in items
    ]


@router.get("/mis-examenes")
def mis_examenes(
    empleado_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    empleado = _buscar_empleado_contexto(db, usuario, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no asociado al usuario actual")

    items = db.query(ExamenMedico).filter(
        ExamenMedico.empleado_id == empleado.id,
        ExamenMedico.activo == True,
    ).order_by(ExamenMedico.id.desc()).all()

    return [
        {
            "id": i.id,
            "tipo_examen": i.tipo_examen,
            "fecha_examen": i.fecha_examen.isoformat() if i.fecha_examen else None,
            "fecha_vencimiento": i.fecha_vencimiento.isoformat() if i.fecha_vencimiento else None,
            "concepto": i.concepto,
            "restricciones": i.restricciones,
            "estado": i.estado,
            "entidad_salud": i.entidad_salud,
        }
        for i in items
    ]


@router.get("/resumen", response_model=PortalEmpleadoResumenResponse)
def resumen_portal_empleado(
    empleado_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    return PortalEmpleadoResumenResponse(
        capacitaciones=mis_capacitaciones(empleado_id, db, usuario),
        epp=mis_epp(empleado_id, db, usuario),
        examenes=mis_examenes(empleado_id, db, usuario),
        reportes=listar_reportes_empleado(empleado_id, None, None, None, None, None, db, usuario),
    )


@router.get("/reportes", response_model=list[ReporteInseguridadResponse])
def listar_reportes_empleado(
    empleado_id: int | None = Query(default=None),
    empresa_id: int | None = Query(default=None),
    tipo_reporte: str | None = Query(default=None),
    prioridad: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    buscar: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    empleado = _buscar_empleado_contexto(db, usuario, empleado_id)
    query = db.query(ReporteInseguridadSST).options(
        joinedload(ReporteInseguridadSST.empresa),
        joinedload(ReporteInseguridadSST.sede),
        joinedload(ReporteInseguridadSST.area),
        joinedload(ReporteInseguridadSST.cargo),
        joinedload(ReporteInseguridadSST.empleado),
    ).filter(ReporteInseguridadSST.activo == True)

    rol = str(getattr(usuario, "rol", "")).upper()
    if rol in {"EMPLEADO", "TRABAJADOR"} and empleado:
        query = query.filter(ReporteInseguridadSST.empleado_id == empleado.id)
    elif empleado_id:
        query = query.filter(ReporteInseguridadSST.empleado_id == empleado_id)
    elif empresa_id:
        query = query.filter(ReporteInseguridadSST.empresa_id == empresa_id)
    elif _usuario_empresa_id(usuario):
        query = query.filter(ReporteInseguridadSST.empresa_id == _usuario_empresa_id(usuario))

    if tipo_reporte:
        query = query.filter(func.upper(ReporteInseguridadSST.tipo_reporte) == tipo_reporte.upper())
    if prioridad:
        query = query.filter(func.upper(ReporteInseguridadSST.prioridad) == prioridad.upper())
    if estado:
        query = query.filter(func.upper(ReporteInseguridadSST.estado) == estado.upper())
    if buscar:
        q = f"%{buscar.lower()}%"
        query = query.filter(or_(
            func.lower(ReporteInseguridadSST.codigo).like(q),
            func.lower(ReporteInseguridadSST.titulo).like(q),
            func.lower(ReporteInseguridadSST.descripcion).like(q),
            func.lower(ReporteInseguridadSST.ubicacion).like(q),
        ))

    items = query.order_by(ReporteInseguridadSST.id.desc()).all()
    return [_reporte_to_response(i) for i in items]


@router.get("/reportes/{reporte_id}", response_model=ReporteInseguridadResponse)
def obtener_reporte_empleado(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    item = db.query(ReporteInseguridadSST).options(
        joinedload(ReporteInseguridadSST.empresa),
        joinedload(ReporteInseguridadSST.sede),
        joinedload(ReporteInseguridadSST.area),
        joinedload(ReporteInseguridadSST.cargo),
        joinedload(ReporteInseguridadSST.empleado),
    ).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Reporte SST no encontrado")
    return _reporte_to_response(item)


@router.post("/reportes", response_model=ReporteInseguridadResponse)
def crear_reporte_empleado(
    data: ReporteInseguridadCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    payload = _asegurar_contexto_reporte(db, usuario, data.model_dump())
    item = ReporteInseguridadSST(**payload)
    item.trazabilidad = f"[{datetime.utcnow().isoformat()}] Reporte creado desde Portal Empleado por usuario {_usuario_id(usuario)}."
    db.add(item)
    db.commit()
    db.refresh(item)
    _crear_notificacion_segura(db, item)
    db.commit()
    db.refresh(item)
    return obtener_reporte_empleado(item.id, db, usuario)


@router.post("/reportes/form", response_model=ReporteInseguridadResponse)
def crear_reporte_empleado_form(
    tipo_reporte: str = Form(default="CONDICION_INSEGURA"),
    prioridad: str = Form(default="MEDIA"),
    titulo: str = Form(...),
    descripcion: str = Form(...),
    ubicacion: str | None = Form(default=None),
    empleado_id: int | None = Form(default=None),
    empresa_id: int | None = Form(default=None),
    sede_id: int | None = Form(default=None),
    area_id: int | None = Form(default=None),
    cargo_id: int | None = Form(default=None),
    accion_inmediata: str | None = Form(default=None),
    observaciones: str | None = Form(default=None),
    archivo: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    data = ReporteInseguridadCreate(
        empleado_id=empleado_id,
        empresa_id=empresa_id,
        sede_id=sede_id,
        area_id=area_id,
        cargo_id=cargo_id,
        tipo_reporte=tipo_reporte,
        prioridad=prioridad,
        titulo=titulo,
        descripcion=descripcion,
        ubicacion=ubicacion,
        accion_inmediata=accion_inmediata,
        observaciones=observaciones,
    )
    payload = _asegurar_contexto_reporte(db, usuario, data.model_dump())
    if archivo:
        payload.update(_guardar_upload(archivo))

    item = ReporteInseguridadSST(**payload)
    item.trazabilidad = f"[{datetime.utcnow().isoformat()}] Reporte creado con formulario/evidencia desde Portal Empleado por usuario {_usuario_id(usuario)}."
    db.add(item)
    db.commit()
    db.refresh(item)
    _crear_notificacion_segura(db, item)
    db.commit()
    db.refresh(item)
    return obtener_reporte_empleado(item.id, db, usuario)


@router.post("/reportes/{reporte_id}/evidencia", response_model=ReporteInseguridadResponse)
def subir_evidencia_reporte(
    reporte_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PORTAL)),
):
    item = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Reporte SST no encontrado")
    if item.estado == "CERRADO":
        raise HTTPException(status_code=400, detail="El reporte está cerrado y no permite nuevas evidencias")

    datos_archivo = _guardar_upload(archivo)
    for key, value in datos_archivo.items():
        setattr(item, key, value)
    item.trazabilidad = (item.trazabilidad + "\n" if item.trazabilidad else "") + f"[{datetime.utcnow().isoformat()}] Evidencia cargada por usuario {_usuario_id(usuario)}."
    db.commit()
    db.refresh(item)
    return obtener_reporte_empleado(item.id, db, usuario)


@router.put("/reportes/{reporte_id}", response_model=ReporteInseguridadResponse)
def actualizar_reporte_empleado(
    reporte_id: int,
    data: ReporteInseguridadUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_GESTION)),
):
    item = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Reporte SST no encontrado")
    if item.estado == "CERRADO":
        raise HTTPException(status_code=400, detail="El reporte está cerrado y no puede modificarse")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    item.trazabilidad = (item.trazabilidad + "\n" if item.trazabilidad else "") + f"[{datetime.utcnow().isoformat()}] Reporte actualizado por usuario {_usuario_id(usuario)}."
    db.commit()
    db.refresh(item)
    return obtener_reporte_empleado(item.id, db, usuario)


@router.patch("/reportes/{reporte_id}/estado", response_model=ReporteInseguridadResponse)
def cambiar_estado_reporte(
    reporte_id: int,
    data: ReporteInseguridadEstadoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_GESTION)),
):
    item = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Reporte SST no encontrado")

    item.estado = data.estado
    if data.responsable_asignado is not None:
        item.responsable_asignado = data.responsable_asignado
    if data.observaciones:
        item.observaciones = ((item.observaciones or "") + f"\n{data.observaciones}").strip()
    if data.estado == "CERRADO" and not item.fecha_cierre:
        item.fecha_cierre = datetime.utcnow()

    item.trazabilidad = (item.trazabilidad + "\n" if item.trazabilidad else "") + f"[{datetime.utcnow().isoformat()}] Estado cambiado a {data.estado} por usuario {_usuario_id(usuario)}."
    db.commit()
    db.refresh(item)
    return obtener_reporte_empleado(item.id, db, usuario)


@router.delete("/reportes/{reporte_id}")
def eliminar_reporte_empleado(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_GESTION)),
):
    item = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Reporte SST no encontrado")
    item.activo = False
    item.estado = "ANULADO"
    item.trazabilidad = (item.trazabilidad + "\n" if item.trazabilidad else "") + f"[{datetime.utcnow().isoformat()}] Reporte anulado por usuario {_usuario_id(usuario)}."
    db.commit()
    return {"ok": True, "message": "Reporte SST anulado", "reporte_id": reporte_id}
