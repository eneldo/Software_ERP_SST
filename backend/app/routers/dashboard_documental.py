# ============================================================
# ROUTER: Dashboard Documental SST Enterprise
# Archivo: backend/app/routers/dashboard_documental.py
# FASE 1.8.4.3.9 - Centro de Control Documental SST Enterprise
# ------------------------------------------------------------
# Entrega KPIs, vencimientos, agrupaciones y versiones recientes
# del Centro de Control Documental SST.
# ============================================================

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.biblioteca_documental import BibliotecaDocumental
from app.models.documento_version import DocumentoVersion
from app.schemas.dashboard_documental_schema import (
    ConteoAgrupado,
    DashboardDocumentalKPI,
    DashboardDocumentalResponse,
    DocumentoVencimientoItem,
    VersionRecienteItem,
)

router = APIRouter(
    prefix="/dashboard-documental",
    tags=["Centro Control Documental SST"],
)

ESTADOS_PENDIENTES = ["BORRADOR", "EN_REVISION", "PENDIENTE", "PENDIENTE_APROBACION"]


def _base_query(db: Session, empresa_id: int | None = None):
    query = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.activo == True)

    if empresa_id:
        query = query.filter(BibliotecaDocumental.empresa_id == empresa_id)

    return query


def _calcular_semaforo(fecha_vencimiento):
    if not fecha_vencimiento:
        return "SIN_FECHA"

    hoy = date.today()
    dias = (fecha_vencimiento - hoy).days

    if dias < 0:
        return "VENCIDO"
    if dias <= 7:
        return "CRITICO"
    if dias <= 15:
        return "ALERTA"
    if dias <= 30:
        return "PROXIMO"
    return "VIGENTE"


def _serializar_vencimiento(documento: BibliotecaDocumental):
    dias_restantes = None

    if documento.fecha_vencimiento:
        dias_restantes = (documento.fecha_vencimiento - date.today()).days

    return DocumentoVencimientoItem(
        id=documento.id,
        codigo_documental=documento.codigo_documental,
        titulo=documento.titulo,
        categoria=documento.categoria,
        tipo_documento=documento.tipo_documento,
        estado=documento.estado,
        responsable=documento.responsable,
        version=documento.version,
        fecha_vencimiento=documento.fecha_vencimiento,
        dias_restantes=dias_restantes,
        semaforo=_calcular_semaforo(documento.fecha_vencimiento),
    )


def _agrupar(db: Session, campo, empresa_id: int | None = None):
    query = (
        db.query(campo.label("nombre"), func.count(BibliotecaDocumental.id).label("total"))
        .filter(BibliotecaDocumental.activo == True)
    )

    if empresa_id:
        query = query.filter(BibliotecaDocumental.empresa_id == empresa_id)

    filas = query.group_by(campo).order_by(func.count(BibliotecaDocumental.id).desc()).all()

    return [ConteoAgrupado(nombre=str(fila.nombre or "Sin definir"), total=fila.total) for fila in filas]


@router.get("/resumen", response_model=DashboardDocumentalResponse)
def obtener_resumen_documental(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])),
):
    hoy = date.today()
    limite_30 = hoy + timedelta(days=30)

    base = _base_query(db, empresa_id)

    total = base.count()
    vigentes = base.filter(BibliotecaDocumental.estado == "VIGENTE").count()
    borradores = base.filter(BibliotecaDocumental.estado == "BORRADOR").count()
    obsoletos = base.filter(BibliotecaDocumental.estado == "OBSOLETO").count()

    vencidos_query = base.filter(
        BibliotecaDocumental.fecha_vencimiento.isnot(None),
        BibliotecaDocumental.fecha_vencimiento < hoy,
        BibliotecaDocumental.estado != "OBSOLETO",
    )

    proximos_query = base.filter(
        BibliotecaDocumental.fecha_vencimiento.isnot(None),
        BibliotecaDocumental.fecha_vencimiento >= hoy,
        BibliotecaDocumental.fecha_vencimiento <= limite_30,
        BibliotecaDocumental.estado != "OBSOLETO",
    )

    vencidos_count = vencidos_query.count()
    proximos_count = proximos_query.count()
    pendientes_revision = base.filter(BibliotecaDocumental.estado.in_(ESTADOS_PENDIENTES)).count()

    version_query = db.query(DocumentoVersion)

    if empresa_id:
        version_query = version_query.join(BibliotecaDocumental).filter(BibliotecaDocumental.empresa_id == empresa_id)

    total_versiones = version_query.count()
    cumplimiento = round((vigentes / total) * 100, 2) if total else 0

    proximos = (
        proximos_query.order_by(BibliotecaDocumental.fecha_vencimiento.asc()).limit(10).all()
    )

    vencidos = (
        vencidos_query.order_by(BibliotecaDocumental.fecha_vencimiento.asc()).limit(10).all()
    )

    versiones_query = (
        db.query(DocumentoVersion, BibliotecaDocumental)
        .join(BibliotecaDocumental, DocumentoVersion.documento_id == BibliotecaDocumental.id)
        .filter(BibliotecaDocumental.activo == True)
    )

    if empresa_id:
        versiones_query = versiones_query.filter(BibliotecaDocumental.empresa_id == empresa_id)

    versiones = versiones_query.order_by(DocumentoVersion.fecha_creacion.desc()).limit(8).all()

    return DashboardDocumentalResponse(
        kpis=DashboardDocumentalKPI(
            total_documentos=total,
            vigentes=vigentes,
            borradores=borradores,
            obsoletos=obsoletos,
            vencidos=vencidos_count,
            proximos_vencer=proximos_count,
            pendientes_revision=pendientes_revision,
            total_versiones=total_versiones,
            cumplimiento_documental=cumplimiento,
        ),
        estados=_agrupar(db, BibliotecaDocumental.estado, empresa_id),
        categorias=_agrupar(db, BibliotecaDocumental.categoria, empresa_id),
        responsables=_agrupar(db, BibliotecaDocumental.responsable, empresa_id),
        proximos_vencer=[_serializar_vencimiento(doc) for doc in proximos],
        vencidos=[_serializar_vencimiento(doc) for doc in vencidos],
        versiones_recientes=[
            VersionRecienteItem(
                id=version.id,
                documento_id=version.documento_id,
                codigo_documental=documento.codigo_documental,
                titulo=documento.titulo,
                version=version.version,
                descripcion_cambio=version.descripcion_cambio,
                usuario=version.usuario,
                fecha_creacion=version.fecha_creacion,
            )
            for version, documento in versiones
        ],
    )


@router.get("/vencimientos", response_model=list[DocumentoVencimientoItem])
def listar_vencimientos_documentales(
    empresa_id: int | None = None,
    dias: int = 30,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])),
):
    hoy = date.today()
    limite = hoy + timedelta(days=dias)

    documentos = (
        _base_query(db, empresa_id)
        .filter(
            BibliotecaDocumental.fecha_vencimiento.isnot(None),
            BibliotecaDocumental.fecha_vencimiento <= limite,
            BibliotecaDocumental.estado != "OBSOLETO",
        )
        .order_by(BibliotecaDocumental.fecha_vencimiento.asc())
        .all()
    )

    return [_serializar_vencimiento(doc) for doc in documentos]


@router.get("/indicadores", response_model=DashboardDocumentalKPI)
def obtener_indicadores_documentales(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])),
):
    resumen = obtener_resumen_documental(empresa_id=empresa_id, db=db, usuario=usuario)
    return resumen.kpis
