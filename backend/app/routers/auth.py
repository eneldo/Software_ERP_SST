from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.login_intento import LoginIntento
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from app.auth.security import hash_password, verify_password
from app.auth.auth_handler import create_access_token
from app.auth.dependencies import get_current_user, require_roles


router = APIRouter(prefix="/auth", tags=["Autenticación JWT PRO"])


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


@router.post("/crear-usuario", response_model=UsuarioResponse)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    existe = db.query(Usuario).filter(Usuario.correo == data.correo).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este correo",
        )

    nuevo_usuario = Usuario(
        nombres=data.nombres,
        apellidos=data.apellidos,
        correo=data.correo,
        password=hash_password(data.password),
        rol=data.rol,
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

    registrar_intento_login(db, correo, ip, True, "Login exitoso")

    token = create_access_token(
        data={
            "user_id": usuario.id,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "empresa_id": usuario.empresa_id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "empresa_id": usuario.empresa_id,
        },
    }


@router.post("/login-json", response_model=TokenResponse)
def login_json(
    data: LoginRequest,
    request: Request,
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

    registrar_intento_login(db, correo, ip, True, "Login exitoso")

    token = create_access_token(
        data={
            "user_id": usuario.id,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "empresa_id": usuario.empresa_id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "empresa_id": usuario.empresa_id,
        },
    }


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