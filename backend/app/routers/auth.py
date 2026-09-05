# ============================================================
# ROUTER AUTH - ERP SST PRO
# H-013a: Logout con blocklist
# H-013b: MFA TOTP
# ============================================================

import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.models.login_intento import LoginIntento
from app.models.token_blocklist import TokenBlocklist
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from app.auth.security import hash_password, verify_password
from app.auth.auth_handler import (
    create_access_token, create_refresh_token, decode_access_token, extract_jti,
)
from app.auth.dependencies import get_current_user, require_roles
from app.config import settings


router = APIRouter(prefix="/auth", tags=["Autenticación JWT PRO"])


class MFASetupResponse(BaseModel):
    secret: str
    qr_code_base64: str
    provisioning_uri: str


class MFAVerifyRequest(BaseModel):
    code: str


class MFALoginRequest(BaseModel):
    correo: str
    password: str
    mfa_code: str


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
        "mfa_enabled": getattr(usuario, "mfa_enabled", False),
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


def _set_access_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.ACCESS_COOKIE_SECURE,
        samesite=settings.ACCESS_COOKIE_SAMESITE,
        path=settings.ACCESS_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        httponly=True,
    )


def _clear_access_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        path=settings.ACCESS_COOKIE_PATH,
        secure=settings.ACCESS_COOKIE_SECURE,
        samesite=settings.ACCESS_COOKIE_SAMESITE,
        httponly=True,
    )


def _revocar_token(db: Session, token: str, motivo: str, usuario_id: int | None = None) -> None:
    payload = decode_access_token(token)
    if not payload:
        return

    jti = payload.get("jti")
    if not jti:
        return

    exp_ts = payload.get("exp")
    exp_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc) if exp_ts else datetime.now(timezone.utc) + timedelta(hours=1)

    bloqueado = TokenBlocklist(
        jti=jti,
        token_type=payload.get("token_type", "access"),
        usuario_id=usuario_id or payload.get("user_id"),
        empresa_id=payload.get("empresa_id"),
        motivo=motivo,
        bloqueado_por=usuario_id,
        exp=exp_dt,
    )
    db.add(bloqueado)
    db.commit()


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

    if getattr(usuario, "mfa_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="MFA habilitado. Use /auth/login-mfa con código TOTP.",
        )

    usuario.ultimo_acceso = datetime.now(timezone.utc)
    registrar_intento_login(db, correo, ip, True, "Login exitoso")
    registrar_auditoria_login(db, usuario, request)
    db.commit()
    db.refresh(usuario)

    token = create_access_token(data=_usuario_payload(usuario))
    _set_refresh_cookie(response, usuario)
    _set_access_cookie(response, token)

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

    if getattr(usuario, "mfa_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="MFA habilitado. Use /auth/login-mfa con código TOTP.",
        )

    usuario.ultimo_acceso = datetime.now(timezone.utc)
    registrar_intento_login(db, correo, ip, True, "Login exitoso")
    registrar_auditoria_login(db, usuario, request)
    db.commit()
    db.refresh(usuario)

    token = create_access_token(data=_usuario_payload(usuario))
    _set_refresh_cookie(response, usuario)
    _set_access_cookie(response, token)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": _usuario_response(usuario),
    }


@router.post("/login-mfa", response_model=TokenResponse)
def login_mfa(
    data: MFALoginRequest,
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

    mfa_secret = getattr(usuario, "mfa_secret", None)
    if not mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA no configurado para este usuario",
        )

    totp = pyotp.TOTP(mfa_secret)
    if not totp.verify(data.mfa_code, valid_window=1):
        registrar_intento_login(db, correo, ip, False, "Código MFA inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código MFA inválido o expirado",
        )

    usuario.ultimo_acceso = datetime.now(timezone.utc)
    registrar_intento_login(db, correo, ip, True, "Login MFA exitoso")
    registrar_auditoria_login(db, usuario, request)
    db.commit()
    db.refresh(usuario)

    token = create_access_token(data=_usuario_payload(usuario))
    _set_refresh_cookie(response, usuario)
    _set_access_cookie(response, token)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": _usuario_response(usuario),
    }


@router.post("/mfa/setup", response_model=MFASetupResponse)
def mfa_setup(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=usuario.correo,
        issuer_name="ERP-SST-PRO",
    )

    qr = qrcode.make(provisioning_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    usuario.mfa_secret = secret
    db.commit()

    return MFASetupResponse(
        secret=secret,
        qr_code_base64=f"data:image/png;base64,{qr_base64}",
        provisioning_uri=provisioning_uri,
    )


@router.post("/mfa/verify")
def mfa_verify(
    data: MFAVerifyRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    mfa_secret = getattr(usuario, "mfa_secret", None)
    if not mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primero ejecute /auth/mfa/setup",
        )

    totp = pyotp.TOTP(mfa_secret)
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código MFA inválido",
        )

    usuario.mfa_enabled = True
    db.commit()

    return {"mensaje": "MFA habilitado correctamente"}


@router.post("/mfa/disable")
def mfa_disable(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    usuario.mfa_enabled = False
    usuario.mfa_secret = None
    db.commit()

    return {"mensaje": "MFA deshabilitado correctamente"}


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

    jti = payload.get("jti")
    if jti:
        from app.models.token_blocklist import TokenBlocklist
        bloqueado = db.query(TokenBlocklist).filter(
            TokenBlocklist.jti == jti,
            TokenBlocklist.token_type == "refresh",
        ).first()
        if bloqueado:
            _clear_refresh_cookie(response)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revocado")

    usuario = db.query(Usuario).filter(Usuario.id == payload.get("user_id")).first()
    if not usuario or not usuario.activo:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no disponible")

    token = create_access_token(data=_usuario_payload(usuario))
    _set_refresh_cookie(response, usuario)
    _set_access_cookie(response, token)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": _usuario_response(usuario),
    }


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    access_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)

    if access_token:
        _revocar_token(db, access_token, "LOGOUT", usuario.id)
    if refresh_token:
        _revocar_token(db, refresh_token, "LOGOUT", usuario.id)

    _clear_refresh_cookie(response)
    _clear_access_cookie(response)

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
