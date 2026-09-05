# ============================================================
# ROUTER INDICADORES OFICIALES SST
# H-016: TF, TG, TI, Mortalidad, Ausentismo
# ============================================================

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.usuario import Usuario
from app.services.indicadores_oficiales_service import (
    calcular_indicadores_oficiales,
    calcular_tasa_frecuencia,
    calcular_tasa_gravedad,
    calcular_tasa_incapacidad,
    calcular_tasa_mortalidad,
    calcular_tasa_ausentismo,
)

router = APIRouter(
    prefix="/indicadores/oficiales",
    tags=["H-016: Indicadores Oficiales SST"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST", "AUDITOR_INT"]


@router.get("/")
def obtener_indicadores_oficiales(
    empresa_id: int,
    fecha_inicio: date = Query(..., description="Fecha inicio del periodo"),
    fecha_fin: date = Query(..., description="Fecha fin del periodo"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_LECTURA)),
):
    return calcular_indicadores_oficiales(db, empresa_id, fecha_inicio, fecha_fin)


@router.get("/tasa-frecuencia")
def obtener_tasa_frecuencia(
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_LECTURA)),
):
    return calcular_tasa_frecuencia(db, empresa_id, fecha_inicio, fecha_fin)


@router.get("/tasa-gravedad")
def obtener_tasa_gravedad(
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_LECTURA)),
):
    return calcular_tasa_gravedad(db, empresa_id, fecha_inicio, fecha_fin)


@router.get("/tasa-incapacidad")
def obtener_tasa_incapacidad(
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_LECTURA)),
):
    return calcular_tasa_incapacidad(db, empresa_id, fecha_inicio, fecha_fin)


@router.get("/mortalidad")
def obtener_tasa_mortalidad(
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_LECTURA)),
):
    return calcular_tasa_mortalidad(db, empresa_id, fecha_inicio, fecha_fin)


@router.get("/ausentismo")
def obtener_tasa_ausentismo(
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_LECTURA)),
):
    return calcular_tasa_ausentismo(db, empresa_id, fecha_inicio, fecha_fin)
