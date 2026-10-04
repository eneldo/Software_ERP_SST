from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
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

ROLES_LECTURA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "COORDINADOR_SST",
    "AUDITOR",
]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"]
ROLES_ADMIN = ["SUPER_ADMIN", "ADMIN_EMPRESA"]


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(
            status_code=403, detail="No tiene permisos sobre esta empresa"
        )
    return int(usuario_empresa_id)


def _objetivo_autorizado(db: Session, objetivo_id: int, usuario) -> ObjetivoSST:
    query = db.query(ObjetivoSST).filter(ObjetivoSST.id == objetivo_id)
    tenant_id = _empresa_id_autorizada(usuario, None)
    if tenant_id is not None:
        query = query.filter(ObjetivoSST.empresa_id == tenant_id)
    objetivo = query.first()
    if not objetivo:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    return objetivo


@router.post("/", response_model=ObjetivoSSTResponse)
def crear_objetivo(
    data: ObjetivoSSTCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    tenant_id = _empresa_id_autorizada(usuario, data.empresa_id)
    empresa = db.query(Empresa).filter(Empresa.id == tenant_id).first()

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    payload = data.model_dump()
    payload["empresa_id"] = tenant_id
    objetivo = ObjetivoSST(**payload)

    db.add(objetivo)
    db.commit()
    db.refresh(objetivo)

    return objetivo


@router.get("/", response_model=list[ObjetivoSSTResponse])
def listar_objetivos(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    query = db.query(ObjetivoSST)
    if tenant_id is not None:
        query = query.filter(ObjetivoSST.empresa_id == tenant_id)
    return query.order_by(ObjetivoSST.id.desc()).all()


@router.put("/{objetivo_id}")
def actualizar_objetivo(
    objetivo_id: int,
    data: ObjetivoSSTUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    objetivo = _objetivo_autorizado(db, objetivo_id, usuario)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(objetivo, key, value)

    db.commit()

    return {"mensaje": "Objetivo actualizado"}


@router.delete("/{objetivo_id}")
def eliminar_objetivo(
    objetivo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ADMIN)),
):
    objetivo = _objetivo_autorizado(db, objetivo_id, usuario)

    objetivo.activo = False

    db.commit()

    return {"mensaje": "Objetivo desactivado"}
