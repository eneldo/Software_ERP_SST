# ============================================================
# ROUTER: USUARIOS DEL SISTEMA PRO
# ERP SST PRO ENTERPRISE
# FASE HARDENING — CRUD completo de usuarios
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.auth.security import hash_password
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario_sistema_schema import (
    ROLES_SISTEMA,
    UsuarioSistemaCreate,
    UsuarioSistemaPasswordUpdate,
    UsuarioSistemaResponse,
    UsuarioSistemaStats,
    UsuarioSistemaUpdate,
)


router = APIRouter(
    prefix="/usuarios-sistema",
    tags=["Usuarios del Sistema PRO"],
)

ROLES_ADMIN_USUARIOS = ["SUPER_ADMIN"]


def obtener_usuario_o_404(db: Session, usuario_id: int) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return usuario




def contar_super_admins_activos(db: Session) -> int:
    return (
        db.query(Usuario)
        .filter(Usuario.rol == "SUPER_ADMIN", Usuario.activo == True)
        .count()
    )


def proteger_ultimo_super_admin(db: Session, usuario: Usuario, nuevo_rol: str | None = None, nuevo_activo: bool | None = None) -> None:
    es_super_admin_actual = str(usuario.rol or "").upper() == "SUPER_ADMIN" and bool(usuario.activo) is True
    if not es_super_admin_actual:
        return

    pierde_rol = nuevo_rol is not None and str(nuevo_rol).upper() != "SUPER_ADMIN"
    se_desactiva = nuevo_activo is not None and nuevo_activo is False

    if (pierde_rol or se_desactiva) and contar_super_admins_activos(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede modificar/desactivar el último SUPER_ADMIN activo del sistema",
        )

def validar_correo_unico(db: Session, correo: str, usuario_id: int | None = None) -> None:
    query = db.query(Usuario).filter(Usuario.correo == correo.strip().lower())
    if usuario_id is not None:
        query = query.filter(Usuario.id != usuario_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este correo electrónico",
        )


@router.get("/roles-disponibles", response_model=list[str])
def roles_disponibles(
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    return ROLES_SISTEMA


@router.get("/stats", response_model=UsuarioSistemaStats)
def estadisticas_usuarios(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    total = db.query(Usuario).count()
    activos = db.query(Usuario).filter(Usuario.activo == True).count()
    super_admins = db.query(Usuario).filter(Usuario.rol == "SUPER_ADMIN").count()

    return UsuarioSistemaStats(
        total=total,
        activos=activos,
        inactivos=max(total - activos, 0),
        super_admins=super_admins,
    )


@router.get("/", response_model=list[UsuarioSistemaResponse])
def listar_usuarios_sistema(
    buscar: str | None = Query(default=None, description="Buscar por nombre, apellido, correo o rol"),
    rol: str | None = Query(default=None, description="Filtrar por rol"),
    activo: bool | None = Query(default=None, description="Filtrar por estado activo/inactivo"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    query = db.query(Usuario)

    if buscar:
        term = f"%{buscar.strip()}%"
        query = query.filter(
            or_(
                Usuario.nombres.ilike(term),
                Usuario.apellidos.ilike(term),
                Usuario.correo.ilike(term),
                Usuario.rol.ilike(term),
            )
        )

    if rol:
        query = query.filter(Usuario.rol == rol.strip().upper())

    if activo is not None:
        query = query.filter(Usuario.activo == activo)

    return (
        query.order_by(Usuario.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{usuario_id}", response_model=UsuarioSistemaResponse)
def obtener_usuario_sistema(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    return obtener_usuario_o_404(db, usuario_id)


@router.post("/", response_model=UsuarioSistemaResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario_sistema(
    data: UsuarioSistemaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    correo = str(data.correo).strip().lower()
    validar_correo_unico(db, correo)

    nuevo_usuario = Usuario(
        nombres=data.nombres.strip(),
        apellidos=data.apellidos.strip(),
        correo=correo,
        password=hash_password(data.password),
        rol=data.rol.strip().upper(),
        empresa_id=data.empresa_id,
        activo=data.activo,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.put("/{usuario_id}", response_model=UsuarioSistemaResponse)
def actualizar_usuario_sistema(
    usuario_id: int,
    data: UsuarioSistemaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    usuario = obtener_usuario_o_404(db, usuario_id)
    update_data = data.model_dump(exclude_unset=True)

    if "correo" in update_data and update_data["correo"]:
        nuevo_correo = str(update_data["correo"]).strip().lower()
        validar_correo_unico(db, nuevo_correo, usuario_id=usuario_id)
        usuario.correo = nuevo_correo

    if "nombres" in update_data and update_data["nombres"] is not None:
        usuario.nombres = update_data["nombres"].strip()

    if "apellidos" in update_data and update_data["apellidos"] is not None:
        usuario.apellidos = update_data["apellidos"].strip()

    nuevo_rol = None
    if "rol" in update_data and update_data["rol"] is not None:
        nuevo_rol = update_data["rol"].strip().upper()
        proteger_ultimo_super_admin(db, usuario, nuevo_rol=nuevo_rol)
        usuario.rol = nuevo_rol

    if "empresa_id" in update_data:
        usuario.empresa_id = update_data["empresa_id"]

    if "activo" in update_data and update_data["activo"] is not None:
        if usuario.id == usuario_actual.id and update_data["activo"] is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puede desactivar su propio usuario",
            )
        proteger_ultimo_super_admin(db, usuario, nuevo_activo=update_data["activo"])
        usuario.activo = update_data["activo"]

    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/password", response_model=UsuarioSistemaResponse)
def cambiar_password_usuario_sistema(
    usuario_id: int,
    data: UsuarioSistemaPasswordUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    usuario = obtener_usuario_o_404(db, usuario_id)
    usuario.password = hash_password(data.password)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/toggle-activo", response_model=UsuarioSistemaResponse)
def cambiar_estado_usuario_sistema(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    usuario = obtener_usuario_o_404(db, usuario_id)

    if usuario.id == usuario_actual.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede activar/desactivar su propio usuario desde esta acción",
        )

    proteger_ultimo_super_admin(db, usuario, nuevo_activo=not bool(usuario.activo))
    usuario.activo = not bool(usuario.activo)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}")
def eliminar_usuario_sistema(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(ROLES_ADMIN_USUARIOS)),
):
    usuario = obtener_usuario_o_404(db, usuario_id)

    if usuario.id == usuario_actual.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede eliminar/desactivar su propio usuario",
        )

    proteger_ultimo_super_admin(db, usuario, nuevo_activo=False)

    # Eliminación lógica para no perder trazabilidad de auditoría.
    usuario.activo = False
    db.commit()

    return {
        "ok": True,
        "mensaje": "Usuario desactivado correctamente",
        "usuario_id": usuario_id,
    }
