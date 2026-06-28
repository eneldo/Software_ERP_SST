# ============================================================
# ROUTER: Centro Documental Enterprise Visual PRO
# Archivo: backend/app/routers/documental_enterprise.py
# FASE 1.8.4.3.9.2
# ------------------------------------------------------------
# Endpoints ejecutivos para la capa visual del centro documental:
# listado inteligente, alertas, historial y cambio de estado.
# ============================================================

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.biblioteca_documental import BibliotecaDocumental
from app.models.archivo_sst import ArchivoSST

try:
    from app.models.documento_version import DocumentoVersion
except Exception:  # Permite que el backend cargue aunque aún no esté creado el modelo de versiones.
    DocumentoVersion = None


router = APIRouter(
    prefix="/documental-enterprise",
    tags=["Centro Documental Enterprise PRO"],
)


def _base_query(db: Session, empresa_id: Optional[int] = None):
    query = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.activo == True)
    if empresa_id:
        query = query.filter(BibliotecaDocumental.empresa_id == empresa_id)
    return query


def _dias_restantes(fecha_vencimiento):
    if not fecha_vencimiento:
        return None
    return (fecha_vencimiento - date.today()).days


def _serializar_documento(doc: BibliotecaDocumental):
    archivo = doc.archivo
    dias_restantes = _dias_restantes(doc.fecha_vencimiento)

    if doc.fecha_vencimiento and doc.fecha_vencimiento < date.today():
        alerta = "VENCIDO"
    elif dias_restantes is not None and dias_restantes <= 30:
        alerta = "PROXIMO"
    elif (doc.estado_revision or "").upper() in ["PENDIENTE", "EN_REVISION"]:
        alerta = "REVISION"
    else:
        alerta = "OK"

    return {
        "id": doc.id,
        "empresa_id": doc.empresa_id,
        "archivo_id": doc.archivo_id,
        "usuario_id": doc.usuario_id,
        "codigo_documental": doc.codigo_documental,
        "titulo": doc.titulo,
        "categoria": doc.categoria,
        "tipo_documento": doc.tipo_documento,
        "modulo_origen": doc.modulo_origen,
        "version": doc.version,
        "estado": doc.estado,
        "estado_revision": doc.estado_revision,
        "aprobador": doc.aprobador,
        "motivo_cambio_estado": doc.motivo_cambio_estado,
        "responsable": doc.responsable,
        "descripcion": doc.descripcion,
        "palabras_clave": doc.palabras_clave,
        "fecha_aprobacion": doc.fecha_aprobacion,
        "fecha_vencimiento": doc.fecha_vencimiento,
        "ultima_revision": doc.ultima_revision,
        "proxima_revision": doc.proxima_revision,
        "dias_restantes": dias_restantes,
        "alerta": alerta,
        "activo": doc.activo,
        "archivo_url": archivo.url if archivo else None,
        "archivo_nombre": archivo.nombre_original if archivo else None,
        "archivo_extension": archivo.extension if archivo else None,
        "archivo_mime_type": archivo.mime_type if archivo else None,
        "fecha_creacion": doc.fecha_creacion,
        "fecha_actualizacion": doc.fecha_actualizacion,
    }


@router.get("/documentos")
def listar_documentos_enterprise(
    empresa_id: Optional[int] = None,
    categoria: Optional[str] = None,
    estado: Optional[str] = None,
    estado_revision: Optional[str] = None,
    responsable: Optional[str] = None,
    buscar: Optional[str] = None,
    limite: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    query = _base_query(db, empresa_id)

    if categoria:
        query = query.filter(BibliotecaDocumental.categoria.ilike(categoria))
    if estado:
        query = query.filter(BibliotecaDocumental.estado.ilike(estado))
    if estado_revision:
        query = query.filter(BibliotecaDocumental.estado_revision.ilike(estado_revision))
    if responsable:
        query = query.filter(BibliotecaDocumental.responsable.ilike(f"%{responsable}%"))
    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            or_(
                BibliotecaDocumental.codigo_documental.ilike(patron),
                BibliotecaDocumental.titulo.ilike(patron),
                BibliotecaDocumental.categoria.ilike(patron),
                BibliotecaDocumental.responsable.ilike(patron),
                BibliotecaDocumental.palabras_clave.ilike(patron),
            )
        )

    documentos = query.order_by(BibliotecaDocumental.fecha_actualizacion.desc()).limit(limite).all()
    return [_serializar_documento(doc) for doc in documentos]


@router.get("/alertas")
def obtener_alertas_enterprise(
    empresa_id: Optional[int] = None,
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    hoy = date.today()
    limite = hoy + timedelta(days=dias)
    base = _base_query(db, empresa_id)

    vencidos = base.filter(BibliotecaDocumental.fecha_vencimiento < hoy).count()
    proximos = base.filter(
        BibliotecaDocumental.fecha_vencimiento >= hoy,
        BibliotecaDocumental.fecha_vencimiento <= limite,
    ).count()
    pendientes_revision = base.filter(
        func.upper(func.coalesce(BibliotecaDocumental.estado_revision, "PENDIENTE")).in_(
            ["PENDIENTE", "EN_REVISION"]
        )
    ).count()
    sin_aprobador = base.filter(
        or_(BibliotecaDocumental.aprobador == None, BibliotecaDocumental.aprobador == "")
    ).count()

    return {
        "vencidos": vencidos,
        "proximos": proximos,
        "pendientes_revision": pendientes_revision,
        "sin_aprobador": sin_aprobador,
        "nivel": "CRITICO" if vencidos else "ALERTA" if proximos or pendientes_revision else "ESTABLE",
    }


@router.get("/historial/{documento_id}")
def obtener_historial_enterprise(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if DocumentoVersion is None:
        return []

    versiones = (
        db.query(DocumentoVersion)
        .filter(DocumentoVersion.documento_id == documento_id)
        .order_by(DocumentoVersion.fecha_creacion.desc())
        .all()
    )

    return [
        {
            "id": version.id,
            "documento_id": version.documento_id,
            "version": version.version,
            "descripcion_cambio": version.descripcion_cambio,
            "usuario": version.usuario,
            "archivo_url": version.archivo_url,
            "fecha_creacion": version.fecha_creacion,
        }
        for version in versiones
    ]


@router.patch("/documentos/{documento_id}/estado")
def cambiar_estado_documental_enterprise(
    documento_id: int,
    estado: str,
    estado_revision: Optional[str] = None,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    documento.estado = estado.upper()
    if estado_revision:
        documento.estado_revision = estado_revision.upper()
    if motivo:
        documento.motivo_cambio_estado = motivo

    if documento.estado == "VIGENTE" and not documento.fecha_aprobacion:
        documento.fecha_aprobacion = date.today()

    db.commit()
    db.refresh(documento)
    return _serializar_documento(documento)
