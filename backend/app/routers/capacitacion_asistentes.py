# ============================================================
# ROUTER: ASISTENTES DE CAPACITACIÓN SST
# FASE 2.7.4 - HARDENING ENTERPRISE CAPACITACIONES SST
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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


def recalcular_total_asistentes(db: Session, capacitacion_id: int) -> None:
    total = (
        db.query(CapacitacionAsistenteSST)
        .filter(
            CapacitacionAsistenteSST.capacitacion_id == capacitacion_id,
            CapacitacionAsistenteSST.activo == True,
            CapacitacionAsistenteSST.asistio == True,
        )
        .count()
    )
    capacitacion = db.query(CapacitacionSST).filter(CapacitacionSST.id == capacitacion_id).first()
    if capacitacion:
        capacitacion.total_asistentes = total


@router.get("/{capacitacion_id}/asistentes", response_model=list[CapacitacionAsistenteResponse])
def listar_asistentes(capacitacion_id: int, db: Session = Depends(get_db)):
    capacitacion = db.query(CapacitacionSST).filter(CapacitacionSST.id == capacitacion_id).first()
    if not capacitacion:
        raise HTTPException(status_code=404, detail="Capacitación no encontrada")

    return (
        db.query(CapacitacionAsistenteSST)
        .filter(
            CapacitacionAsistenteSST.capacitacion_id == capacitacion_id,
            CapacitacionAsistenteSST.activo == True,
        )
        .order_by(CapacitacionAsistenteSST.id.asc())
        .all()
    )


@router.post("/{capacitacion_id}/asistentes", response_model=CapacitacionAsistenteResponse)
def crear_asistente(capacitacion_id: int, data: CapacitacionAsistenteCreate, db: Session = Depends(get_db)):
    capacitacion = db.query(CapacitacionSST).filter(CapacitacionSST.id == capacitacion_id).first()
    if not capacitacion:
        raise HTTPException(status_code=404, detail="Capacitación no encontrada")

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
def actualizar_asistente(asistente_id: int, data: CapacitacionAsistenteUpdate, db: Session = Depends(get_db)):
    asistente = db.query(CapacitacionAsistenteSST).filter(CapacitacionAsistenteSST.id == asistente_id).first()
    if not asistente:
        raise HTTPException(status_code=404, detail="Asistente no encontrado")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(asistente, campo, valor)

    recalcular_total_asistentes(db, asistente.capacitacion_id)
    db.commit()
    db.refresh(asistente)
    return asistente


@router.patch("/asistentes/{asistente_id}/asistencia", response_model=CapacitacionAsistenteResponse)
def marcar_asistencia(asistente_id: int, data: CapacitacionAsistenciaPatch, db: Session = Depends(get_db)):
    asistente = db.query(CapacitacionAsistenteSST).filter(CapacitacionAsistenteSST.id == asistente_id).first()
    if not asistente:
        raise HTTPException(status_code=404, detail="Asistente no encontrado")

    asistente.asistio = data.asistio
    recalcular_total_asistentes(db, asistente.capacitacion_id)
    db.commit()
    db.refresh(asistente)
    return asistente


@router.delete("/asistentes/{asistente_id}")
def eliminar_asistente(asistente_id: int, db: Session = Depends(get_db)):
    asistente = db.query(CapacitacionAsistenteSST).filter(CapacitacionAsistenteSST.id == asistente_id).first()
    if not asistente:
        raise HTTPException(status_code=404, detail="Asistente no encontrado")

    capacitacion_id = asistente.capacitacion_id
    asistente.activo = False
    recalcular_total_asistentes(db, capacitacion_id)
    db.commit()
    return {"mensaje": "Asistente eliminado correctamente"}
