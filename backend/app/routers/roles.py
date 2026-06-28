from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rol import Rol
from app.schemas.rol_schema import RolCreate, RolUpdate, RolResponse
from app.auth.dependencies import require_roles


router = APIRouter(prefix="/roles", tags=["Roles dinámicos PRO"])


@router.post("/", response_model=RolResponse)
def crear_rol(
    data: RolCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN"]))
):
    existe = db.query(Rol).filter(Rol.nombre == data.nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail="El rol ya existe")

    rol = Rol(nombre=data.nombre.upper(), descripcion=data.descripcion)
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


@router.get("/", response_model=list[RolResponse])
def listar_roles(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    return db.query(Rol).order_by(Rol.id.asc()).all()


@router.put("/{rol_id}", response_model=RolResponse)
def actualizar_rol(
    rol_id: int,
    data: RolUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN"]))
):
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    if data.nombre is not None:
        rol.nombre = data.nombre.upper()
    if data.descripcion is not None:
        rol.descripcion = data.descripcion
    if data.activo is not None:
        rol.activo = data.activo

    db.commit()
    db.refresh(rol)
    return rol


@router.delete("/{rol_id}")
def eliminar_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN"]))
):
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    rol.activo = False
    db.commit()

    return {"mensaje": "Rol desactivado correctamente"}