from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.objetivo_sst import ObjetivoSST
from app.models.empresa import Empresa

from app.schemas.objetivo_sst_schema import (
    ObjetivoSSTCreate,
    ObjetivoSSTUpdate,
    ObjetivoSSTResponse,
)

router = APIRouter(
    prefix="/planear/objetivos-sst",
    tags=["PLANEAR - Objetivos SST"],
)


@router.post("/", response_model=ObjetivoSSTResponse)
def crear_objetivo(
    data: ObjetivoSSTCreate,
    db: Session = Depends(get_db),
):
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

    objetivo = ObjetivoSST(**data.model_dump())

    db.add(objetivo)
    db.commit()
    db.refresh(objetivo)

    return objetivo


@router.get("/", response_model=list[ObjetivoSSTResponse])
def listar_objetivos(
    db: Session = Depends(get_db),
):
    return (
        db.query(ObjetivoSST)
        .order_by(ObjetivoSST.id.desc())
        .all()
    )


@router.put("/{objetivo_id}")
def actualizar_objetivo(
    objetivo_id: int,
    data: ObjetivoSSTUpdate,
    db: Session = Depends(get_db),
):
    objetivo = (
        db.query(ObjetivoSST)
        .filter(ObjetivoSST.id == objetivo_id)
        .first()
    )

    if not objetivo:
        raise HTTPException(
            status_code=404,
            detail="Objetivo no encontrado",
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(objetivo, key, value)

    db.commit()

    return {"mensaje": "Objetivo actualizado"}


@router.delete("/{objetivo_id}")
def eliminar_objetivo(
    objetivo_id: int,
    db: Session = Depends(get_db),
):
    objetivo = (
        db.query(ObjetivoSST)
        .filter(ObjetivoSST.id == objetivo_id)
        .first()
    )

    if not objetivo:
        raise HTTPException(
            status_code=404,
            detail="Objetivo no encontrado",
        )

    objetivo.activo = False

    db.commit()

    return {"mensaje": "Objetivo desactivado"}