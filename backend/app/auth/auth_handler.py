# ============================================================
# JWT HANDLER - ERP SST PRO
# Genera y valida tokens JWT empresariales
# H-013a: jti claim para blocklist
# ============================================================

import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import settings


def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid.uuid4())
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "token_type": token_type,
        "jti": jti,
    })
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_access_token(data: dict) -> str:
    return _create_token(
        data,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(data: dict) -> str:
    return _create_token(
        data,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload

    except JWTError:
        return None


def extract_jti(token: str) -> str | None:
    payload = decode_access_token(token)
    if payload:
        return payload.get("jti")
    return None
