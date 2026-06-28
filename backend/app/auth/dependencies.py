from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.permiso import Permiso
from app.models.usuario_permiso import UsuarioPermiso
from app.auth.auth_handler import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
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
        if usuario.rol not in roles_permitidos:
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

        if not permiso:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene el permiso requerido: {codigo_permiso}",
            )

        return usuario

    return permission_checker