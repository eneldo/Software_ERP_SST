# ============================================================
# ROUTER EVALUACIÓN KIRKPATRICK SST
# 4 niveles: Reacción / Aprendizaje / Comportamiento / Resultados
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.evaluacion_kirkpatrick import EvaluacionKirkpatrickSST
from app.models.capacitacion import CapacitacionSST
from app.models.empleado import Empleado
from app.schemas.evaluacion_kirkpatrick_schema import (
    EvaluacionKirkpatrickCreate,
    EvaluacionKirkpatrickUpdate,
    EvaluacionKirkpatrickResponse,
)

router = APIRouter(prefix="/kirkpatrick", tags=["Evaluación Kirkpatrick SST"])

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)


def _to_response(item: EvaluacionKirkpatrickSST) -> EvaluacionKirkpatrickResponse:
    data = EvaluacionKirkpatrickResponse.model_validate(item)
    data.capacitacion_nombre = item.capacitacion.nombre if item.capacitacion else None
    data.empleado_nombre = f"{item.empleado.nombres} {item.empleado.apellidos}" if item.empleado else None
    return data


@router.get("/", response_model=list[EvaluacionKirkpatrickResponse])
def listar_evaluaciones(
    empresa_id: int | None = Query(default=None),
    capacitacion_id: int | None = Query(default=None),
    nivel: int | None = Query(default=None, ge=1, le=4, description="Filtrar por nivel evaluado"),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_id_autorizada(usuario, empresa_id)
    query = db.query(EvaluacionKirkpatrickSST).filter(EvaluacionKirkpatrickSST.activo.is_(True))
    if empresa_id:
        query = query.filter(EvaluacionKirkpatrickSST.empresa_id == empresa_id)
    if capacitacion_id:
        query = query.filter(EvaluacionKirkpatrickSST.capacitacion_id == capacitacion_id)
    if nivel == 1:
        query = query.filter(EvaluacionKirkpatrickSST.nivel1_satisfaccion.isnot(None))
    elif nivel == 2:
        query = query.filter(EvaluacionKirkpatrickSST.nivel2_puntuacion_post.isnot(None))
    elif nivel == 3:
        query = query.filter(EvaluacionKirkpatrickSST.nivel3_aplicacion_pct.isnot(None))
    elif nivel == 4:
        query = query.filter(EvaluacionKirkpatrickSST.nivel4_valor_despues.isnot(None))
    items = query.order_by(EvaluacionKirkpatrickSST.id.desc()).all()
    return [_to_response(i) for i in items]


@router.post("/", response_model=EvaluacionKirkpatrickResponse)
def crear_evaluacion(
    data: EvaluacionKirkpatrickCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_id_autorizada(usuario, data.empresa_id)

    cap = db.query(CapacitacionSST).filter(CapacitacionSST.id == data.capacitacion_id).first()
    if not cap:
        raise HTTPException(status_code=404, detail="Capacitación no encontrada")
    if cap.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="La capacitación no pertenece a esta empresa")

    if data.empleado_id:
        emp = db.query(Empleado).filter(Empleado.id == data.empleado_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

    payload = data.model_dump()
    payload["empresa_id"] = empresa_id
    item = EvaluacionKirkpatrickSST(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.get("/{evaluacion_id}", response_model=EvaluacionKirkpatrickResponse)
def obtener_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EvaluacionKirkpatrickSST).filter(EvaluacionKirkpatrickSST.id == evaluacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Evaluación Kirkpatrick no encontrada")
    _empresa_id_autorizada(usuario, item.empresa_id)
    return _to_response(item)


@router.put("/{evaluacion_id}", response_model=EvaluacionKirkpatrickResponse)
def actualizar_evaluacion(
    evaluacion_id: int,
    data: EvaluacionKirkpatrickUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EvaluacionKirkpatrickSST).filter(EvaluacionKirkpatrickSST.id == evaluacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Evaluación Kirkpatrick no encontrada")
    _empresa_id_autorizada(usuario, item.empresa_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_response(item)


@router.delete("/{evaluacion_id}")
def eliminar_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EvaluacionKirkpatrickSST).filter(EvaluacionKirkpatrickSST.id == evaluacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Evaluación Kirkpatrick no encontrada")
    _empresa_id_autorizada(usuario, item.empresa_id)
    item.activo = False
    db.commit()
    return {"ok": True, "mensaje": "Evaluación Kirkpatrick eliminada"}


@router.get("/resumen/{capacitacion_id}")
def resumen_kirkpatrick(
    capacitacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    cap = db.query(CapacitacionSST).filter(CapacitacionSST.id == capacitacion_id).first()
    if not cap:
        raise HTTPException(status_code=404, detail="Capacitación no encontrada")
    _empresa_id_autorizada(usuario, cap.empresa_id)

    items = db.query(EvaluacionKirkpatrickSST).filter(
        EvaluacionKirkpatrickSST.capacitacion_id == capacitacion_id,
        EvaluacionKirkpatrickSST.activo.is_(True),
    ).all()

    total = len(items)
    if total == 0:
        return {"total": 0, "nivel1": {}, "nivel2": {}, "nivel3": {}, "nivel4": {}}

    satisfacciones = [i.nivel1_satisfaccion for i in items if i.nivel1_satisfaccion is not None]
    nivel1_avg = round(sum(satisfacciones) / len(satisfacciones), 2) if satisfacciones else None

    pre = [float(i.nivel2_puntuacion_pre) for i in items if i.nivel2_puntuacion_pre is not None]
    post = [float(i.nivel2_puntuacion_post) for i in items if i.nivel2_puntuacion_post is not None]
    aprobados = sum(1 for i in items if i.nivel2_aprobado)

    aplicaciones = [float(i.nivel3_aplicacion_pct) for i in items if i.nivel3_aplicacion_pct is not None]
    nivel3_avg = round(sum(aplicaciones) / len(aplicaciones), 2) if aplicaciones else None

    impactos = []
    for i in items:
        if i.nivel4_valor_antes is not None and i.nivel4_valor_despues is not None:
            impactos.append({
                "indicador": i.nivel4_indicador,
                "antes": float(i.nivel4_valor_antes),
                "despues": float(i.nivel4_valor_despues),
                "variacion": round(float(i.nivel4_valor_despues) - float(i.nivel4_valor_antes), 2),
            })

    return {
        "total": total,
        "nivel1": {
            "satisfaccion_promedio": nivel1_avg,
            "total_evaluados": len(satisfacciones),
        },
        "nivel2": {
            "pre_promedio": round(sum(pre) / len(pre), 2) if pre else None,
            "post_promedio": round(sum(post) / len(post), 2) if post else None,
            "aprobados": aprobados,
            "total_evaluados": len(post),
        },
        "nivel3": {
            "aplicacion_promedio": nivel3_avg,
            "total_evaluados": len(aplicaciones),
        },
        "nivel4": {
            "impactos": impactos,
            "total_con_impacto": len(impactos),
        },
    }
