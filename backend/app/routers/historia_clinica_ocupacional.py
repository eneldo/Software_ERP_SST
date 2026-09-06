# ============================================================
# ROUTER: HISTORIA CLÍNICA OCUPACIONAL (HCO)
# Resolución 1843/2025 Art. 12 — Separada de concepto médico
# ============================================================

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_permission, get_current_user
from app.models.historia_clinica_ocupacional import HistoriaClinicaOcupacional
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/historia-clinica-ocupacional",
    tags=["Historia Clínica Ocupacional"],
)

PERM_VER_HCO = require_permission("HISTORIA_CLINICA_OCUPACIONAL_VER")
PERM_CREAR_HCO = require_permission("HISTORIA_CLINICA_OCUPACIONAL_CREAR")
PERM_ADMIN_HCO = require_permission("HISTORIA_CLINICA_OCUPACIONAL_ADMINISTRAR")


def _empresa_id_autorizada(usuario: Usuario, empresa_id: int) -> int:
    if usuario.rol == "SUPER_ADMIN":
        return empresa_id
    if usuario.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Acceso denegado a otra empresa")
    return empresa_id


def _sanitizar_hco(hco: HistoriaClinicaOcupacional, usuario: Usuario) -> dict:
    """Sanitiza campos sensibles según permisos del usuario.

    Solo médicos ocupacionales con permiso HISTORIA_CLINICA_ACCEDER
    pueden ver concepto médico y restricciones.
    """
    puede_ver_concepto = (
        usuario.rol in ("SUPER_ADMIN", "MEDICO_OCUPACIONAL")
        or any(
            getattr(p, "codigo", "") == "HISTORIA_CLINICA_ACCEDER"
            for p in getattr(usuario, "permisos", [])
        )
    )

    data = {
        "id": hco.id,
        "empresa_id": hco.empresa_id,
        "empleado_id": hco.empleado_id,
        "fecha_elaboracion": hco.fecha_elaboracion,
        "medico_cargo": hco.medico_cargo,
        "motivo_consulta": hco.motivo_consulta,
        "antecedentes_personales": hco.antecedentes_personales,
        "antecedentes_familiares": hco.antecedentes_familiares,
        "antecedentes_ocupacionales": hco.antecedentes_ocupacionales,
        "cargo_actual": hco.cargo_actual,
        "fecha_ingreso": hco.fecha_ingreso,
        "tiempo_exposicion": hco.tiempo_exposicion,
        "factores_riesgo": hco.factores_riesgo,
        "diagnostico": hco.diagnostico,
        "cie10": hco.cie10,
        "consentimiento_obtenido": hco.consentimiento_obtenido,
        "activo": hco.activo,
        "fecha_creacion": hco.fecha_creacion,
    }

    if puede_ver_concepto:
        data["concepto_medico"] = hco.concepto_medico
        data["aptitud"] = hco.aptitud
        data["restricciones_laborales"] = hco.restricciones_laborales
        data["recomendaciones"] = hco.recomendaciones
        data["examen_fisico_general"] = hco.examen_fisico_general
        data["signos_vitales"] = hco.signos_vitales
    else:
        data["concepto_medico"] = "[RESTRINGIDO]"
        data["aptitud"] = "[RESTRINGIDO]"
        data["restricciones_laborales"] = "[RESTRINGIDO]"
        data["recomendaciones"] = "[RESTRINGIDO]"
        data["examen_fisico_general"] = "[RESTRINGIDO]"
        data["signos_vitales"] = "[RESTRINGIDO]"

    return data


# ── LISTAR HCO POR EMPRESA ────────────────────────────────────

@router.get("/{empresa_id}")
def listar_historias_clinicas(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_VER_HCO),
    empleado_id: int | None = Query(None),
    activo: bool = Query(True),
):
    _empresa_id_autorizada(usuario, empresa_id)

    query = (
        db.query(HistoriaClinicaOcupacional)
        .filter(HistoriaClinicaOcupacional.empresa_id == empresa_id)
    )

    if empleado_id:
        query = query.filter(HistoriaClinicaOcupacional.empleado_id == empleado_id)
    if activo is not None:
        query = query.filter(HistoriaClinicaOcupacional.activo == activo)

    hcos = query.order_by(HistoriaClinicaOcupacional.fecha_elaboracion.desc()).all()
    return [_sanitizar_hco(hco, usuario) for hco in hcos]


# ── OBTENER HCO POR ID ────────────────────────────────────────

@router.get("/{empresa_id}/{hco_id}")
def obtener_historia_clinica(
    empresa_id: int,
    hco_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_VER_HCO),
):
    _empresa_id_autorizada(usuario, empresa_id)

    hco = (
        db.query(HistoriaClinicaOcupacional)
        .filter(
            HistoriaClinicaOcupacional.id == hco_id,
            HistoriaClinicaOcupacional.empresa_id == empresa_id,
        )
        .first()
    )
    if not hco:
        raise HTTPException(status_code=404, detail="Historia clínica ocupacional no encontrada")

    return _sanitizar_hco(hco, usuario)


# ── CREAR HCO ─────────────────────────────────────────────────

@router.post("/{empresa_id}")
def crear_historia_clinica(
    empresa_id: int,
    data: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_CREAR_HCO),
):
    _empresa_id_autorizada(usuario, empresa_id)

    hco = HistoriaClinicaOcupacional(
        empresa_id=empresa_id,
        empleado_id=data.get("empleado_id"),
        examen_medico_id=data.get("examen_medico_id"),
        fecha_elaboracion=data.get("fecha_elaboracion", datetime.utcnow()),
        medico_cargo=data.get("medico_cargo"),
        motivo_consulta=data.get("motivo_consulta"),
        antecedentes_personales=data.get("antecedentes_personales"),
        antecedentes_familiares=data.get("antecedentes_familiares"),
        antecedentes_ocupacionales=data.get("antecedentes_ocupacionales"),
        cargo_actual=data.get("cargo_actual"),
        fecha_ingreso=data.get("fecha_ingreso"),
        tiempo_exposicion=data.get("tiempo_exposicion"),
        factores_riesgo=data.get("factores_riesgo"),
        diagnostico=data.get("diagnostico"),
        cie10=data.get("cie10"),
        consentimiento_obtenido=data.get("consentimiento_obtenido", False),
        fecha_consentimiento=data.get("fecha_consentimiento"),
    )
    db.add(hco)
    db.commit()
    db.refresh(hco)

    return {"id": hco.id, "mensaje": "Historia clínica ocupacional creada"}


# ── ACTUALIZAR HCO ────────────────────────────────────────────

@router.put("/{empresa_id}/{hco_id}")
def actualizar_historia_clinica(
    empresa_id: int,
    hco_id: int,
    data: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_ADMIN_HCO),
):
    _empresa_id_autorizada(usuario, empresa_id)

    hco = (
        db.query(HistoriaClinicaOcupacional)
        .filter(
            HistoriaClinicaOcupacional.id == hco_id,
            HistoriaClinicaOcupacional.empresa_id == empresa_id,
        )
        .first()
    )
    if not hco:
        raise HTTPException(status_code=404, detail="Historia clínica ocupacional no encontrada")

    for key, value in data.items():
        if hasattr(hco, key) and key not in ("id", "empresa_id", "fecha_creacion"):
            setattr(hco, key, value)

    hco.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(hco)

    return {"mensaje": "Historia clínica ocupacional actualizada"}


# ── DESACTIVAR HCO ────────────────────────────────────────────

@router.delete("/{empresa_id}/{hco_id}")
def eliminar_historia_clinica(
    empresa_id: int,
    hco_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(PERM_ADMIN_HCO),
):
    _empresa_id_autorizada(usuario, empresa_id)

    hco = (
        db.query(HistoriaClinicaOcupacional)
        .filter(
            HistoriaClinicaOcupacional.id == hco_id,
            HistoriaClinicaOcupacional.empresa_id == empresa_id,
        )
        .first()
    )
    if not hco:
        raise HTTPException(status_code=404, detail="Historia clínica ocupacional no encontrada")

    hco.activo = False
    hco.fecha_actualizacion = datetime.utcnow()
    db.commit()

    return {"mensaje": "Historia clínica ocupacional desactivada"}
