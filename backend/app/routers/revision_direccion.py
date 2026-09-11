# ============================================================
# USO DEL ARCHIVO:
# Router principal del módulo Revisión por la Dirección SST.
#
# Incluye:
# - Dashboard ejecutivo
# - CRUD de revisiones
# - CRUD de compromisos gerenciales
# - Cambio de estado
# - Bloqueo legal documental al aprobar/cerrar/anular
# - Congelamiento de edición/eliminación cuando bloqueado=True
# - Versionado documental automático antes de editar
# - Snapshot automático antes de cambio de estado
#
# Ubicación:
# backend/app/routers/revision_direccion.py
#
# FASE 1.8.4.3.6 — Snapshot Automático Enterprise
# ============================================================

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import require_roles
from app.core.roles import (
    ROLES_ALTA_DIRECCION,
    ROLES_GESTION_SST,
    ROLES_LECTURA_EJECUTIVA,
    normalizar_rol,
)
from app.models.empresa import Empresa
from app.models.revision_direccion import (
    RevisionDireccionSST,
    RevisionDireccionCompromisoSST,
)
from app.schemas.revision_direccion import (
    RevisionDireccionCreate,
    RevisionDireccionUpdate,
    RevisionDireccionResponse,
    RevisionDireccionDashboardResponse,
    RevisionDireccionCompromisoCreate,
    RevisionDireccionCompromisoUpdate,
    RevisionDireccionCompromisoResponse,
)
from app.services.revision_version_service import crear_snapshot_revision


router = APIRouter(
    prefix="/verificar/revision-direccion",
    tags=["Revisión Dirección SST"],
)


ROLES_LECTURA = list(ROLES_LECTURA_EJECUTIVA)
ROLES_ESCRITURA = list(ROLES_GESTION_SST)
ROLES_CAMBIO_ESTADO = list(dict.fromkeys((*ROLES_GESTION_SST, *ROLES_ALTA_DIRECCION)))
ROLES_APROBACION = set(ROLES_ALTA_DIRECCION)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def generar_codigo_revision(db: Session) -> str:
    total = db.query(RevisionDireccionSST).count() + 1
    return f"RD-SST-{total:04d}"


def obtener_usuario_id(usuario):
    return getattr(usuario, "id", None)


def empresa_autorizada(usuario, empresa_id: int | None = None) -> int | None:
    if normalizar_rol(getattr(usuario, "rol", None)) == "SUPER_ADMIN":
        return empresa_id
    empresa_usuario = getattr(usuario, "empresa_id", None)
    if not empresa_usuario:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(empresa_id) != int(empresa_usuario):
        raise HTTPException(status_code=403, detail="No puede acceder a revisiones de otra empresa")
    return int(empresa_usuario)


def obtener_revision_o_404(db: Session, revision_id: int, usuario=None):
    revision = (
        db.query(RevisionDireccionSST)
        .options(joinedload(RevisionDireccionSST.compromisos))
        .filter(
            RevisionDireccionSST.id == revision_id,
            RevisionDireccionSST.activo == True,
        )
        .first()
    )

    if not revision:
        raise HTTPException(
            status_code=404,
            detail="Revisión por la Dirección no encontrada",
        )

    if usuario is not None:
        empresa_autorizada(usuario, revision.empresa_id)

    return revision


def validar_revision_no_bloqueada(revision: RevisionDireccionSST):
    if getattr(revision, "bloqueado", False):
        raise HTTPException(
            status_code=403,
            detail=(
                "La revisión se encuentra bloqueada legalmente "
                "y no puede modificarse."
            ),
        )


def recalcular_compromisos(db: Session, revision: RevisionDireccionSST):
    compromisos = (
        db.query(RevisionDireccionCompromisoSST)
        .filter(
            RevisionDireccionCompromisoSST.revision_id == revision.id,
            RevisionDireccionCompromisoSST.activo == True,
        )
        .all()
    )

    total = len(compromisos)
    cerrados = len([c for c in compromisos if c.estado == "CERRADO"])
    pendientes = total - cerrados

    revision.total_compromisos = total
    revision.compromisos_cerrados = cerrados
    revision.compromisos_pendientes = pendientes
    revision.porcentaje_cumplimiento = (
        round((cerrados / total) * 100, 2)
        if total
        else 0
    )

    db.commit()
    db.refresh(revision)

    return revision


def crear_snapshot_seguro(
    db: Session,
    revision: RevisionDireccionSST,
    usuario_id: int | None,
    accion: str,
    observacion: str,
):
    """
    Crea snapshot documental sin detener el flujo principal si ocurre un error.
    """
    try:
        crear_snapshot_revision(
            db=db,
            revision=revision,
            usuario_id=usuario_id,
            accion=accion,
            observacion=observacion,
        )
    except Exception as error:
        import logging
        logging.getLogger("app.revision_direccion").error(
            "Error creando snapshot documental revision_id=%s accion=%s error=%s",
            getattr(revision, "id", None),
            accion,
            error,
        )


# ============================================================
# DASHBOARD
# ============================================================

@router.get(
    "/dashboard",
    response_model=RevisionDireccionDashboardResponse,
)
def dashboard_revision_direccion(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    empresa_id = empresa_autorizada(usuario, empresa_id)
    q_revisiones = db.query(RevisionDireccionSST).filter(
        RevisionDireccionSST.activo == True
    )

    q_compromisos = db.query(RevisionDireccionCompromisoSST).filter(
        RevisionDireccionCompromisoSST.activo == True
    )

    if empresa_id:
        q_revisiones = q_revisiones.filter(
            RevisionDireccionSST.empresa_id == empresa_id
        )
        q_compromisos = q_compromisos.filter(
            RevisionDireccionCompromisoSST.empresa_id == empresa_id
        )

    revisiones = q_revisiones.all()
    compromisos = q_compromisos.all()

    total_compromisos = len(compromisos)
    compromisos_cerrados = len(
        [c for c in compromisos if c.estado == "CERRADO"]
    )
    compromisos_pendientes = total_compromisos - compromisos_cerrados

    return {
        "total_revisiones": len(revisiones),
        "borradores": len([r for r in revisiones if r.estado == "BORRADOR"]),
        "aprobadas": len([r for r in revisiones if r.estado == "APROBADA"]),
        "cerradas": len([r for r in revisiones if r.estado == "CERRADA"]),
        "total_compromisos": total_compromisos,
        "compromisos_pendientes": compromisos_pendientes,
        "compromisos_cerrados": compromisos_cerrados,
        "porcentaje_cumplimiento_global": (
            round((compromisos_cerrados / total_compromisos) * 100, 2)
            if total_compromisos
            else 0
        ),
    }


# ============================================================
# REVISIONES
# ============================================================

@router.post(
    "/",
    response_model=RevisionDireccionResponse,
)
def crear_revision_direccion(
    data: RevisionDireccionCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa_autorizada(usuario, data.empresa_id)
    empresa = (
        db.query(Empresa)
        .filter(Empresa.id == data.empresa_id)
        .first()
    )

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    revision = RevisionDireccionSST(
        **data.model_dump(),
        codigo=generar_codigo_revision(db),
        usuario_id=obtener_usuario_id(usuario),
        estado="BORRADOR",
        bloqueado=False,
        version_documental="BORRADOR",
    )

    db.add(revision)
    db.commit()
    db.refresh(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="CREACION",
        observacion="Snapshot automático de creación de revisión",
    )

    return revision


@router.get(
    "/",
    response_model=list[RevisionDireccionResponse],
)
def listar_revisiones_direccion(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    empresa_id = empresa_autorizada(usuario, empresa_id)
    query = (
        db.query(RevisionDireccionSST)
        .options(joinedload(RevisionDireccionSST.compromisos))
        .filter(RevisionDireccionSST.activo == True)
    )

    if empresa_id:
        query = query.filter(RevisionDireccionSST.empresa_id == empresa_id)

    return query.order_by(RevisionDireccionSST.id.desc()).all()


@router.get(
    "/{revision_id}",
    response_model=RevisionDireccionResponse,
)
def obtener_revision_direccion(
    revision_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return obtener_revision_o_404(db, revision_id, usuario)


@router.put(
    "/{revision_id}",
    response_model=RevisionDireccionResponse,
)
def actualizar_revision_direccion(
    revision_id: int,
    data: RevisionDireccionUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    revision = obtener_revision_o_404(db, revision_id, usuario)
    validar_revision_no_bloqueada(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="ACTUALIZACION_PREVIA",
        observacion="Snapshot automático previo a modificación de revisión",
    )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(revision, key, value)

    db.commit()
    db.refresh(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="ACTUALIZACION_POSTERIOR",
        observacion="Snapshot automático posterior a modificación de revisión",
    )

    return revision


@router.patch(
    "/{revision_id}/estado",
    response_model=RevisionDireccionResponse,
)
def cambiar_estado_revision(
    revision_id: int,
    estado: str,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_CAMBIO_ESTADO)),
):
    estados_validos = [
        "BORRADOR",
        "APROBADA",
        "CERRADA",
        "ANULADA",
    ]

    if estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Use: {', '.join(estados_validos)}",
        )

    if estado in {"APROBADA", "CERRADA", "ANULADA"} and normalizar_rol(usuario.rol) not in ROLES_APROBACION:
        raise HTTPException(
            status_code=403,
            detail="Solo la alta dirección o el administrador de empresa puede aprobar, cerrar o anular la revisión",
        )

    revision = obtener_revision_o_404(db, revision_id, usuario)

    if getattr(revision, "bloqueado", False):
        raise HTTPException(
            status_code=403,
            detail="La revisión ya está bloqueada legalmente.",
        )

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="CAMBIO_ESTADO_PREVIO",
        observacion=f"Snapshot automático previo a cambio de estado a {estado}",
    )

    revision.estado = estado

    if estado == "APROBADA":
        ahora = datetime.now()
        usuario_id = obtener_usuario_id(usuario)

        revision.bloqueado = True
        revision.fecha_bloqueo = ahora
        revision.fecha_aprobacion = ahora
        revision.bloqueado_por_usuario_id = usuario_id
        revision.aprobado_por_usuario_id = usuario_id
        revision.version_documental = "OFICIAL"
        revision.motivo_bloqueo = (
            "Acta aprobada y congelada legalmente."
        )

    elif estado == "CERRADA":
        ahora = datetime.now()
        usuario_id = obtener_usuario_id(usuario)

        revision.bloqueado = True
        revision.fecha_bloqueo = ahora
        revision.bloqueado_por_usuario_id = usuario_id
        revision.version_documental = "CERRADA"
        revision.motivo_bloqueo = (
            "Acta cerrada y congelada documentalmente."
        )

    elif estado == "ANULADA":
        ahora = datetime.now()
        usuario_id = obtener_usuario_id(usuario)

        revision.bloqueado = True
        revision.fecha_bloqueo = ahora
        revision.bloqueado_por_usuario_id = usuario_id
        revision.version_documental = "ANULADA"
        revision.motivo_bloqueo = (
            "Acta anulada y bloqueada documentalmente."
        )

    db.commit()
    db.refresh(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="CAMBIO_ESTADO_POSTERIOR",
        observacion=f"Snapshot automático posterior a cambio de estado a {estado}",
    )

    return revision


@router.delete("/{revision_id}")
def eliminar_revision_direccion(
    revision_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    revision = obtener_revision_o_404(db, revision_id, usuario)
    validar_revision_no_bloqueada(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="ELIMINACION_LOGICA_PREVIA",
        observacion="Snapshot automático previo a eliminación lógica",
    )

    revision.activo = False

    db.commit()

    return {
        "mensaje": "Revisión por la Dirección eliminada correctamente",
    }


# ============================================================
# COMPROMISOS
# ============================================================

@router.post(
    "/{revision_id}/compromisos",
    response_model=RevisionDireccionCompromisoResponse,
)
def crear_compromiso_revision(
    revision_id: int,
    data: RevisionDireccionCompromisoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    revision = obtener_revision_o_404(db, revision_id, usuario)
    validar_revision_no_bloqueada(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="COMPROMISO_CREACION_PREVIA",
        observacion="Snapshot automático previo a creación de compromiso",
    )

    compromiso = RevisionDireccionCompromisoSST(
        revision_id=revision.id,
        empresa_id=revision.empresa_id,
        **data.model_dump(),
        estado="PENDIENTE",
    )

    db.add(compromiso)
    db.commit()
    db.refresh(compromiso)

    recalcular_compromisos(db, revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="COMPROMISO_CREACION_POSTERIOR",
        observacion="Snapshot automático posterior a creación de compromiso",
    )

    return compromiso


@router.put(
    "/compromisos/{compromiso_id}",
    response_model=RevisionDireccionCompromisoResponse,
)
def actualizar_compromiso_revision(
    compromiso_id: int,
    data: RevisionDireccionCompromisoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    compromiso = (
        db.query(RevisionDireccionCompromisoSST)
        .filter(
            RevisionDireccionCompromisoSST.id == compromiso_id,
            RevisionDireccionCompromisoSST.activo == True,
        )
        .first()
    )

    if not compromiso:
        raise HTTPException(
            status_code=404,
            detail="Compromiso no encontrado",
        )

    revision = obtener_revision_o_404(db, compromiso.revision_id, usuario)
    validar_revision_no_bloqueada(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="COMPROMISO_ACTUALIZACION_PREVIA",
        observacion="Snapshot automático previo a modificación de compromiso",
    )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(compromiso, key, value)

    if compromiso.estado == "CERRADO" and not compromiso.fecha_cierre:
        compromiso.fecha_cierre = datetime.now().date()

    db.commit()
    db.refresh(compromiso)

    recalcular_compromisos(db, revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="COMPROMISO_ACTUALIZACION_POSTERIOR",
        observacion="Snapshot automático posterior a modificación de compromiso",
    )

    return compromiso


@router.delete("/compromisos/{compromiso_id}")
def eliminar_compromiso_revision(
    compromiso_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    compromiso = (
        db.query(RevisionDireccionCompromisoSST)
        .filter(
            RevisionDireccionCompromisoSST.id == compromiso_id,
            RevisionDireccionCompromisoSST.activo == True,
        )
        .first()
    )

    if not compromiso:
        raise HTTPException(
            status_code=404,
            detail="Compromiso no encontrado",
        )

    revision = obtener_revision_o_404(db, compromiso.revision_id, usuario)
    validar_revision_no_bloqueada(revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="COMPROMISO_ELIMINACION_PREVIA",
        observacion="Snapshot automático previo a eliminación de compromiso",
    )

    compromiso.activo = False
    db.commit()

    recalcular_compromisos(db, revision)

    crear_snapshot_seguro(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="COMPROMISO_ELIMINACION_POSTERIOR",
        observacion="Snapshot automático posterior a eliminación de compromiso",
    )

    return {
        "mensaje": "Compromiso eliminado correctamente",
    }
