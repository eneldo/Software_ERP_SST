# ============================================================
# ROUTER EMPRESAS PRO
# Incluye clasificación automática SST + logo corporativo
# ============================================================

from pathlib import Path
from uuid import uuid4
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa_schema import EmpresaCreate, EmpresaUpdate, EmpresaResponse
from app.auth.dependencies import require_roles
from app.core.file_security import validate_upload
from app.services.estandares_sst import calcular_estandares_sst
from app.services.relation_guard import execute_smart_delete


router = APIRouter(
    prefix="/empresas",
    tags=["Empresas PRO"],
)

# Carpeta base para uploads
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
LOGOS_DIR = UPLOAD_DIR / "logos"
LOGOS_DIR.mkdir(parents=True, exist_ok=True)


def aplicar_clasificacion_estandares(empresa: Empresa) -> Empresa:
    clasificacion = calcular_estandares_sst(
        numero_trabajadores=empresa.numero_trabajadores,
        clase_riesgo=empresa.clase_riesgo,
        tipo_empresa=empresa.tipo_empresa,
    )

    empresa.tipo_estandares_sst = clasificacion["tipo_estandares_sst"]
    empresa.total_estandares_sst = clasificacion["total_estandares_sst"]
    empresa.descripcion_estandares_sst = clasificacion["descripcion_estandares_sst"]

    return empresa


def validar_acceso_empresa(usuario, empresa_id: int) -> None:
    if getattr(usuario, "rol", None) == "SUPER_ADMIN":
        return

    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id and int(usuario_empresa_id) == int(empresa_id):
        return

    raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")


@router.post("/", response_model=EmpresaResponse)
def crear_empresa(
    data: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    existe = db.query(Empresa).filter(Empresa.nit == data.nit).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una empresa con este NIT",
        )

    empresa = Empresa(**data.model_dump())
    aplicar_clasificacion_estandares(empresa)

    db.add(empresa)
    db.commit()
    db.refresh(empresa)

    return empresa


@router.get("/", response_model=list[EmpresaResponse])
def listar_empresas(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    query = db.query(Empresa).filter(Empresa.estado == True)
    if getattr(usuario, "rol", None) != "SUPER_ADMIN" and getattr(usuario, "empresa_id", None):
        query = query.filter(Empresa.id == usuario.empresa_id)
    return query.order_by(Empresa.id.desc()).all()


@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obtener_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    validar_acceso_empresa(usuario, empresa.id)

    return empresa


@router.put("/{empresa_id}", response_model=EmpresaResponse)
def actualizar_empresa(
    empresa_id: int,
    data: EmpresaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    validar_acceso_empresa(usuario, empresa.id)

    update_data = data.model_dump(exclude_unset=True)

    if "nit" in update_data:
        existe = (
            db.query(Empresa)
            .filter(
                Empresa.nit == update_data["nit"],
                Empresa.id != empresa_id,
            )
            .first()
        )

        if existe:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otra empresa con este NIT",
            )

    for key, value in update_data.items():
        setattr(empresa, key, value)

    aplicar_clasificacion_estandares(empresa)

    db.commit()
    db.refresh(empresa)

    return empresa


@router.post("/{empresa_id}/logo", response_model=EmpresaResponse)
def subir_logo_empresa(
    empresa_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    validar_acceso_empresa(usuario, empresa.id)

    validation = validate_upload(file, allowed_extensions={".png", ".jpg", ".jpeg", ".webp"})
    extension = validation.extension

    nombre_archivo = f"empresa_{empresa_id}_{uuid4().hex}{extension}"
    ruta_fisica = LOGOS_DIR / nombre_archivo

    ruta_fisica.write_bytes(validation.content)

    empresa.logo = f"/uploads/logos/{nombre_archivo}"

    db.commit()
    db.refresh(empresa)

    return empresa


@router.delete("/{empresa_id}/logo", response_model=EmpresaResponse)
def eliminar_logo_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    validar_acceso_empresa(usuario, empresa.id)

    empresa.logo = None

    db.commit()
    db.refresh(empresa)

    return empresa


@router.delete("/{empresa_id}")
def eliminar_empresa(
    empresa_id: int,
    modo: str = Query(
        default="AUTO",
        description="AUTO elimina si no tiene dependencias; si tiene dependencias inactiva. Use DELETE o INACTIVATE para forzar política.",
    ),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN"])),
):
    """
    Eliminación inteligente de empresas.

    Política Enterprise:
    - Si la empresa no tiene dependencias bloqueantes: eliminación física segura.
    - Si tiene sedes, usuarios, empleados, matrices, inspecciones u otros registros SST: inactivación.
    - La validación detallada está disponible en /integridad/eliminacion/empresa/{empresa_id}.
    """
    resultado = execute_smart_delete(
        db,
        entity="empresa",
        record_id=empresa_id,
        mode=modo,
        confirmed=True,
    )

    if resultado.get("action") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=resultado.get("message", "Empresa no encontrada"))

    if not resultado.get("success"):
        raise HTTPException(status_code=400, detail=resultado)

    return resultado
