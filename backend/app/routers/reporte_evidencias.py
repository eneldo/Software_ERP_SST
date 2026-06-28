# ============================================================
# ROUTER EVIDENCIAS INTELIGENTES REPORTES SST - ERP SST PRO
# FASE 1.1.25.6
# Archivo: backend/app/routers/reporte_evidencias.py
# ============================================================

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.reporte_evidencia_sst import ReporteEvidenciaSST
from app.models.reporte_inseguridad import ReporteInseguridadSST
from app.schemas.reporte_evidencia_schema import (
    ReporteEvidenciaDashboardResponse,
    ReporteEvidenciaResponse,
    ReporteTimelineItem,
)
from app.services.reporte_evidencia_service import guardar_evidencias_reporte, sincronizar_evidencia_legado

router = APIRouter(prefix="/reportes-evidencias", tags=["Evidencias Reportes SST"])
ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


def _obtener_reporte(db: Session, reporte_id: int) -> ReporteInseguridadSST:
    reporte = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.id == reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte SST no encontrado")
    return reporte


@router.get("/reporte/{reporte_id}", response_model=list[ReporteEvidenciaResponse])
def listar_evidencias_reporte(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    reporte = _obtener_reporte(db, reporte_id)
    if reporte.archivo_url:
        sincronizar_evidencia_legado(db, reporte)
        db.commit()
    return db.query(ReporteEvidenciaSST).filter(
        ReporteEvidenciaSST.reporte_id == reporte_id,
        ReporteEvidenciaSST.activo.is_(True),
    ).order_by(ReporteEvidenciaSST.fecha_creacion.desc(), ReporteEvidenciaSST.id.desc()).all()


@router.post("/reporte/{reporte_id}", response_model=list[ReporteEvidenciaResponse])
def subir_evidencias_reporte(
    reporte_id: int,
    archivos: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    reporte = _obtener_reporte(db, reporte_id)
    evidencias = guardar_evidencias_reporte(db, reporte, archivos, descripcion_base=f"{reporte.titulo} {reporte.descripcion} {reporte.ubicacion}")
    reporte.trazabilidad = f"{reporte.trazabilidad or ''}\n[{datetime.utcnow().isoformat()}] {len(evidencias)} evidencia(s) cargada(s) desde gestión SST.".strip()
    db.commit()
    for ev in evidencias:
        db.refresh(ev)
    return evidencias


@router.delete("/{evidencia_id}")
def eliminar_evidencia_reporte(
    evidencia_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    ev = db.query(ReporteEvidenciaSST).filter(ReporteEvidenciaSST.id == evidencia_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    ev.activo = False
    ev.fecha_actualizacion = datetime.utcnow()
    reporte = db.query(ReporteInseguridadSST).filter(ReporteInseguridadSST.id == ev.reporte_id).first()
    if reporte:
        reporte.trazabilidad = f"{reporte.trazabilidad or ''}\n[{datetime.utcnow().isoformat()}] Evidencia #{ev.id} desactivada.".strip()
    db.commit()
    return {"ok": True, "mensaje": "Evidencia desactivada correctamente"}


@router.get("/dashboard", response_model=ReporteEvidenciaDashboardResponse)
def dashboard_evidencias_reportes(
    empresa_id: int | None = None,
    area_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = db.query(ReporteEvidenciaSST).join(ReporteInseguridadSST, ReporteEvidenciaSST.reporte_id == ReporteInseguridadSST.id).filter(ReporteEvidenciaSST.activo.is_(True))
    if empresa_id:
        query = query.filter(ReporteInseguridadSST.empresa_id == empresa_id)
    if area_id:
        query = query.filter(ReporteInseguridadSST.area_id == area_id)
    evidencias = query.all()

    por_tipo: dict[str, int] = {}
    por_categoria: dict[str, int] = {}
    peso_original = 0
    peso_optimizado = 0
    for ev in evidencias:
        tipo = ev.tipo_archivo or "OTRO"
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        cat = ev.categoria_ia or "SIN_CLASIFICAR"
        por_categoria[cat] = por_categoria.get(cat, 0) + 1
        peso_original += int(ev.peso_original_bytes or 0)
        peso_optimizado += int(ev.peso_optimizado_bytes or 0)

    ahorro = max(peso_original - peso_optimizado, 0)
    return ReporteEvidenciaDashboardResponse(
        total=len(evidencias),
        imagenes=por_tipo.get("IMAGEN", 0),
        videos=por_tipo.get("VIDEO", 0),
        pdf=por_tipo.get("PDF", 0),
        audios=por_tipo.get("AUDIO", 0),
        otros=por_tipo.get("OTRO", 0),
        peso_original_bytes=peso_original,
        peso_optimizado_bytes=peso_optimizado,
        ahorro_bytes=ahorro,
        ahorro_porcentaje=round((ahorro / peso_original) * 100, 2) if peso_original else 0,
        por_categoria_ia=por_categoria,
        por_tipo_archivo=por_tipo,
    )


@router.get("/reporte/{reporte_id}/timeline", response_model=list[ReporteTimelineItem])
def timeline_reporte(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    reporte = _obtener_reporte(db, reporte_id)
    evidencias = db.query(ReporteEvidenciaSST).filter(
        ReporteEvidenciaSST.reporte_id == reporte_id,
        ReporteEvidenciaSST.activo.is_(True),
    ).order_by(ReporteEvidenciaSST.fecha_creacion.asc()).all()
    items = [ReporteTimelineItem(fecha=reporte.fecha_reporte, tipo="REPORTE", titulo="Reporte recibido", descripcion=reporte.codigo, icono="alerta")]
    for ev in evidencias:
        items.append(ReporteTimelineItem(fecha=ev.fecha_creacion, tipo="EVIDENCIA", titulo=f"Evidencia {ev.tipo_archivo}", descripcion=ev.archivo_nombre, icono="archivo"))
    if reporte.responsable_asignado:
        items.append(ReporteTimelineItem(fecha=reporte.fecha_actualizacion or reporte.fecha_reporte, tipo="ASIGNACION", titulo="Responsable asignado", descripcion=reporte.responsable_asignado, icono="usuario"))
    if reporte.inspeccion_id:
        items.append(ReporteTimelineItem(fecha=reporte.fecha_actualizacion or reporte.fecha_reporte, tipo="INSPECCION", titulo="Inspección asociada", descripcion=f"Inspección ID {reporte.inspeccion_id}", icono="inspeccion"))
    if reporte.capa_id:
        items.append(ReporteTimelineItem(fecha=reporte.fecha_actualizacion or reporte.fecha_reporte, tipo="CAPA", titulo="CAPA asociada", descripcion=f"CAPA ID {reporte.capa_id}", icono="capa"))
    if reporte.estado in {"CERRADO", "ANULADO"}:
        items.append(ReporteTimelineItem(fecha=reporte.fecha_cierre, tipo="CIERRE", titulo=f"Reporte {reporte.estado}", descripcion=reporte.accion_inmediata, icono="cierre"))
    return sorted(items, key=lambda x: x.fecha or datetime.utcnow())
