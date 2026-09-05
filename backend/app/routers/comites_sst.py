# ============================================================
# ROUTER COMITÉS SST - COPASST / VIGÍA SST
# FASE auditoría - H-008
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.empresa import Empresa
from app.models.comite_sst import ComiteSST, ComiteIntegranteSST, ComiteReunionSST

from app.schemas.comite_sst_schema import (
    ComiteCreate,
    ComiteUpdate,
    ComiteResponse,
    ComiteIntegranteCreate,
    ComiteIntegranteResponse,
    ComiteReunionCreate,
    ComiteReunionResponse,
)
from app.routers.empresas import validar_acceso_empresa


router = APIRouter(
    prefix="/sst/comites",
    tags=["SST - Comités COPASST / Vigía"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST", "COPASST", "VIGIA_SST"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


def serializar_comite(comite: ComiteSST) -> dict:
    return {
        "id": comite.id,
        "empresa_id": comite.empresa_id,
        "tipo_comite": comite.tipo_comite,
        "nombre": comite.nombre,
        "descripcion": comite.descripcion,
        "fecha_constitucion": comite.fecha_constitucion,
        "fecha_fin_periodo": comite.fecha_fin_periodo,
        "vigente": comite.vigente,
        "observaciones": comite.observaciones,
        "activo": comite.activo,
        "fecha_creacion": comite.fecha_creacion,
        "fecha_actualizacion": comite.fecha_actualizacion,
        "total_integrantes": len([i for i in comite.integrantes if i.activo]) if comite.integrantes else 0,
        "total_reuniones": len([r for r in comite.reuniones if r.activo]) if comite.reuniones else 0,
    }


@router.get("/", response_model=list[ComiteResponse])
def listar_comites(
    empresa_id: int,
    tipo_comite: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    validar_acceso_empresa(usuario, empresa_id)
    query = (
        db.query(ComiteSST)
        .options(
            joinedload(ComiteSST.integrantes),
            joinedload(ComiteSST.reuniones),
        )
        .filter(ComiteSST.empresa_id == empresa_id, ComiteSST.activo == True)
    )
    if tipo_comite:
        query = query.filter(ComiteSST.tipo_comite == tipo_comite.upper())
    comites = query.order_by(ComiteSST.id.desc()).all()
    return [serializar_comite(c) for c in comites]


@router.post("/", response_model=ComiteResponse)
def crear_comite(
    data: ComiteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    validar_acceso_empresa(usuario, data.empresa_id)

    comite = ComiteSST(
        empresa_id=data.empresa_id,
        usuario_id=usuario.id,
        tipo_comite=data.tipo_comite.upper(),
        nombre=data.nombre,
        descripcion=data.descripcion,
        fecha_constitucion=data.fecha_constitucion,
        fecha_fin_periodo=data.fecha_fin_periodo,
        observaciones=data.observaciones,
    )
    db.add(comite)
    db.commit()
    db.refresh(comite)
    return serializar_comite(comite)


@router.get("/{comite_id}", response_model=ComiteResponse)
def obtener_comite(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    comite = (
        db.query(ComiteSST)
        .options(
            joinedload(ComiteSST.integrantes),
            joinedload(ComiteSST.reuniones),
        )
        .filter(ComiteSST.id == comite_id)
        .first()
    )
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    return serializar_comite(comite)


@router.put("/{comite_id}", response_model=ComiteResponse)
def actualizar_comite(
    comite_id: int,
    data: ComiteUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(comite, key, value)

    db.commit()
    db.refresh(comite)

    comite = (
        db.query(ComiteSST)
        .options(joinedload(ComiteSST.integrantes), joinedload(ComiteSST.reuniones))
        .filter(ComiteSST.id == comite_id)
        .first()
    )
    return serializar_comite(comite)


@router.delete("/{comite_id}")
def eliminar_comite(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    comite.activo = False
    db.commit()
    return {"mensaje": "Comité desactivado correctamente"}


# ============================================================
# INTEGRANTES
# ============================================================

@router.get("/{comite_id}/integrantes", response_model=list[ComiteIntegranteResponse])
def listar_integrantes(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    integrantes = (
        db.query(ComiteIntegranteSST)
        .filter(ComiteIntegranteSST.comite_id == comite_id, ComiteIntegranteSST.activo == True)
        .all()
    )
    return integrantes


@router.post("/{comite_id}/integrantes", response_model=ComiteIntegranteResponse)
def agregar_integrante(
    comite_id: int,
    data: ComiteIntegranteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)

    integrante = ComiteIntegranteSST(
        comite_id=comite_id,
        empresa_id=comite.empresa_id,
        **data.model_dump(),
    )
    db.add(integrante)
    db.commit()
    db.refresh(integrante)
    return integrante


@router.delete("/{comite_id}/integrantes/{integrante_id}")
def eliminar_integrante(
    comite_id: int,
    integrante_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    integrante = (
        db.query(ComiteIntegranteSST)
        .filter(ComiteIntegranteSST.id == integrante_id, ComiteIntegranteSST.comite_id == comite_id)
        .first()
    )
    if not integrante:
        raise HTTPException(status_code=404, detail="Integrante no encontrado")
    validar_acceso_empresa(usuario, integrante.empresa_id)
    integrante.activo = False
    db.commit()
    return {"mensaje": "Integrante removido correctamente"}


# ============================================================
# REUNIONES
# ============================================================

@router.get("/{comite_id}/reuniones", response_model=list[ComiteReunionResponse])
def listar_reuniones(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    reuniones = (
        db.query(ComiteReunionSST)
        .filter(ComiteReunionSST.comite_id == comite_id, ComiteReunionSST.activo == True)
        .order_by(ComiteReunionSST.fecha_reunion.desc())
        .all()
    )
    return reuniones


@router.post("/{comite_id}/reuniones", response_model=ComiteReunionResponse)
def crear_reunion(
    comite_id: int,
    data: ComiteReunionCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)

    reunion = ComiteReunionSST(
        comite_id=comite_id,
        empresa_id=comite.empresa_id,
        usuario_id=usuario.id,
        **data.model_dump(),
    )
    db.add(reunion)
    db.commit()
    db.refresh(reunion)
    return reunion


@router.put("/{comite_id}/reuniones/{reunion_id}", response_model=ComiteReunionResponse)
def actualizar_reunion(
    comite_id: int,
    reunion_id: int,
    data: ComiteReunionCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    reunion = (
        db.query(ComiteReunionSST)
        .filter(ComiteReunionSST.id == reunion_id, ComiteReunionSST.comite_id == comite_id)
        .first()
    )
    if not reunion:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    validar_acceso_empresa(usuario, reunion.empresa_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(reunion, key, value)

    db.commit()
    db.refresh(reunion)
    return reunion
