# ============================================================
# ROUTER ESTANDARES MINIMOS CRITERIOS
# H-017: CRUD + Historial + Vinculación plan mejora
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.estandar_minimo_criterio import EstandarMinimoCriterio
from app.models.estandar_minimo_historial import EstandarMinimoHistorial
from app.schemas.estandar_minimo_schema import (
    EstandarMinimoCriterioCreate,
    EstandarMinimoCriterioUpdate,
    EstandarMinimoCriterioResponse,
    EstandarMinimoHistorialResponse,
)

router = APIRouter(
    prefix="/planear/estandares-minimos",
    tags=["H-017: Estándares Mínimos SST"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST", "AUDITOR_INT"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


def _registrar_historial(
    db: Session,
    estandar_id: int,
    tipo_cambio: str,
    descripcion: str,
    valor_anterior: str | None = None,
    valor_nuevo: str | None = None,
    usuario_id: int | None = None,
    empresa_id: int | None = None,
):
    historial = EstandarMinimoHistorial(
        estandar_criterio_id=estandar_id,
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        tipo_cambio=tipo_cambio,
        descripcion_cambio=descripcion,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
    )
    db.add(historial)


@router.get("/", response_model=list[EstandarMinimoCriterioResponse])
def listar_estandares(
    tipo_estandares: str = "7",
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return (
        db.query(EstandarMinimoCriterio)
        .filter(
            EstandarMinimoCriterio.tipo_estandares == tipo_estandares,
            EstandarMinimoCriterio.activo == True,
        )
        .order_by(EstandarMinimoCriterio.numeral)
        .all()
    )


@router.get("/todos", response_model=list[EstandarMinimoCriterioResponse])
def listar_todos_estandares(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return (
        db.query(EstandarMinimoCriterio)
        .filter(EstandarMinimoCriterio.activo == True)
        .order_by(EstandarMinimoCriterio.tipo_estandares, EstandarMinimoCriterio.numeral)
        .all()
    )


@router.get("/{item_id}", response_model=EstandarMinimoCriterioResponse)
def obtener_estandar(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    item = db.query(EstandarMinimoCriterio).filter(EstandarMinimoCriterio.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")
    return item


@router.post("/", response_model=EstandarMinimoCriterioResponse)
def crear_estandar(
    data: EstandarMinimoCriterioCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = EstandarMinimoCriterio(
        tipo_estandares=data.tipo_estandares,
        estandar=data.estandar,
        numeral=data.numeral,
        criterio=data.criterio,
        puntaje=data.puntaje,
        version_norma=data.version_norma,
    )
    db.add(item)
    db.flush()

    _registrar_historial(
        db, item.id, "CREACION",
        f"Criterio creado: {item.estandar} - {item.numeral}",
        valor_nuevo=item.criterio,
        usuario_id=usuario.id,
        empresa_id=getattr(usuario, "empresa_id", None),
    )

    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=EstandarMinimoCriterioResponse)
def actualizar_estandar(
    item_id: int,
    data: EstandarMinimoCriterioUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = db.query(EstandarMinimoCriterio).filter(EstandarMinimoCriterio.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")

    cambios = []
    for field, value in data.model_dump(exclude_unset=True).items():
        old = getattr(item, field)
        if old != value:
            cambios.append(f"{field}: {old} → {value}")
            setattr(item, field, value)

    if cambios:
        _registrar_historial(
            db, item.id, "MODIFICACION",
            "; ".join(cambios),
            usuario_id=usuario.id,
            empresa_id=getattr(usuario, "empresa_id", None),
        )

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def eliminar_estandar(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = db.query(EstandarMinimoCriterio).filter(EstandarMinimoCriterio.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")

    item.activo = False
    _registrar_historial(
        db, item.id, "DESACTIVACION",
        f"Criterio desactivado: {item.estandar}",
        usuario_id=usuario.id,
        empresa_id=getattr(usuario, "empresa_id", None),
    )
    db.commit()

    return {"mensaje": "Criterio desactivado correctamente"}


@router.get("/{item_id}/historial", response_model=list[EstandarMinimoHistorialResponse])
def listar_historial_estandar(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    item = db.query(EstandarMinimoCriterio).filter(EstandarMinimoCriterio.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Criterio no encontrado")

    return (
        db.query(EstandarMinimoHistorial)
        .filter(
            EstandarMinimoHistorial.estandar_criterio_id == item_id,
            EstandarMinimoHistorial.activo == True,
        )
        .order_by(EstandarMinimoHistorial.fecha_creacion.desc())
        .all()
    )


@router.get("/resumen/{tipo_estandares}")
def resumen_estandares(
    tipo_estandares: str,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    total = (
        db.query(func.count(EstandarMinimoCriterio.id))
        .filter(
            EstandarMinimoCriterio.tipo_estandares == tipo_estandares,
            EstandarMinimoCriterio.activo == True,
        )
        .scalar()
    )

    puntaje_total = (
        db.query(func.coalesce(func.sum(EstandarMinimoCriterio.puntaje), 0))
        .filter(
            EstandarMinimoCriterio.tipo_estandares == tipo_estandares,
            EstandarMinimoCriterio.activo == True,
        )
        .scalar()
    )

    return {
        "tipo_estandares": tipo_estandares,
        "total_criterios": total,
        "puntaje_total": puntaje_total,
    }
