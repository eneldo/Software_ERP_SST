# ============================================================
# ROUTER: Firma Documental SST
# Archivo: backend/app/routers/firma_documental.py
# FASE 1.8.4.3.10.1 - Backend de Firma y Aprobación Digital
# ============================================================

import hashlib
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.biblioteca_documental import BibliotecaDocumental
from app.models.firma_digital import FirmaDigitalSST
from app.models.firma_documental_sst import FirmaDocumentalSST
from app.models.usuario import Usuario
from app.schemas.firma_documental_schema import (
    FirmaDocumentalCreate,
    FirmaDocumentalAprobar,
    FirmaDocumentalRechazar,
    FirmaDocumentalResponse,
    FirmaDocumentalResumen,
    FirmaDocumentalHistorialResponse,
    FirmaDocumentalDocumentoItem,
    FirmaDocumentalWorkflowResponse,
    FirmaDocumentalCertificadoResponse,
)

router = APIRouter(
    prefix="/firma-documental",
    tags=["Firma y Aprobación Digital SST"],
)

ROLES_PERMITIDOS = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "COORDINADOR",
    "AUDITOR",
]

ROLES_APROBACION = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
]


# ------------------------------------------------------------
# Utilidades internas
# ------------------------------------------------------------
def _empresa_usuario(usuario: Usuario) -> Optional[int]:
    return getattr(usuario, "empresa_id", None)


def _query_documentos_empresa(db: Session, usuario: Usuario, empresa_id: Optional[int] = None):
    query = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.activo == True)

    if empresa_id:
        query = query.filter(BibliotecaDocumental.empresa_id == empresa_id)
    elif getattr(usuario, "rol", "") != "SUPER_ADMIN" and _empresa_usuario(usuario):
        query = query.filter(BibliotecaDocumental.empresa_id == _empresa_usuario(usuario))

    return query


def _obtener_documento_o_404(db: Session, documento_id: int, usuario: Usuario):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()

    if not documento or not getattr(documento, "activo", True):
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if getattr(usuario, "rol", "") != "SUPER_ADMIN" and _empresa_usuario(usuario):
        if documento.empresa_id != _empresa_usuario(usuario):
            raise HTTPException(status_code=403, detail="No puede gestionar documentos de otra empresa")

    return documento


def _obtener_firma_activa(db: Session, usuario_id: int, firma_digital_id: Optional[int] = None):
    query = db.query(FirmaDigitalSST).filter(FirmaDigitalSST.usuario_id == usuario_id)

    if firma_digital_id:
        query = query.filter(FirmaDigitalSST.id == firma_digital_id)
    else:
        query = query.filter(FirmaDigitalSST.activo == True)

    return query.order_by(FirmaDigitalSST.id.desc()).first()


def _generar_hash(documento_id: int, usuario_id: Optional[int], rol_firmante: str, tipo_accion: str) -> str:
    base = f"{documento_id}|{usuario_id}|{rol_firmante}|{tipo_accion}|{date.today().isoformat()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _actualizar_estado_documento_por_firma(db: Session, documento: BibliotecaDocumental, tipo_accion: str):
    if tipo_accion == "APROBACION":
        documento.estado_revision = "APROBADO"
        documento.estado = "VIGENTE"
        documento.fecha_aprobacion = date.today()
        if not documento.ultima_revision:
            documento.ultima_revision = date.today()
    elif tipo_accion == "RECHAZO":
        documento.estado_revision = "RECHAZADO"
        documento.estado = "BORRADOR"
    elif tipo_accion == "REVISION":
        documento.estado_revision = "EN_REVISION"
    else:
        if not documento.estado_revision:
            documento.estado_revision = "PENDIENTE"

    db.add(documento)


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------
@router.get("/resumen", response_model=FirmaDocumentalResumen)
def obtener_resumen_firmas(
    empresa_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_PERMITIDOS)),
):
    documentos_query = _query_documentos_empresa(db, usuario_actual, empresa_id)
    documento_ids = [item.id for item in documentos_query.all()]

    total_documentos = len(documento_ids)

    firmas_query = db.query(FirmaDocumentalSST).filter(FirmaDocumentalSST.activo == True)
    if documento_ids:
        firmas_query = firmas_query.filter(FirmaDocumentalSST.documento_id.in_(documento_ids))
    else:
        firmas_query = firmas_query.filter(False)

    firmas_registradas = firmas_query.count()
    aprobados = firmas_query.filter(FirmaDocumentalSST.estado == "APROBADO").count()
    rechazados = firmas_query.filter(FirmaDocumentalSST.estado == "RECHAZADO").count()

    documentos_firmados = (
        firmas_query.with_entities(FirmaDocumentalSST.documento_id)
        .distinct()
        .count()
    )

    firmas_sst = firmas_query.filter(FirmaDocumentalSST.rol_firmante == "RESPONSABLE_SST").count()
    firmas_gerencia = firmas_query.filter(
        FirmaDocumentalSST.rol_firmante.in_(["GERENCIA", "REPRESENTANTE_LEGAL", "GERENTE"])
    ).count()

    documentos_pendientes = max(total_documentos - documentos_firmados, 0)
    cumplimiento = round((documentos_firmados / total_documentos) * 100, 2) if total_documentos else 0

    return FirmaDocumentalResumen(
        total_documentos=total_documentos,
        documentos_firmados=documentos_firmados,
        documentos_pendientes=documentos_pendientes,
        aprobados=aprobados,
        rechazados=rechazados,
        firmas_registradas=firmas_registradas,
        cumplimiento_firmas=cumplimiento,
        firmas_sst=firmas_sst,
        firmas_gerencia=firmas_gerencia,
        certificados_disponibles=firmas_registradas,
    )


@router.get("/documentos", response_model=list[FirmaDocumentalDocumentoItem])
def listar_documentos_para_firma(
    empresa_id: Optional[int] = Query(default=None),
    estado_revision: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_PERMITIDOS)),
):
    query = _query_documentos_empresa(db, usuario_actual, empresa_id)

    if estado_revision:
        query = query.filter(BibliotecaDocumental.estado_revision == estado_revision.upper())

    documentos = query.order_by(BibliotecaDocumental.id.desc()).all()
    respuesta = []

    for doc in documentos:
        firmas = (
            db.query(FirmaDocumentalSST)
            .filter(
                FirmaDocumentalSST.documento_id == doc.id,
                FirmaDocumentalSST.activo == True,
            )
            .all()
        )

        roles_firmados = {firma.rol_firmante.upper() for firma in firmas if firma.estado in ["FIRMADO", "APROBADO"]}

        respuesta.append(
            FirmaDocumentalDocumentoItem(
                id=doc.id,
                codigo_documental=doc.codigo_documental,
                titulo=doc.titulo,
                categoria=doc.categoria,
                version=doc.version,
                estado=doc.estado,
                estado_revision=getattr(doc, "estado_revision", None),
                responsable=doc.responsable,
                aprobador=getattr(doc, "aprobador", None),
                fecha_aprobacion=str(doc.fecha_aprobacion) if doc.fecha_aprobacion else None,
                fecha_vencimiento=str(doc.fecha_vencimiento) if doc.fecha_vencimiento else None,
                total_firmas=len(firmas),
                firmado_responsable_sst="RESPONSABLE_SST" in roles_firmados,
                firmado_gerencia="GERENCIA" in roles_firmados or "REPRESENTANTE_LEGAL" in roles_firmados,
            )
        )

    return respuesta


@router.get("/historial/{documento_id}", response_model=FirmaDocumentalHistorialResponse)
def historial_firmas_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_PERMITIDOS)),
):
    _obtener_documento_o_404(db, documento_id, usuario_actual)

    firmas = (
        db.query(FirmaDocumentalSST)
        .filter(FirmaDocumentalSST.documento_id == documento_id)
        .order_by(FirmaDocumentalSST.fecha_firma.desc())
        .all()
    )

    return FirmaDocumentalHistorialResponse(
        documento_id=documento_id,
        total=len(firmas),
        firmas=firmas,
    )


@router.post("/firmar", response_model=FirmaDocumentalResponse, status_code=status.HTTP_201_CREATED)
def firmar_documento(
    payload: FirmaDocumentalCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_PERMITIDOS)),
):
    documento = _obtener_documento_o_404(db, payload.documento_id, usuario_actual)

    firma_activa = _obtener_firma_activa(db, usuario_actual.id, payload.firma_digital_id)

    # La firma digital cargada es recomendada, pero no bloqueamos el flujo
    # para permitir pruebas y aprobación documental inicial.
    firma_digital_id = firma_activa.id if firma_activa else payload.firma_digital_id

    registro = FirmaDocumentalSST(
        empresa_id=documento.empresa_id,
        documento_id=documento.id,
        usuario_id=usuario_actual.id,
        firma_digital_id=firma_digital_id,
        rol_firmante=payload.rol_firmante.upper(),
        nombre_firmante=payload.nombre_firmante,
        cargo_firmante=payload.cargo_firmante,
        tipo_accion="FIRMA",
        estado="FIRMADO",
        observaciones=payload.observaciones,
        ip_origen=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        hash_firma=_generar_hash(documento.id, usuario_actual.id, payload.rol_firmante.upper(), "FIRMA"),
        activo=True,
    )

    db.add(registro)
    _actualizar_estado_documento_por_firma(db, documento, "FIRMA")
    db.commit()
    db.refresh(registro)

    return registro


@router.post("/documento/{documento_id}/aprobar", response_model=FirmaDocumentalResponse)
def aprobar_documento(
    documento_id: int,
    payload: FirmaDocumentalAprobar,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_APROBACION)),
):
    documento = _obtener_documento_o_404(db, documento_id, usuario_actual)

    firma_activa = _obtener_firma_activa(db, usuario_actual.id, payload.firma_digital_id)
    firma_digital_id = firma_activa.id if firma_activa else payload.firma_digital_id

    nombre = getattr(usuario_actual, "nombre", None) or getattr(usuario_actual, "email", None) or "Usuario aprobador"
    cargo = getattr(usuario_actual, "cargo", None) or "Aprobador documental"

    registro = FirmaDocumentalSST(
        empresa_id=documento.empresa_id,
        documento_id=documento.id,
        usuario_id=usuario_actual.id,
        firma_digital_id=firma_digital_id,
        rol_firmante="GERENCIA" if usuario_actual.rol in ["SUPER_ADMIN", "ADMIN_EMPRESA"] else "RESPONSABLE_SST",
        nombre_firmante=nombre,
        cargo_firmante=cargo,
        tipo_accion="APROBACION",
        estado="APROBADO",
        observaciones=payload.observaciones,
        ip_origen=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        hash_firma=_generar_hash(documento.id, usuario_actual.id, "APROBACION", "APROBACION"),
        activo=True,
    )

    documento.aprobador = nombre
    _actualizar_estado_documento_por_firma(db, documento, "APROBACION")

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro


@router.post("/documento/{documento_id}/rechazar", response_model=FirmaDocumentalResponse)
def rechazar_documento(
    documento_id: int,
    payload: FirmaDocumentalRechazar,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_APROBACION)),
):
    documento = _obtener_documento_o_404(db, documento_id, usuario_actual)

    nombre = getattr(usuario_actual, "nombre", None) or getattr(usuario_actual, "email", None) or "Usuario revisor"
    cargo = getattr(usuario_actual, "cargo", None) or "Revisor documental"

    registro = FirmaDocumentalSST(
        empresa_id=documento.empresa_id,
        documento_id=documento.id,
        usuario_id=usuario_actual.id,
        firma_digital_id=None,
        rol_firmante="REVISOR",
        nombre_firmante=nombre,
        cargo_firmante=cargo,
        tipo_accion="RECHAZO",
        estado="RECHAZADO",
        observaciones=payload.observaciones,
        motivo_rechazo=payload.motivo_rechazo,
        ip_origen=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        hash_firma=_generar_hash(documento.id, usuario_actual.id, "RECHAZO", "RECHAZO"),
        activo=True,
    )

    documento.motivo_cambio_estado = payload.motivo_rechazo
    _actualizar_estado_documento_por_firma(db, documento, "RECHAZO")

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro



@router.get("/workflow/{documento_id}", response_model=FirmaDocumentalWorkflowResponse)
def obtener_workflow_documental(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_PERMITIDOS)),
):
    """Retorna el estado visual del flujo de aprobación digital de un documento."""
    documento = _obtener_documento_o_404(db, documento_id, usuario_actual)

    firmas = (
        db.query(FirmaDocumentalSST)
        .filter(
            FirmaDocumentalSST.documento_id == documento_id,
            FirmaDocumentalSST.activo == True,
        )
        .all()
    )

    roles = {str(f.rol_firmante or "").upper() for f in firmas if f.estado in ["FIRMADO", "APROBADO"]}
    estados = {str(f.estado or "").upper() for f in firmas}

    estado_revision = str(getattr(documento, "estado_revision", "") or "").upper()
    estado_documento = str(getattr(documento, "estado", "") or "").upper()

    return FirmaDocumentalWorkflowResponse(
        documento_id=documento.id,
        codigo=documento.codigo_documental,
        titulo=documento.titulo,
        estado=documento.estado,
        estado_revision=documento.estado_revision,
        workflow={
            "creado": True,
            "revision": estado_revision in ["EN_REVISION", "APROBADO", "RECHAZADO"] or "RESPONSABLE_SST" in roles,
            "firma_sst": "RESPONSABLE_SST" in roles,
            "gerencia": bool(roles.intersection({"GERENCIA", "REPRESENTANTE_LEGAL", "GERENTE"})),
            "aprobado": "APROBADO" in estados or estado_revision == "APROBADO",
            "vigente": estado_documento == "VIGENTE",
            "rechazado": "RECHAZADO" in estados or estado_revision == "RECHAZADO",
        },
    )


@router.get("/certificado/{firma_documental_id}", response_model=FirmaDocumentalCertificadoResponse)
def obtener_certificado_firma(
    firma_documental_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_PERMITIDOS)),
):
    """Entrega los datos auditables para generar el certificado de firma digital en frontend."""
    firma = (
        db.query(FirmaDocumentalSST)
        .filter(FirmaDocumentalSST.id == firma_documental_id)
        .first()
    )

    if not firma:
        raise HTTPException(status_code=404, detail="Firma documental no encontrada")

    documento = _obtener_documento_o_404(db, firma.documento_id, usuario_actual)

    return FirmaDocumentalCertificadoResponse(
        firma_id=firma.id,
        documento_id=firma.documento_id,
        codigo_documental=documento.codigo_documental,
        titulo=documento.titulo,
        version=documento.version,
        estado_documento=documento.estado,
        estado_revision=getattr(documento, "estado_revision", None),
        rol_firmante=firma.rol_firmante,
        nombre_firmante=firma.nombre_firmante,
        cargo_firmante=firma.cargo_firmante,
        tipo_accion=firma.tipo_accion,
        estado_firma=firma.estado,
        observaciones=firma.observaciones,
        motivo_rechazo=firma.motivo_rechazo,
        ip_origen=firma.ip_origen,
        user_agent=firma.user_agent,
        hash_firma=firma.hash_firma,
        fecha_firma=firma.fecha_firma,
        empresa_id=firma.empresa_id,
    )


@router.delete("/{firma_documental_id}")
def anular_firma_documental(
    firma_documental_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    firma = db.query(FirmaDocumentalSST).filter(FirmaDocumentalSST.id == firma_documental_id).first()

    if not firma:
        raise HTTPException(status_code=404, detail="Firma documental no encontrada")

    firma.activo = False
    firma.estado = "ANULADO"
    db.commit()

    return {"mensaje": "Firma documental anulada correctamente"}
