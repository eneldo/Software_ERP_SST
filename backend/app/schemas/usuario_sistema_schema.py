# ============================================================
# SCHEMAS: USUARIOS DEL SISTEMA PRO
# ERP SST PRO ENTERPRISE
# FASE HARDENING — Usuarios del Sistema PRO
# ============================================================

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.roles import ROLES_SISTEMA


def _validar_password_fuerte(value: str) -> str:
    if len(value) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", value):
        raise ValueError("La contraseña debe contener al menos una mayúscula.")
    if not re.search(r"[a-z]", value):
        raise ValueError("La contraseña debe contener al menos una minúscula.")
    if not re.search(r"\d", value):
        raise ValueError("La contraseña debe contener al menos un número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", value):
        raise ValueError("La contraseña debe contener al menos un carácter especial.")
    return value


class UsuarioSistemaBase(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=255)
    apellidos: str = Field(..., min_length=2, max_length=255)
    correo: EmailStr
    rol: str = Field(default="ADMIN_EMPRESA", max_length=50)
    empresa_id: Optional[int] = None
    activo: bool = True

    @field_validator("nombres", "apellidos", "rol")
    @classmethod
    def limpiar_texto(cls, value: str) -> str:
        return value.strip()

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, value: str) -> str:
        rol = value.strip().upper()
        if rol not in ROLES_SISTEMA:
            raise ValueError(f"Rol no permitido. Roles válidos: {', '.join(ROLES_SISTEMA)}")
        return rol


class UsuarioSistemaCreate(UsuarioSistemaBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        return _validar_password_fuerte(value)


class UsuarioSistemaUpdate(BaseModel):
    nombres: Optional[str] = Field(default=None, min_length=2, max_length=255)
    apellidos: Optional[str] = Field(default=None, min_length=2, max_length=255)
    correo: Optional[EmailStr] = None
    rol: Optional[str] = Field(default=None, max_length=50)
    empresa_id: Optional[int] = None
    activo: Optional[bool] = None

    @field_validator("nombres", "apellidos", "rol")
    @classmethod
    def limpiar_texto(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if isinstance(value, str) else value

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        rol = value.strip().upper()
        if rol not in ROLES_SISTEMA:
            raise ValueError(f"Rol no permitido. Roles válidos: {', '.join(ROLES_SISTEMA)}")
        return rol


class UsuarioSistemaPasswordUpdate(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        return _validar_password_fuerte(value)


class UsuarioSistemaResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: EmailStr
    rol: str
    activo: bool
    empresa_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioSistemaStats(BaseModel):
    total: int
    activos: int
    inactivos: int
    super_admins: int
