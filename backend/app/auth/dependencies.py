from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.permiso import Permiso
from app.models.usuario_permiso import UsuarioPermiso
from app.auth.auth_handler import decode_access_token
from app.config import settings
from app.core.roles import COORDINADOR_SST, RESPONSABLE_SST, normalizar_rol


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _extract_token(request: Request, token: str | None) -> str | None:
    if token:
        return token
    return request.cookies.get(settings.ACCESS_COOKIE_NAME)


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    resolved_token = _extract_token(request, token)

    if not resolved_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(resolved_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("token_type", "access") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no valido para autenticacion",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin información de usuario",
        )

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return usuario


def require_roles(roles_permitidos: list):
    def role_checker(usuario: Usuario = Depends(get_current_user)):
        rol_usuario = normalizar_rol(usuario.rol)
        roles_normalizados = {normalizar_rol(rol) for rol in roles_permitidos}
        roles_heredados = {
            COORDINADOR_SST: {RESPONSABLE_SST},
        }
        autorizado = rol_usuario in roles_normalizados or bool(
            roles_heredados.get(rol_usuario, set()) & roles_normalizados
        )

        if not autorizado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para esta acción",
            )
        return usuario

    return role_checker


def require_permission(codigo_permiso: str):
    def permission_checker(
        usuario: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if usuario.rol == "SUPER_ADMIN":
            return usuario

        if not user_has_permission(db, usuario, codigo_permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene el permiso requerido: {codigo_permiso}",
            )

        return usuario

    return permission_checker


def user_has_permission(db: Session, usuario: Usuario, codigo_permiso: str) -> bool:
    if usuario.rol == "SUPER_ADMIN":
        return True

    permiso = (
        db.query(Permiso)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
        .filter(
            UsuarioPermiso.usuario_id == usuario.id,
            Permiso.codigo == codigo_permiso.upper(),
            Permiso.activo == True,
        )
        .first()
    )

    return permiso is not None
