# ============================================================
# ROUTER: ASISTENTES DE CAPACITACIÓN SST
# FASE 2.7.4 - HARDENING ENTERPRISE CAPACITACIONES SST
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.capacitacion import CapacitacionSST, CapacitacionAsistenteSST
from app.schemas.capacitacion_asistente import (
    CapacitacionAsistenteCreate,
    CapacitacionAsistenteUpdate,
    CapacitacionAsistenciaPatch,
    CapacitacionAsistenteResponse,
)

router = APIRouter(
    prefix="/hacer/capacitaciones",
    tags=["HACER - Capacitaciones Asistentes SST"],
)

ROLES_LECTURA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "COORDINADOR_SST",
    "AUDITOR",
]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"]


def _empresa_id_usuario(usuario) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return None
    empresa_id = getattr(usuario, "empresa_id", None)
    if empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    return int(empresa_id)


def _capacitacion_or_404(db: Session, capacitacion_id: int, usuario):
    query = db.query(CapacitacionSST).filter(CapacitacionSST.id == capacitacion_id)
    empresa_id = _empresa_id_usuario(usuario)
    if empresa_id is not None:
        query = query.filter(CapacitacionSST.empresa_id == empresa_id)
    capacitacion = query.first()
    if not capacitacion:
        raise HTTPException(status_code=404, detail="Capacitación no encontrada")
    return capacitacion


def _asistente_or_404(db: Session, asistente_id: int, usuario):
    query = db.query(CapacitacionAsistenteSST).join(
        CapacitacionSST,
        CapacitacionSST.id == CapacitacionAsistenteSST.capacitacion_id,
    ).filter(CapacitacionAsistenteSST.id == asistente_id)
    empresa_id = _empresa_id_usuario(usuario)
    if empresa_id is not None:
        query = query.filter(CapacitacionSST.empresa_id == empresa_id)
    asistente = query.first()
    if not asistente:
        raise HTTPException(status_code=404, detail="Asistente no encontrado")
    return asistente


def recalcular_total_asistentes(db: Session, capacitacion_id: int) -> None:
    total = (
        db.query(CapacitacionAsistenteSST)
        .filter(
            CapacitacionAsistenteSST.capacitacion_id == capacitacion_id,
            CapacitacionAsistenteSST.activo,
            CapacitacionAsistenteSST.asistio,
        )
        .count()
    )
    capacitacion = (
        db.query(CapacitacionSST).filter(CapacitacionSST.id == capacitacion_id).first()
    )
    if capacitacion:
        capacitacion.total_asistentes = total


@router.get(
    "/{capacitacion_id}/asistentes", response_model=list[CapacitacionAsistenteResponse]
)
def listar_asistentes(
    capacitacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    _capacitacion_or_404(db, capacitacion_id, usuario)

    return (
        db.query(CapacitacionAsistenteSST)
        .filter(
            CapacitacionAsistenteSST.capacitacion_id == capacitacion_id,
            CapacitacionAsistenteSST.activo,
        )
        .order_by(CapacitacionAsistenteSST.id.asc())
        .all()
    )


@router.post(
    "/{capacitacion_id}/asistentes", response_model=CapacitacionAsistenteResponse
)
def crear_asistente(
    capacitacion_id: int,
    data: CapacitacionAsistenteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    _capacitacion_or_404(db, capacitacion_id, usuario)

    asistente = CapacitacionAsistenteSST(
        capacitacion_id=capacitacion_id,
        empleado_id=data.empleado_id,
        nombres=data.nombres,
        documento=data.documento,
        cargo=data.cargo,
        area=data.area,
        asistio=data.asistio,
        evaluacion=data.evaluacion,
        firma_url=data.firma_url,
        observaciones=data.observaciones,
    )
    db.add(asistente)
    db.flush()
    recalcular_total_asistentes(db, capacitacion_id)
    db.commit()
    db.refresh(asistente)
    return asistente


@router.put("/asistentes/{asistente_id}", response_model=CapacitacionAsistenteResponse)
def actualizar_asistente(
    asistente_id: int,
    data: CapacitacionAsistenteUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    asistente = _asistente_or_404(db, asistente_id, usuario)

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(asistente, campo, valor)

    recalcular_total_asistentes(db, asistente.capacitacion_id)
    db.commit()
    db.refresh(asistente)
    return asistente


@router.patch(
    "/asistentes/{asistente_id}/asistencia",
    response_model=CapacitacionAsistenteResponse,
)
def marcar_asistencia(
    asistente_id: int,
    data: CapacitacionAsistenciaPatch,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    asistente = _asistente_or_404(db, asistente_id, usuario)

    asistente.asistio = data.asistio
    recalcular_total_asistentes(db, asistente.capacitacion_id)
    db.commit()
    db.refresh(asistente)
    return asistente


@router.delete("/asistentes/{asistente_id}")
def eliminar_asistente(
    asistente_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    asistente = _asistente_or_404(db, asistente_id, usuario)

    capacitacion_id = asistente.capacitacion_id
    asistente.activo = False
    recalcular_total_asistentes(db, capacitacion_id)
    db.commit()
    return {"mensaje": "Asistente eliminado correctamente"}
