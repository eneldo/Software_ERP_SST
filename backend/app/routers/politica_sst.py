# ============================================================
# ROUTER POLÍTICA SST
# FASE 2.1 - PLANEAR SG-SST PRO
# H-009: Políticas obligatorias diferenciadas
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

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

TIPOS_POLITICA_VALIDOS = {
    "POLITICA_SST",
    "CONVIVENCIA",
    "ALCOHOL_TABACO",
    "PREVENCION_INCENDIOS",
    "PROTECCION_DATOS",
}


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)


@router.post("/", response_model=PoliticaSSTResponse)
def crear_politica_sst(
    data: PoliticaSSTCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    empresa_id = _empresa_id_autorizada(usuario, data.empresa_id)

    if data.tipo_politica not in TIPOS_POLITICA_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de política no válido. Use: {', '.join(sorted(TIPOS_POLITICA_VALIDOS))}"
        )

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    existe = db.query(PoliticaSST).filter(
        and_(
            PoliticaSST.empresa_id == empresa_id,
            PoliticaSST.tipo_politica == data.tipo_politica,
            PoliticaSST.version == data.version,
            PoliticaSST.activo == True,
        )
    ).first()

    if existe:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe una política tipo '{data.tipo_politica}' versión {data.version}"
        )

    politica = PoliticaSST(**data.model_dump())
    politica.empresa_id = empresa_id

    db.add(politica)
    db.commit()
    db.refresh(politica)

    return politica


@router.get("/", response_model=list[PoliticaSSTResponse])
def listar_politicas_sst(
    empresa_id: int | None = None,
    tipo_politica: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]))
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)

    query = db.query(PoliticaSST).filter(PoliticaSST.activo == True)

    if tenant_id is not None:
        query = query.filter(PoliticaSST.empresa_id == tenant_id)

    if tipo_politica:
        query = query.filter(PoliticaSST.tipo_politica == tipo_politica.upper())

    if estado:
        query = query.filter(PoliticaSST.estado == estado.upper())

    return query.order_by(PoliticaSST.tipo_politica, PoliticaSST.id.desc()).all()


@router.get("/tipos")
def listar_tipos_politica():
    return [
        {"codigo": t, "nombre": t.replace("_", " ").title(), "obligatoria": t in TIPOS_OBLIGATORIOS}
        for t in sorted(TIPOS_POLITICA_VALIDOS)
    ]


TIPOS_OBLIGATORIOS = {"POLITICA_SST", "CONVIVENCIA", "ALCOHOL_TABACO"}


@router.get("/verificar-obligatorias")
def verificar_politicas_obligatorias(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="Se requiere empresa_id")

    obligatorias = {}
    for tipo in TIPOS_OBLIGATORIOS:
        aprobada = db.query(PoliticaSST).filter(
            PoliticaSST.empresa_id == tenant_id,
            PoliticaSST.tipo_politica == tipo,
            PoliticaSST.estado == "APROBADA",
            PoliticaSST.activo == True,
        ).first()
        any_version = db.query(PoliticaSST).filter(
            PoliticaSST.empresa_id == tenant_id,
            PoliticaSST.tipo_politica == tipo,
            PoliticaSST.activo == True,
        ).first()
        obligatorias[tipo] = {
            "tipo": tipo,
            "nombre": tipo.replace("_", " ").title(),
            "aprobada": aprobada is not None,
            "existe": any_version is not None,
            "politica_id": (aprobada or any_version).id if (aprobada or any_version) else None,
            "version": (aprobada or any_version).version if (aprobada or any_version) else None,
        }

    total = len(TIPOS_OBLIGATORIOS)
    aprobadas = sum(1 for v in obligatorias.values() if v["aprobada"])
    return {
        "empresa_id": tenant_id,
        "total_obligatorias": total,
        "aprobadas": aprobadas,
        "pendientes": total - aprobadas,
        "cumple": aprobadas == total,
        "detalles": list(obligatorias.values()),
    }


@router.get("/{politica_id}", response_model=PoliticaSSTResponse)
def obtener_politica_sst(
    politica_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]))
):
    politica = db.query(PoliticaSST).filter(PoliticaSST.id == politica_id).first()

    if not politica:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    tenant_id = _empresa_id_autorizada(usuario, None)
    if tenant_id is not None and politica.empresa_id != tenant_id:
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

    tenant_id = _empresa_id_autorizada(usuario, None)
    if tenant_id is not None and politica.empresa_id != tenant_id:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    if politica.estado == "APROBADA" and data.estado and data.estado != "APROBADA":
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar una política aprobada. Cree una nueva versión."
        )

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

    tenant_id = _empresa_id_autorizada(usuario, None)
    if tenant_id is not None and politica.empresa_id != tenant_id:
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

    tenant_id = _empresa_id_autorizada(usuario, None)
    if tenant_id is not None and politica.empresa_id != tenant_id:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    if politica.estado == "APROBADA":
        raise HTTPException(status_code=400, detail="La política ya está aprobada")

    politica.estado = "APROBADA"

    db.commit()
    db.refresh(politica)

    return politica
