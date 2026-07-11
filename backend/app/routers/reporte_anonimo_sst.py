from __future__ import annotations

import logging
import os
import uuid
from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.area import Area
from app.models.empresa import Empresa
from app.models.notificacion_sst import NotificacionSST
from app.models.reporte_inseguridad import ReporteInseguridadSST
from app.schemas.reporte_anonimo_sst_schema import ReporteAnonimoSSTPublicResponse
from app.services.reporte_evidencia_service import guardar_evidencias_reporte

logger = logging.getLogger("app.reportes_anonimos")

router = APIRouter(prefix="/reporte-anonimo-sst", tags=["Reporte Anonimo SST Publico"])

UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()
DEFAULT_EMPRESA_ID = int(os.getenv("REPORTE_ANONIMO_EMPRESA_ID", "1"))
MAX_PUBLIC_FILES = int(os.getenv("REPORTE_ANONIMO_MAX_ARCHIVOS", "5"))


def _clean_upper(value: str | None, default: str) -> str:
    value = str(value or "").strip().upper()
    return value or default


def _empresa_default(db: Session) -> Empresa:
    empresa = db.query(Empresa).filter(Empresa.id == DEFAULT_EMPRESA_ID).first()
    if empresa:
        return empresa
    empresa = db.query(Empresa).order_by(Empresa.id.asc()).first()
    if empresa:
        return empresa
    raise HTTPException(status_code=400, detail="No existe empresa configurada para recibir reportes anonimos SST.")


def _validar_area(db: Session, empresa_id: int, area_id: int | None):
    if not area_id:
        return None
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area no encontrada")
    if area.empresa_id != empresa_id:
        raise HTTPException(status_code=400, detail="El area no pertenece a la empresa configurada")
    return area


def _codigo_reporte() -> str:
    return f"RAN-SST-{uuid.uuid4().hex[:8].upper()}"


def _crear_notificacion(db: Session, reporte: ReporteInseguridadSST):
    prioridad = _clean_upper(reporte.prioridad, "MEDIA")
    tipo_reporte = _clean_upper(reporte.tipo_reporte, "CONDICION_INSEGURA")
    fecha_evento = None
    if reporte.fecha_reporte:
        try:
            fecha_evento = reporte.fecha_reporte.date()
        except Exception:
            fecha_evento = date.today()

    noti = NotificacionSST(
        empresa_id=reporte.empresa_id,
        sede_id=None,
        area_id=reporte.area_id,
        usuario_id=None,
        modulo="REPORTE_ANONIMO_SST",
        referencia_id=reporte.id,
        clave_unica=f"REPORTE-ANONIMO-{reporte.id}",
        tipo="ALERTA",
        prioridad=prioridad,
        estado="PENDIENTE",
        titulo=f"Reporte anonimo SST: {reporte.titulo}",
        descripcion=f"{tipo_reporte}. Ubicacion: {reporte.ubicacion or 'No especificada'}. {reporte.descripcion}",
        accion_recomendada=(
            "Revisar el reporte anonimo, validar la condicion y definir si genera "
            "inspeccion, hallazgo, incidente o CAPA."
        ),
        url_destino="/verificar/reportes-anonimos",
        fecha_evento=fecha_evento,
        fecha_vencimiento=None,
        leida=False,
        archivada=False,
        activa=True,
        origen_generacion="REPORTE_ANONIMO_QR",
        metadata_json=f'{{"reporte_id": {reporte.id}, "codigo": "{reporte.codigo}", "tipo_reporte": "{tipo_reporte}"}}',
    )
    db.add(noti)


@router.get("/opciones")
def opciones_publicas(db: Session = Depends(get_db)):
    empresa = _empresa_default(db)
    areas = db.query(Area).filter(Area.empresa_id == empresa.id).order_by(Area.nombre.asc()).all()
    return {
        "empresa_default": {"id": empresa.id, "nombre": empresa.nombre},
        "areas": [{"id": area.id, "empresa_id": area.empresa_id, "nombre": area.nombre} for area in areas],
        "tipos": ["ACTO_INSEGURO", "CONDICION_INSEGURA", "INCIDENTE", "ACCIDENTE", "SUGERENCIA"],
        "prioridades": ["BAJA", "MEDIA", "ALTA", "CRITICA"],
        "mensaje": "Reporte publico configurado sin seleccion de empresa ni sede.",
    }


@router.post("/reportes", response_model=ReporteAnonimoSSTPublicResponse)
def crear_reporte_anonimo(
    request: Request,
    area_id: int | None = Form(default=None),
    tipo: str = Form(default="CONDICION_INSEGURA"),
    prioridad: str = Form(default="MEDIA"),
    ubicacion: str = Form(...),
    titulo: str = Form(...),
    descripcion: str = Form(...),
    accion_inmediata: str | None = Form(default=None),
    observaciones: str | None = Form(default=None),
    nombre_reportante: str | None = Form(default=None),
    telefono_reportante: str | None = Form(default=None),
    correo_reportante: str | None = Form(default=None),
    archivo: UploadFile | None = File(default=None),
    archivos: list[UploadFile] | None = File(default=None),
    db: Session = Depends(get_db),
):
    _ = request

    if len((descripcion or "").strip()) < 10:
        raise HTTPException(status_code=422, detail="La descripcion debe tener minimo 10 caracteres")
    if len((descripcion or "").strip()) > 700:
        raise HTTPException(status_code=422, detail="La descripcion no puede superar los 700 caracteres")
    if len((ubicacion or "").strip()) < 3:
        raise HTTPException(status_code=422, detail="La ubicacion es obligatoria")
    if len((titulo or "").strip()) < 3:
        raise HTTPException(status_code=422, detail="El titulo del reporte es obligatorio")

    empresa = _empresa_default(db)
    _validar_area(db, empresa.id, area_id)

    obs_extra = []
    if observaciones:
        obs_extra.append(observaciones.strip())
    if nombre_reportante or telefono_reportante or correo_reportante:
        obs_extra.append(
            "Datos opcionales del reportante: "
            f"Nombre: {(nombre_reportante or 'No suministrado').strip()} | "
            f"Telefono: {(telefono_reportante or 'No suministrado').strip()} | "
            f"Correo: {(correo_reportante or 'No suministrado').strip()}"
        )

    fecha_actual = datetime.utcnow()
    reporte = ReporteInseguridadSST(
        codigo=_codigo_reporte(),
        empresa_id=empresa.id,
        sede_id=None,
        area_id=area_id,
        cargo_id=None,
        empleado_id=None,
        usuario_id=None,
        tipo_reporte=_clean_upper(tipo, "CONDICION_INSEGURA"),
        prioridad=_clean_upper(prioridad, "MEDIA"),
        estado="REPORTADO",
        titulo=titulo.strip(),
        descripcion=descripcion.strip(),
        ubicacion=ubicacion.strip(),
        responsable_asignado=None,
        accion_inmediata=(accion_inmediata or "").strip() or None,
        observaciones="\n".join(obs_extra) if obs_extra else None,
        trazabilidad=f"[{fecha_actual.isoformat()}] Reporte anonimo SST recibido desde link publico/QR.",
        origen="REPORTE_ANONIMO_QR",
        genera_notificacion=True,
        convertido_a_inspeccion=False,
        inspeccion_id=None,
        capa_id=None,
        incidente_id=None,
        activo=True,
        fecha_reporte=fecha_actual,
    )

    try:
        db.add(reporte)
        db.flush()
        lista_archivos = []
        if archivo and archivo.filename:
            lista_archivos.append(archivo)
        if archivos:
            lista_archivos.extend([a for a in archivos if a and a.filename])
        if len(lista_archivos) > MAX_PUBLIC_FILES:
            raise HTTPException(status_code=422, detail=f"Maximo {MAX_PUBLIC_FILES} archivo(s) por reporte")
        evidencias = guardar_evidencias_reporte(db, reporte, lista_archivos, descripcion_base=f"{titulo} {descripcion} {ubicacion}")
        if evidencias:
            reporte.trazabilidad = (
                f"{reporte.trazabilidad}\n"
                f"[{fecha_actual.isoformat()}] {len(evidencias)} evidencia(s) inteligente(s) cargada(s)."
            )
        _crear_notificacion(db, reporte)
        db.commit()
        db.refresh(reporte)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Error guardando reporte anonimo SST")
        raise HTTPException(status_code=500, detail="No fue posible guardar el reporte SST.") from exc

    return ReporteAnonimoSSTPublicResponse(
        ok=True,
        mensaje="Reporte SST recibido correctamente. El equipo SST revisara la informacion.",
        codigo=reporte.codigo,
        reporte_id=reporte.id,
    )
