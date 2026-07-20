from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.permiso import Permiso
from app.models.usuario import Usuario
from app.models.usuario_permiso import UsuarioPermiso
from app.schemas.permiso_schema import (
    PermisoCreate,
    PermisoUpdate,
    PermisoResponse,
    AsignarPermisosUsuario,
)
from app.auth.dependencies import require_roles, get_current_user, require_permission
from app.core.default_permissions import PERM_PERMISOS_GESTIONAR, ensure_default_permissions


router = APIRouter(prefix="/permisos", tags=["Permisos dinámicos PRO"])
GESTIONAR_PERMISOS = require_permission(PERM_PERMISOS_GESTIONAR)


@router.post("/", response_model=PermisoResponse)
def crear_permiso(
    data: PermisoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(GESTIONAR_PERMISOS)
):
    ensure_default_permissions(db)
    existe = db.query(Permiso).filter(Permiso.codigo == data.codigo.upper()).first()
    if existe:
        raise HTTPException(status_code=400, detail="El permiso ya existe")

    permiso = Permiso(
        codigo=data.codigo.upper(),
        nombre=data.nombre,
        modulo=data.modulo.upper(),
        descripcion=data.descripcion,
    )

    db.add(permiso)
    db.commit()
    db.refresh(permiso)
    return permiso


@router.get("/", response_model=list[PermisoResponse])
def listar_permisos(
    db: Session = Depends(get_db),
    usuario=Depends(GESTIONAR_PERMISOS)
):
    ensure_default_permissions(db)
    return db.query(Permiso).order_by(Permiso.modulo.asc(), Permiso.codigo.asc()).all()


@router.put("/{permiso_id}", response_model=PermisoResponse)
def actualizar_permiso(
    permiso_id: int,
    data: PermisoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(GESTIONAR_PERMISOS),
):
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")

    payload = data.model_dump(exclude_unset=True)
    if "codigo" in payload and payload["codigo"]:
        codigo = payload["codigo"].strip().upper()
        duplicado = db.query(Permiso).filter(Permiso.codigo == codigo, Permiso.id != permiso_id).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otro permiso con ese código")
        payload["codigo"] = codigo
    if "modulo" in payload and payload["modulo"]:
        payload["modulo"] = payload["modulo"].strip().upper()
    if "nombre" in payload and payload["nombre"]:
        payload["nombre"] = payload["nombre"].strip()

    for key, value in payload.items():
        setattr(permiso, key, value)
    db.commit()
    db.refresh(permiso)
    return permiso


@router.delete("/{permiso_id}")
def eliminar_permiso(
    permiso_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(GESTIONAR_PERMISOS),
):
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    permiso.activo = False
    db.query(UsuarioPermiso).filter(UsuarioPermiso.permiso_id == permiso_id).delete()
    db.commit()
    return {"mensaje": "Permiso desactivado correctamente", "permiso_id": permiso_id}


@router.post("/usuario/asignar")
def asignar_permisos_usuario(
    data: AsignarPermisosUsuario,
    db: Session = Depends(get_db),
    usuario=Depends(GESTIONAR_PERMISOS)
):
    ensure_default_permissions(db)
    usuario_obj = db.query(Usuario).filter(Usuario.id == data.usuario_id).first()
    if not usuario_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.query(UsuarioPermiso).filter(
        UsuarioPermiso.usuario_id == data.usuario_id
    ).delete()

    for permiso_id in data.permisos_ids:
        permiso = db.query(Permiso).filter(Permiso.id == permiso_id, Permiso.activo == True).first()
        if permiso:
            db.add(UsuarioPermiso(usuario_id=data.usuario_id, permiso_id=permiso_id))

    db.commit()

    return {"mensaje": "Permisos asignados correctamente"}


@router.get("/usuario/{usuario_id}")
def permisos_por_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(GESTIONAR_PERMISOS)
):
    usuario_obj = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    permisos = (
        db.query(Permiso)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
        .filter(UsuarioPermiso.usuario_id == usuario_id)
        .all()
    )

    return {
        "usuario_id": usuario_id,
        "permisos": [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "modulo": p.modulo,
            }
            for p in permisos
        ],
    }


@router.get("/mis-permisos")
def mis_permisos(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    permisos = (
        db.query(Permiso)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
        .filter(UsuarioPermiso.usuario_id == usuario.id)
        .all()
    )

    return {
        "usuario": usuario.correo,
        "rol": usuario.rol,
        "permisos": [p.codigo for p in permisos],
    }
