# ============================================================
# ROUTER EMERGENCIAS SST
# FASE auditoría - H-009
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.empresa import Empresa
from app.models.emergencia_sst import (
    BrigadaEmergencia, BrigadaIntegranteSST,
    SimulacroEmergencia, AmenazaEmergencia, InspeccionEmergencia,
)

from app.schemas.emergencia_sst_schema import (
    BrigadaCreate, BrigadaUpdate, BrigadaResponse, BrigadaIntegranteCreate, BrigadaIntegranteResponse,
    SimulacroCreate, SimulacroUpdate, SimulacroResponse,
    AmenazaCreate, AmenazaUpdate, AmenazaResponse,
    InspeccionEmergenciaCreate, InspeccionEmergenciaUpdate, InspeccionEmergenciaResponse,
)
from app.routers.empresas import validar_acceso_empresa


router = APIRouter(
    prefix="/sst/emergencias",
    tags=["SST - Emergencias"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


# ============================================================
# BRIGADAS
# ============================================================

@router.get("/brigadas", response_model=list[BrigadaResponse])
def listar_brigadas(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    validar_acceso_empresa(usuario, empresa_id)
    brigadas = (
        db.query(BrigadaEmergencia)
        .filter(BrigadaEmergencia.empresa_id == empresa_id, BrigadaEmergencia.activo == True)
        .all()
    )
    resultado = []
    for b in brigadas:
        integrantes = [i for i in b.integrantes if i.activo] if b.integrantes else []
        resultado.append(BrigadaResponse(
            id=b.id, empresa_id=b.empresa_id, nombre=b.nombre,
            tipo_brigada=b.tipo_brigada, descripcion=b.descripcion,
            fecha_conformacion=b.fecha_conformacion, activo=b.activo,
            fecha_creacion=b.fecha_creacion, total_integrantes=len(integrantes),
        ))
    return resultado


@router.post("/brigadas", response_model=BrigadaResponse)
def crear_brigada(
    data: BrigadaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    validar_acceso_empresa(usuario, data.empresa_id)
    brigada = BrigadaEmergencia(usuario_id=usuario.id, **data.model_dump())
    db.add(brigada)
    db.commit()
    db.refresh(brigada)
    return BrigadaResponse.model_validate(brigada)


@router.put("/brigadas/{brigada_id}", response_model=BrigadaResponse)
def actualizar_brigada(
    brigada_id: int,
    data: BrigadaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    brigada = db.query(BrigadaEmergencia).filter(BrigadaEmergencia.id == brigada_id).first()
    if not brigada:
        raise HTTPException(status_code=404, detail="Brigada no encontrada")
    validar_acceso_empresa(usuario, brigada.empresa_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(brigada, key, value)
    db.commit()
    db.refresh(brigada)
    return BrigadaResponse.model_validate(brigada)


@router.delete("/brigadas/{brigada_id}")
def eliminar_brigada(
    brigada_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    brigada = db.query(BrigadaEmergencia).filter(BrigadaEmergencia.id == brigada_id).first()
    if not brigada:
        raise HTTPException(status_code=404, detail="Brigada no encontrada")
    validar_acceso_empresa(usuario, brigada.empresa_id)
    brigada.activo = False
    db.commit()
    return {"mensaje": "Brigada desactivada correctamente"}


@router.post("/brigadas/{brigada_id}/integrantes", response_model=BrigadaIntegranteResponse)
def agregar_integrante_brigada(
    brigada_id: int,
    data: BrigadaIntegranteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    brigada = db.query(BrigadaEmergencia).filter(BrigadaEmergencia.id == brigada_id).first()
    if not brigada:
        raise HTTPException(status_code=404, detail="Brigada no encontrada")
    validar_acceso_empresa(usuario, brigada.empresa_id)

    integrante = BrigadaIntegranteSST(brigada_id=brigada_id, empresa_id=brigada.empresa_id, **data.model_dump())
    db.add(integrante)
    db.commit()
    db.refresh(integrante)
    return integrante


@router.get("/brigadas/{brigada_id}/integrantes", response_model=list[BrigadaIntegranteResponse])
def listar_integrantes_brigada(
    brigada_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    brigada = db.query(BrigadaEmergencia).filter(BrigadaEmergencia.id == brigada_id).first()
    if not brigada:
        raise HTTPException(status_code=404, detail="Brigada no encontrada")
    validar_acceso_empresa(usuario, brigada.empresa_id)
    return (
        db.query(BrigadaIntegranteSST)
        .filter(BrigadaIntegranteSST.brigada_id == brigada_id, BrigadaIntegranteSST.activo == True)
        .all()
    )


@router.delete("/brigadas/{brigada_id}/integrantes/{integrante_id}")
def eliminar_integrante_brigada(
    brigada_id: int,
    integrante_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    integrante = (
        db.query(BrigadaIntegranteSST)
        .filter(
            BrigadaIntegranteSST.id == integrante_id,
            BrigadaIntegranteSST.brigada_id == brigada_id,
        )
        .first()
    )
    if not integrante:
        raise HTTPException(status_code=404, detail="Integrante no encontrado")
    validar_acceso_empresa(usuario, integrante.empresa_id)
    integrante.activo = False
    db.commit()
    return {"mensaje": "Integrante removido correctamente"}


# ============================================================
# SIMULACROS
# ============================================================

@router.get("/simulacros", response_model=list[SimulacroResponse])
def listar_simulacros(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    validar_acceso_empresa(usuario, empresa_id)
    return (
        db.query(SimulacroEmergencia)
        .filter(SimulacroEmergencia.empresa_id == empresa_id, SimulacroEmergencia.activo == True)
        .order_by(SimulacroEmergencia.fecha_programada.desc())
        .all()
    )


@router.post("/simulacros", response_model=SimulacroResponse)
def crear_simulacro(
    data: SimulacroCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    validar_acceso_empresa(usuario, data.empresa_id)
    simulacro = SimulacroEmergencia(usuario_id=usuario.id, **data.model_dump())
    db.add(simulacro)
    db.commit()
    db.refresh(simulacro)
    return simulacro


@router.put("/simulacros/{simulacro_id}", response_model=SimulacroResponse)
def actualizar_simulacro(
    simulacro_id: int,
    data: SimulacroUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    simulacro = db.query(SimulacroEmergencia).filter(SimulacroEmergencia.id == simulacro_id).first()
    if not simulacro:
        raise HTTPException(status_code=404, detail="Simulacro no encontrado")
    validar_acceso_empresa(usuario, simulacro.empresa_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(simulacro, key, value)

    if data.estado:
        simulacro.estado = data.estado

    db.commit()
    db.refresh(simulacro)
    return simulacro


@router.delete("/simulacros/{simulacro_id}")
def eliminar_simulacro(
    simulacro_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    simulacro = db.query(SimulacroEmergencia).filter(SimulacroEmergencia.id == simulacro_id).first()
    if not simulacro:
        raise HTTPException(status_code=404, detail="Simulacro no encontrado")
    validar_acceso_empresa(usuario, simulacro.empresa_id)
    simulacro.activo = False
    db.commit()
    return {"mensaje": "Simulacro desactivado correctamente"}


# ============================================================
# AMENAZAS
# ============================================================

@router.get("/amenazas", response_model=list[AmenazaResponse])
def listar_amenazas(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    validar_acceso_empresa(usuario, empresa_id)
    return (
        db.query(AmenazaEmergencia)
        .filter(AmenazaEmergencia.empresa_id == empresa_id, AmenazaEmergencia.activo == True)
        .all()
    )


@router.post("/amenazas", response_model=AmenazaResponse)
def crear_amenaza(
    data: AmenazaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    validar_acceso_empresa(usuario, data.empresa_id)
    amenaza = AmenazaEmergencia(usuario_id=usuario.id, **data.model_dump())

    if data.probabilidad and data.impacto:
        niveles = {"BAJA": 1, "MEDIA": 2, "ALTA": 3}
        impactos = {"BAJO": 1, "MEDIO": 2, "ALTO": 3}
        prob = niveles.get(data.probabilidad.upper(), 1)
        imp = impactos.get(data.impacto.upper(), 1)
        total = prob * imp
        if total >= 6:
            amenaza.nivel_riesgo = "CRITICO"
        elif total >= 4:
            amenaza.nivel_riesgo = "ALTO"
        elif total >= 2:
            amenaza.nivel_riesgo = "MEDIO"
        else:
            amenaza.nivel_riesgo = "BAJO"

    db.add(amenaza)
    db.commit()
    db.refresh(amenaza)
    return amenaza


@router.put("/amenazas/{amenaza_id}", response_model=AmenazaResponse)
def actualizar_amenaza(
    amenaza_id: int,
    data: AmenazaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    amenaza = db.query(AmenazaEmergencia).filter(AmenazaEmergencia.id == amenaza_id).first()
    if not amenaza:
        raise HTTPException(status_code=404, detail="Amenaza no encontrada")
    validar_acceso_empresa(usuario, amenaza.empresa_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(amenaza, key, value)
    if amenaza.probabilidad and amenaza.impacto:
        niveles = {"BAJA": 1, "MEDIA": 2, "ALTA": 3}
        impactos = {"BAJO": 1, "MEDIO": 2, "ALTO": 3}
        total = niveles.get(amenaza.probabilidad.upper(), 1) * impactos.get(amenaza.impacto.upper(), 1)
        amenaza.nivel_riesgo = "CRITICO" if total >= 6 else "ALTO" if total >= 4 else "MEDIO" if total >= 2 else "BAJO"
    db.commit()
    db.refresh(amenaza)
    return amenaza


@router.delete("/amenazas/{amenaza_id}")
def eliminar_amenaza(
    amenaza_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    amenaza = db.query(AmenazaEmergencia).filter(AmenazaEmergencia.id == amenaza_id).first()
    if not amenaza:
        raise HTTPException(status_code=404, detail="Amenaza no encontrada")
    validar_acceso_empresa(usuario, amenaza.empresa_id)
    amenaza.activo = False
    db.commit()
    return {"mensaje": "Amenaza desactivada correctamente"}


# ============================================================
# INSPECCIONES EMERGENCIA
# ============================================================

@router.get("/inspecciones", response_model=list[InspeccionEmergenciaResponse])
def listar_inspecciones_emergencia(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    validar_acceso_empresa(usuario, empresa_id)
    return (
        db.query(InspeccionEmergencia)
        .filter(InspeccionEmergencia.empresa_id == empresa_id, InspeccionEmergencia.activo == True)
        .order_by(InspeccionEmergencia.fecha_inspeccion.desc())
        .all()
    )


@router.post("/inspecciones", response_model=InspeccionEmergenciaResponse)
def crear_inspeccion_emergencia(
    data: InspeccionEmergenciaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    validar_acceso_empresa(usuario, data.empresa_id)
    inspeccion = InspeccionEmergencia(usuario_id=usuario.id, **data.model_dump())
    db.add(inspeccion)
    db.commit()
    db.refresh(inspeccion)
    return inspeccion


@router.put("/inspecciones/{inspeccion_id}", response_model=InspeccionEmergenciaResponse)
def actualizar_inspeccion_emergencia(
    inspeccion_id: int,
    data: InspeccionEmergenciaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    inspeccion = db.query(InspeccionEmergencia).filter(InspeccionEmergencia.id == inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    validar_acceso_empresa(usuario, inspeccion.empresa_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inspeccion, key, value)
    db.commit()
    db.refresh(inspeccion)
    return inspeccion


@router.delete("/inspecciones/{inspeccion_id}")
def eliminar_inspeccion_emergencia(
    inspeccion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    inspeccion = db.query(InspeccionEmergencia).filter(InspeccionEmergencia.id == inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    validar_acceso_empresa(usuario, inspeccion.empresa_id)
    inspeccion.activo = False
    db.commit()
    return {"mensaje": "Inspección desactivada correctamente"}
