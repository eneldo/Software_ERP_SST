# ============================================================
# JWT HANDLER - ERP SST PRO
# Genera y valida tokens JWT empresariales
# ============================================================

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import settings


def create_access_token(data: dict) -> str:
    """
    Crea token JWT con expiración.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


def decode_access_token(token: str):
    """
    Decodifica token JWT.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload

    except JWTError:
        return None