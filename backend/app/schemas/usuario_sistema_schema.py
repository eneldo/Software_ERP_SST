# ============================================================
# SCHEMAS: USUARIOS DEL SISTEMA PRO
# ERP SST PRO ENTERPRISE
# FASE HARDENING — Usuarios del Sistema PRO
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


ROLES_SISTEMA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "COORDINADOR_SST",
    "RESPONSABLE_SST",
    "TECNICO_SST",
    "AUDITOR",
    "EMPLEADO",
    "SOLO_LECTURA",
]


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
