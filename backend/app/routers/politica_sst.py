# ============================================================
# ROUTER POLÍTICA SST
# FASE 2.1 - PLANEAR SG-SST PRO
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.models.politica_sst import PoliticaSST
from app.schemas.politica_sst_schema import (
    PoliticaSSTCreate,
    PoliticaSSTUpdate,
    PoliticaSSTResponse,
)
from app.auth.dependencies import require_roles, require_permission
from app.core.default_permissions import PERM_DOCUMENTOS_APROBAR, PERM_REGISTROS_ELIMINAR


router = APIRouter(
    prefix="/planear/politica-sst",
    tags=["PLANEAR - Política SST PRO"]
)
APROBAR_DOCUMENTOS = require_permission(PERM_DOCUMENTOS_APROBAR)
ELIMINAR_REGISTROS = require_permission(PERM_REGISTROS_ELIMINAR)


@router.post("/", response_model=PoliticaSSTResponse)
def crear_politica_sst(
    data: PoliticaSSTCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    politica = PoliticaSST(**data.model_dump())

    db.add(politica)
    db.commit()
    db.refresh(politica)

    return politica


@router.get("/", response_model=list[PoliticaSSTResponse])
def listar_politicas_sst(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]))
):
    query = db.query(PoliticaSST)

    if empresa_id:
        query = query.filter(PoliticaSST.empresa_id == empresa_id)

    return query.order_by(PoliticaSST.id.desc()).all()


@router.get("/{politica_id}", response_model=PoliticaSSTResponse)
def obtener_politica_sst(
    politica_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]))
):
    politica = db.query(PoliticaSST).filter(PoliticaSST.id == politica_id).first()

    if not politica:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    return politica


@router.put("/{politica_id}", response_model=PoliticaSSTResponse)
def actualizar_politica_sst(
    politica_id: int,
    data: PoliticaSSTUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    politica = db.query(PoliticaSST).filter(PoliticaSST.id == politica_id).first()

    if not politica:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(politica, key, value)

    db.commit()
    db.refresh(politica)

    return politica


@router.delete("/{politica_id}")
def eliminar_politica_sst(
    politica_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(ELIMINAR_REGISTROS)
):
    politica = db.query(PoliticaSST).filter(PoliticaSST.id == politica_id).first()

    if not politica:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    politica.activo = False
    politica.estado = "OBSOLETA"

    db.commit()

    return {"mensaje": "Política SST desactivada correctamente"}


@router.patch("/{politica_id}/aprobar", response_model=PoliticaSSTResponse)
def aprobar_politica_sst(
    politica_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(APROBAR_DOCUMENTOS)
):
    politica = db.query(PoliticaSST).filter(PoliticaSST.id == politica_id).first()

    if not politica:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    politica.estado = "APROBADA"

    db.commit()
    db.refresh(politica)

    return politica
