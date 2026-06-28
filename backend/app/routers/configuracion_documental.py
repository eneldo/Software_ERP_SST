# ============================================================
# ROUTER CONFIGURACIÓN DOCUMENTAL
# FASE 2.2.1B - Configuración Documental y Firmas PRO
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.models.configuracion_documental import ConfiguracionDocumental
from app.schemas.configuracion_documental_schema import (
    ConfiguracionDocumentalCreate,
    ConfiguracionDocumentalUpdate,
    ConfiguracionDocumentalResponse,
)
from app.auth.dependencies import require_roles


router = APIRouter(
    prefix="/configuracion-documental",
    tags=["Configuración Documental y Firmas PRO"],
)


@router.post("/", response_model=ConfiguracionDocumentalResponse)
def crear_configuracion_documental(
    data: ConfiguracionDocumentalCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    existe = (
        db.query(ConfiguracionDocumental)
        .filter(ConfiguracionDocumental.empresa_id == data.empresa_id)
        .first()
    )

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe configuración documental para esta empresa. Use actualizar.",
        )

    configuracion = ConfiguracionDocumental(**data.model_dump())

    db.add(configuracion)
    db.commit()
    db.refresh(configuracion)

    return configuracion


@router.get("/", response_model=list[ConfiguracionDocumentalResponse])
def listar_configuraciones_documentales(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    return (
        db.query(ConfiguracionDocumental)
        .order_by(ConfiguracionDocumental.id.desc())
        .all()
    )


@router.get("/empresa/{empresa_id}", response_model=ConfiguracionDocumentalResponse)
def obtener_configuracion_por_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    configuracion = (
        db.query(ConfiguracionDocumental)
        .filter(ConfiguracionDocumental.empresa_id == empresa_id)
        .first()
    )

    if not configuracion:
        raise HTTPException(
            status_code=404,
            detail="No existe configuración documental para esta empresa",
        )

    return configuracion


@router.put("/empresa/{empresa_id}", response_model=ConfiguracionDocumentalResponse)
def actualizar_configuracion_por_empresa(
    empresa_id: int,
    data: ConfiguracionDocumentalUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    configuracion = (
        db.query(ConfiguracionDocumental)
        .filter(ConfiguracionDocumental.empresa_id == empresa_id)
        .first()
    )

    if not configuracion:
        raise HTTPException(
            status_code=404,
            detail="No existe configuración documental para esta empresa",
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(configuracion, key, value)

    db.commit()
    db.refresh(configuracion)

    return configuracion


@router.post("/empresa/{empresa_id}/crear-o-actualizar", response_model=ConfiguracionDocumentalResponse)
def crear_o_actualizar_configuracion(
    empresa_id: int,
    data: ConfiguracionDocumentalUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    configuracion = (
        db.query(ConfiguracionDocumental)
        .filter(ConfiguracionDocumental.empresa_id == empresa_id)
        .first()
    )

    if not configuracion:
        configuracion = ConfiguracionDocumental(
            empresa_id=empresa_id,
            logo_url=data.logo_url,
            firma_representante_url=data.firma_representante_url,
            firma_sst_url=data.firma_sst_url,
            sello_url=data.sello_url,
            prefijo_documental=data.prefijo_documental or "SGSST",
            version_documental=data.version_documental or "1.0",
            pie_documental=data.pie_documental or "Documento controlado generado desde ERP SST PRO.",
        )

        db.add(configuracion)
        db.commit()
        db.refresh(configuracion)

        return configuracion

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(configuracion, key, value)

    db.commit()
    db.refresh(configuracion)

    return configuracion


@router.delete("/empresa/{empresa_id}")
def eliminar_configuracion_documental(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    configuracion = (
        db.query(ConfiguracionDocumental)
        .filter(ConfiguracionDocumental.empresa_id == empresa_id)
        .first()
    )

    if not configuracion:
        raise HTTPException(
            status_code=404,
            detail="Configuración documental no encontrada",
        )

    db.delete(configuracion)
    db.commit()

    return {"mensaje": "Configuración documental eliminada correctamente"}