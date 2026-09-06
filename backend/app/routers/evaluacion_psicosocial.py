# ============================================================
# ROUTER: EVALUACIÓN PSICOSOCIAL SST
# Resolución 2646/2008 — Factores de riesgo psicosocial
# ============================================================

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_permission, get_current_user
from app.models.evaluacion_psicosocial import (
    EvaluacionPsicosocialSST,
    FactorPsicosocialSST,
    FACTORES_PSICOSOCIALES,
    NIVELES_RIESGO_PSICOSOCIAL,
)
from app.models.usuario import Usuario
from app.schemas.psicosocial_schema import (
    EvaluacionPsicosocialCreate,
    EvaluacionPsicosocialUpdate,
    EvaluacionPsicosocialResponse,
    EvaluacionPsicosocialList,
    FactorPsicosocialResponse,
)

router = APIRouter(
    prefix="/evaluaciones-psicosociales",
    tags=["Evaluaciones Psicosociales SST"],
)

PERM_CREAR = require_permission("EVALUACION_PSICOSOCIAL_CREAR")
PERM_LEER = require_permission("EVALUACION_PSICOSOCIAL_LEER")
PERM_ADMIN = require_permission("EVALUACION_PSICOSOCIAL_ADMINISTRAR")


def _empresa_id_autorizada(usuario: Usuario, empresa_id: int) -> int:
    if usuario.rol == "SUPER_ADMIN":
        return empresa_id
    if usuario.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acceso denegado a otra empresa")
    return empresa_id


def _calcular_nivel_riesgo(puntaje: float) -> str:
    if puntaje <= 2.0:
        return "BAJO"
    elif puntaje <= 3.0:
        return "MODERADO"
    elif puntaje <= 4.0:
        return "ALTO"
    return "MUY_ALTO"


# ── LISTAR ──────────────────────────────────────────────────────

@router.get("/{empresa_id}", response_model=list[EvaluacionPsicosocialList])
def listar_evaluaciones_psicosociales(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_LEER),
    activo: bool = Query(True),
    periodo: str | None = Query(None),
):
    _empresa_id_autorizada(usuario, empresa_id)

    query = (
        db.query(EvaluacionPsicosocialSST)
        .filter(EvaluacionPsicosocialSST.empresa_id == empresa_id)
    )

    if activo is not None:
        query = query.filter(EvaluacionPsicosocialSST.activo == activo)
    if periodo:
        query = query.filter(EvaluacionPsicosocialSST.periodo == periodo)

    return query.order_by(EvaluacionPsicosocialSST.fecha_evaluacion.desc()).all()


# ── OBTENER ────────────────────────────────────────────────────

@router.get("/{empresa_id}/{evaluacion_id}", response_model=EvaluacionPsicosocialResponse)
def obtener_evaluacion_psicosocial(
    empresa_id: int,
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_LEER),
):
    _empresa_id_autorizada(usuario, empresa_id)

    evaluacion = (
        db.query(EvaluacionPsicosocialSST)
        .filter(
            EvaluacionPsicosocialSST.id == evaluacion_id,
            EvaluacionPsicosocialSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación psicosocial no encontrada")

    return evaluacion


# ── CREAR ──────────────────────────────────────────────────────

@router.post("/{empresa_id}", response_model=EvaluacionPsicosocialResponse)
def crear_evaluacion_psicosocial(
    empresa_id: int,
    data: EvaluacionPsicosocialCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_CREAR),
):
    _empresa_id_autorizada(usuario, empresa_id)

    evaluacion = EvaluacionPsicosocialSST(
        empresa_id=empresa_id,
        empleado_id=data.empleado_id,
        fecha_evaluacion=data.fecha_evaluacion or datetime.utcnow(),
        periodo=data.periodo,
        evaluador=data.evaluador,
        conclusiones=data.conclusiones,
        recomendaciones=data.recomendaciones,
    )
    db.add(evaluacion)
    db.flush()

    for factor_data in data.factores:
        nivel = factor_data.nivel_riesgo or _calcular_nivel_riesgo(factor_data.puntuacion)
        factor = FactorPsicosocialSST(
            evaluacion_id=evaluacion.id,
            factor=factor_data.factor,
            dominio=factor_data.dominio,
            puntuacion=factor_data.puntuacion,
            nivel_riesgo=nivel,
            observacion=factor_data.observacion,
        )
        db.add(factor)

    # Calcular promedio
    if data.factores:
        promedio = sum(f.puntuacion for f in data.factores) / len(data.factores)
        evaluacion.puntaje_total = round(promedio, 2)
        evaluacion.nivel_riesgo = _calcular_nivel_riesgo(promedio)

    db.commit()
    db.refresh(evaluacion)
    return evaluacion


# ── ACTUALIZAR ─────────────────────────────────────────────────

@router.put("/{empresa_id}/{evaluacion_id}", response_model=EvaluacionPsicosocialResponse)
def actualizar_evaluacion_psicosocial(
    empresa_id: int,
    evaluacion_id: int,
    data: EvaluacionPsicosocialUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_CREAR),
):
    _empresa_id_autorizada(usuario, empresa_id)

    evaluacion = (
        db.query(EvaluacionPsicosocialSST)
        .filter(
            EvaluacionPsicosocialSST.id == evaluacion_id,
            EvaluacionPsicosocialSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación psicosocial no encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(evaluacion, field, value)
    evaluacion.fecha_actualizacion = datetime.utcnow()

    db.commit()
    db.refresh(evaluacion)
    return evaluacion


# ── ELIMINAR (soft delete) ─────────────────────────────────────

@router.delete("/{empresa_id}/{evaluacion_id}")
def eliminar_evaluacion_psicosocial(
    empresa_id: int,
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_ADMIN),
):
    _empresa_id_autorizada(usuario, empresa_id)

    evaluacion = (
        db.query(EvaluacionPsicosocialSST)
        .filter(
            EvaluacionPsicosocialSST.id == evaluacion_id,
            EvaluacionPsicosocialSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación psicosocial no encontrada")

    evaluacion.activo = False
    evaluacion.fecha_actualizacion = datetime.utcnow()
    db.commit()

    return {"mensaje": "Evaluación psicosocial desactivada"}


# ── CATÁLOGO DE FACTORES ──────────────────────────────────────

@router.get("/catalogo/factores")
def listar_factores_psicosociales():
    return FACTORES_PSICOSOCIALES


@router.get("/catalogo/niveles-riesgo")
def listar_niveles_riesgo():
    return NIVELES_RIESGO_PSICOSOCIAL


# ── RESUMEN POR EMPRESA ───────────────────────────────────────

@router.get("/{empresa_id}/resumen/estadisticas")
def resumen_evaluaciones_psicosociales(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_LEER),
):
    _empresa_id_autorizada(usuario, empresa_id)

    total = (
        db.query(func.count(EvaluacionPsicosocialSST.id))
        .filter(
            EvaluacionPsicosocialSST.empresa_id == empresa_id,
            EvaluacionPsicosocialSST.activo == True,
        )
        .scalar() or 0
    )

    por_nivel = (
        db.query(
            EvaluacionPsicosocialSST.nivel_riesgo,
            func.count(EvaluacionPsicosocialSST.id),
        )
        .filter(
            EvaluacionPsicosocialSST.empresa_id == empresa_id,
            EvaluacionPsicosocialSST.activo == True,
        )
        .group_by(EvaluacionPsicosocialSST.nivel_riesgo)
        .all()
    )

    return {
        "empresa_id": empresa_id,
        "total_evaluaciones": total,
        "por_nivel_riesgo": {nivel: count for nivel, count in por_nivel},
    }
