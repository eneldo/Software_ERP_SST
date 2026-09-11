# ============================================================
# SCHEMAS USUARIO - ERP SST PRO
# ============================================================

import re
from typing import Optional
from pydantic import ConfigDict, BaseModel, EmailStr, field_validator


_PASSWORD_MIN_LENGTH = 8


def _validate_password_strength(value: str) -> str:
    if len(value) < _PASSWORD_MIN_LENGTH:
        raise ValueError(f"La contrasena debe tener al menos {_PASSWORD_MIN_LENGTH} caracteres.")
    if not re.search(r"[A-Z]", value):
        raise ValueError("La contrasena debe contener al menos una letra mayuscula.")
    if not re.search(r"[a-z]", value):
        raise ValueError("La contrasena debe contener al menos una letra minuscula.")
    if not re.search(r"\d", value):
        raise ValueError("La contrasena debe contener al menos un numero.")
    return value


class UsuarioCreate(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr
    password: str
    rol: str = "ADMIN_EMPRESA"
    empresa_id: Optional[int] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class UsuarioResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: EmailStr
    rol: str
    activo: bool
    empresa_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
