from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.models.login_intento import LoginIntento
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from app.auth.security import hash_password, verify_password
from app.auth.auth_handler import create_access_token, create_refresh_token, decode_access_token
from app.auth.dependencies import get_current_user, require_roles
from app.config import settings


router = APIRouter(prefix="/auth", tags=["Autenticación JWT PRO"])


def _usuario_payload(usuario: Usuario) -> dict:
    return {
        "user_id": usuario.id,
        "correo": usuario.correo,
        "rol": usuario.rol,
        "empresa_id": usuario.empresa_id,
    }


def _usuario_response(usuario: Usuario) -> dict:
    return {
        "id": usuario.id,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "rol": usuario.rol,
        "empresa_id": usuario.empresa_id,
    }


def _set_refresh_cookie(response: Response, usuario: Usuario) -> None:
    refresh_token = create_refresh_token(_usuario_payload(usuario))
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=settings.REFRESH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        httponly=True,
    )


def registrar_intento_login(
    db: Session,
    correo: str,
    ip: str | None,
    exitoso: bool,
    motivo: str | None = None,
):
    intento = LoginIntento(
        correo=correo,
        ip=ip,
        exitoso=exitoso,
        motivo=motivo,
    )
    db.add(intento)
    db.commit()


def registrar_auditoria_login(db: Session, usuario: Usuario, request: Request) -> None:
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    db.add(
        Auditoria(
            usuario_id=usuario.id,
            empresa_id=usuario.empresa_id,
            metodo="POST",
            ruta=str(request.url.path),
            accion="LOGIN",
            ip=ip,
            user_agent=user_agent,
            status_code=200,
        )
    )


def validar_bloqueo_login(db: Session, correo: str, ip: str | None):
    limite_tiempo = datetime.utcnow() - timedelta(minutes=15)

    fallidos = (
        db.query(LoginIntento)
        .filter(
            LoginIntento.correo == correo,
            LoginIntento.exitoso == False,
            LoginIntento.fecha_creacion >= limite_tiempo,
        )
        .count()
    )

    if fallidos >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intente nuevamente en 15 minutos.",
        )


@router.post(
    "/crear-usuario",
    response_model=UsuarioResponse,
    deprecated=True,
    summary="Crear usuario protegido - usar /usuarios-sistema/ como ruta oficial",
)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles(["SUPER_ADMIN"])),
):
    correo = str(data.correo).strip().lower()
    existe = db.query(Usuario).filter(Usuario.correo == correo).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este correo",
        )

    nuevo_usuario = Usuario(
        nombres=data.nombres.strip(),
        apellidos=data.apellidos.strip(),
        correo=correo,
        password=hash_password(data.password),
        rol=str(data.rol).strip().upper(),
        empresa_id=data.empresa_id,
        activo=True,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.post("/login", response_model=TokenResponse)
def login_swagger(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    correo = form_data.username
    password = form_data.password
    ip = request.client.host if request.client else None

    validar_bloqueo_login(db, correo, ip)

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()

    if not usuario or not verify_password(password, usuario.password):
        registrar_intento_login(db, correo, ip, False, "Credenciales incorrectas")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not usuario.activo:
        registrar_intento_login(db, correo, ip, False, "Usuario inactivo")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    usuario.ultimo_acceso = datetime.now(timezone.utc)
    registrar_intento_login(db, correo, ip, True, "Login exitoso")
    registrar_auditoria_login(db, usuario, request)
    db.commit()
    db.refresh(usuario)

    token = create_access_token(data=_usuario_payload(usuario))
    _set_refresh_cookie(response, usuario)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": _usuario_response(usuario),
    }


@router.post("/login-json", response_model=TokenResponse)
def login_json(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    correo = data.correo
    password = data.password
    ip = request.client.host if request.client else None

    validar_bloqueo_login(db, correo, ip)

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()

    if not usuario or not verify_password(password, usuario.password):
        registrar_intento_login(db, correo, ip, False, "Credenciales incorrectas")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not usuario.activo:
        registrar_intento_login(db, correo, ip, False, "Usuario inactivo")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    usuario.ultimo_acceso = datetime.now(timezone.utc)
    registrar_intento_login(db, correo, ip, True, "Login exitoso")
    registrar_auditoria_login(db, usuario, request)
    db.commit()
    db.refresh(usuario)

    token = create_access_token(data=_usuario_payload(usuario))
    _set_refresh_cookie(response, usuario)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": _usuario_response(usuario),
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion no renovable")

    payload = decode_access_token(refresh_token)
    if not payload or payload.get("token_type") != "refresh":
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")

    usuario = db.query(Usuario).filter(Usuario.id == payload.get("user_id")).first()
    if not usuario or not usuario.activo:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no disponible")

    token = create_access_token(data=_usuario_payload(usuario))
    _set_refresh_cookie(response, usuario)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": _usuario_response(usuario),
    }


@router.post("/logout")
def logout(response: Response):
    _clear_refresh_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=UsuarioResponse)
def perfil_actual(usuario_actual: Usuario = Depends(get_current_user)):
    return usuario_actual


@router.get("/admin-test")
def ruta_admin_test(
    usuario_actual: Usuario = Depends(
        require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])
    )
):
    return {
        "mensaje": "Acceso autorizado a ruta administrativa SST",
        "usuario": usuario_actual.correo,
        "rol": usuario_actual.rol,
    }
