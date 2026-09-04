from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models.profesiograma import (
    TipoEvaluacionMedica,
    ExamenEvaluacionCatalogo,
    Profesiograma,
    ProfesiogramaEvaluacion,
)
from app.models.cargo import Cargo
from app.models.empresa import Empresa
from app.schemas.profesiograma_schema import (
    TipoEvaluacionMedicaCreate,
    TipoEvaluacionMedicaUpdate,
    TipoEvaluacionMedicaResponse,
    ExamenEvaluacionCatalogoCreate,
    ExamenEvaluacionCatalogoUpdate,
    ExamenEvaluacionCatalogoResponse,
    ProfesiogramaCreate,
    ProfesiogramaUpdate,
    ProfesiogramaResponse,
    ProfesiogramaEvaluacionResponse,
)
from app.auth.dependencies import require_roles

router = APIRouter(prefix="/profesiograma", tags=["Profesiograma"])
ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


def _serializar_evaluacion(ev):
    return ProfesiogramaEvaluacionResponse(
        id=ev.id,
        tipo_evaluacion_id=ev.tipo_evaluacion_id,
        examenes_requeridos=ev.examenes_requeridos,
        activo=ev.activo,
        tipo_evaluacion_codigo=ev.tipo_evaluacion.codigo if ev.tipo_evaluacion else None,
        tipo_evaluacion_nombre=ev.tipo_evaluacion.nombre if ev.tipo_evaluacion else None,
    )


def _serializar_profesiograma(prof):
    return ProfesiogramaResponse(
        id=prof.id,
        cargo_id=prof.cargo_id,
        empresa_id=prof.empresa_id,
        riesgos_asociados=prof.riesgos_asociados,
        activo=prof.activo,
        fecha_creacion=prof.fecha_creacion,
        fecha_actualizacion=prof.fecha_actualizacion,
        cargo_nombre=prof.cargo.nombre if prof.cargo else None,
        empresa_nombre=prof.empresa.nombre if prof.empresa else None,
        evaluaciones=[_serializar_evaluacion(ev) for ev in prof.evaluaciones],
    )


# ── Tipos de Evaluación Médica ──────────────────────────────

@router.get("/tipos-evaluacion", response_model=list[TipoEvaluacionMedicaResponse])
def listar_tipos_evaluacion(
    solo_activos: bool = Query(default=True),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    q = db.query(TipoEvaluacionMedica)
    if solo_activos:
        q = q.filter(TipoEvaluacionMedica.activo.is_(True))
    return q.order_by(TipoEvaluacionMedica.id.asc()).all()


@router.post("/tipos-evaluacion", response_model=TipoEvaluacionMedicaResponse)
def crear_tipo_evaluacion(
    data: TipoEvaluacionMedicaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    existente = db.query(TipoEvaluacionMedica).filter(TipoEvaluacionMedica.codigo == data.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un tipo de evaluacion con ese codigo")
    item = TipoEvaluacionMedica(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/tipos-evaluacion/{tipo_id}", response_model=TipoEvaluacionMedicaResponse)
def actualizar_tipo_evaluacion(
    tipo_id: int,
    data: TipoEvaluacionMedicaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(TipoEvaluacionMedica).filter(TipoEvaluacionMedica.id == tipo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Tipo de evaluacion no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/tipos-evaluacion/{tipo_id}")
def eliminar_tipo_evaluacion(
    tipo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(TipoEvaluacionMedica).filter(TipoEvaluacionMedica.id == tipo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Tipo de evaluacion no encontrado")
    item.activo = False
    db.commit()
    return {"ok": True}


# ── Catálogo de Exámenes ────────────────────────────────────

@router.get("/examenes-catalogo", response_model=list[ExamenEvaluacionCatalogoResponse])
def listar_examenes_catalogo(
    solo_activos: bool = Query(default=True),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    q = db.query(ExamenEvaluacionCatalogo)
    if solo_activos:
        q = q.filter(ExamenEvaluacionCatalogo.activo.is_(True))
    return q.order_by(ExamenEvaluacionCatalogo.id.asc()).all()


@router.post("/examenes-catalogo", response_model=ExamenEvaluacionCatalogoResponse)
def crear_examen_catalogo(
    data: ExamenEvaluacionCatalogoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    existente = db.query(ExamenEvaluacionCatalogo).filter(ExamenEvaluacionCatalogo.codigo == data.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un examen con ese codigo")
    item = ExamenEvaluacionCatalogo(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/examenes-catalogo/{examen_id}", response_model=ExamenEvaluacionCatalogoResponse)
def actualizar_examen_catalogo(
    examen_id: int,
    data: ExamenEvaluacionCatalogoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(ExamenEvaluacionCatalogo).filter(ExamenEvaluacionCatalogo.id == examen_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/examenes-catalogo/{examen_id}")
def eliminar_examen_catalogo(
    examen_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(ExamenEvaluacionCatalogo).filter(ExamenEvaluacionCatalogo.id == examen_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    item.activo = False
    db.commit()
    return {"ok": True}


# ── Profesiograma ───────────────────────────────────────────

@router.get("/cargo/{cargo_id}", response_model=ProfesiogramaResponse)
def obtener_profesiograma(
    cargo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    prof = (
        db.query(Profesiograma)
        .options(
            joinedload(Profesiograma.cargo),
            joinedload(Profesiograma.empresa),
            joinedload(Profesiograma.evaluaciones).joinedload(ProfesiogramaEvaluacion.tipo_evaluacion),
        )
        .filter(Profesiograma.cargo_id == cargo_id)
        .first()
    )
    if not prof:
        raise HTTPException(status_code=404, detail="Profesiograma no encontrado para este cargo")
    return _serializar_profesiograma(prof)


@router.post("/cargo/{cargo_id}", response_model=ProfesiogramaResponse)
def crear_o_actualizar_profesiograma(
    cargo_id: int,
    data: ProfesiogramaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")

    prof = db.query(Profesiograma).filter(Profesiograma.cargo_id == cargo_id).first()

    if prof:
        prof.riesgos_asociados = data.riesgos_asociados
        prof.empresa_id = data.empresa_id
        db.query(ProfesiogramaEvaluacion).filter(
            ProfesiogramaEvaluacion.profesiograma_id == prof.id
        ).delete()
    else:
        prof = Profesiograma(
            cargo_id=cargo_id,
            empresa_id=data.empresa_id,
            riesgos_asociados=data.riesgos_asociados,
        )
        db.add(prof)
        db.flush()

    for ev_data in data.evaluaciones:
        ev = ProfesiogramaEvaluacion(
            profesiograma_id=prof.id,
            tipo_evaluacion_id=ev_data.tipo_evaluacion_id,
            examenes_requeridos=ev_data.examenes_requeridos,
        )
        db.add(ev)

    db.commit()

    prof = (
        db.query(Profesiograma)
        .options(
            joinedload(Profesiograma.cargo),
            joinedload(Profesiograma.empresa),
            joinedload(Profesiograma.evaluaciones).joinedload(ProfesiogramaEvaluacion.tipo_evaluacion),
        )
        .filter(Profesiograma.id == prof.id)
        .first()
    )
    return _serializar_profesiograma(prof)


@router.delete("/{profesiograma_id}")
def eliminar_profesiograma(
    profesiograma_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    prof = db.query(Profesiograma).filter(Profesiograma.id == profesiograma_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profesiograma no encontrado")
    db.delete(prof)
    db.commit()
    return {"ok": True}


@router.get("/listar", response_model=list[ProfesiogramaResponse])
def listar_profesiogramas(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    q = (
        db.query(Profesiograma)
        .options(
            joinedload(Profesiograma.cargo),
            joinedload(Profesiograma.empresa),
            joinedload(Profesiograma.evaluaciones).joinedload(ProfesiogramaEvaluacion.tipo_evaluacion),
        )
        .filter(Profesiograma.activo.is_(True))
    )
    if empresa_id:
        q = q.filter(Profesiograma.empresa_id == empresa_id)
    items = q.order_by(Profesiograma.id.desc()).all()
    return [_serializar_profesiograma(p) for p in items]
