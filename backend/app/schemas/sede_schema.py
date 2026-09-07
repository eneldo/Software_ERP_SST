# ============================================================
# SCHEMAS SEDE - ERP SST PRO
# FASE 1.1.2.1 — SEDES SST ENTERPRISE 360°
# ============================================================

from typing import Optional
from datetime import datetime

from pydantic import ConfigDict,  BaseModel, EmailStr, Field


# ============================================================
# BASE
# ============================================================

class SedeBase(BaseModel):
    empresa_id: int

    nombre: str = Field(..., min_length=2, max_length=255)
    codigo_sede: Optional[str] = Field(default=None, max_length=50)
    tipo_sede: Optional[str] = Field(default="PRINCIPAL", max_length=50)

    direccion: Optional[str] = Field(default=None, max_length=255)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    departamento: Optional[str] = Field(default=None, max_length=100)

    telefono: Optional[str] = Field(default=None, max_length=50)
    correo: Optional[EmailStr] = None

    responsable_sede: Optional[str] = Field(default=None, max_length=255)
    cargo_responsable: Optional[str] = Field(default=None, max_length=255)

    numero_empleados: int = Field(default=0, ge=0)


# ============================================================
# CREATE
# ============================================================

class SedeCreate(SedeBase):
    pass


# ============================================================
# UPDATE
# ============================================================

class SedeUpdate(BaseModel):
    empresa_id: Optional[int] = None

    nombre: Optional[str] = Field(default=None, min_length=2, max_length=255)
    codigo_sede: Optional[str] = Field(default=None, max_length=50)
    tipo_sede: Optional[str] = Field(default=None, max_length=50)

    direccion: Optional[str] = Field(default=None, max_length=255)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    departamento: Optional[str] = Field(default=None, max_length=100)

    telefono: Optional[str] = Field(default=None, max_length=50)
    correo: Optional[EmailStr] = None

    responsable_sede: Optional[str] = Field(default=None, max_length=255)
    cargo_responsable: Optional[str] = Field(default=None, max_length=255)

    numero_empleados: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = None


# ============================================================
# RESPONSE SIMPLE
# ============================================================

class SedeResponse(BaseModel):
    id: int
    empresa_id: int

    nombre: str
    codigo_sede: Optional[str] = None
    tipo_sede: Optional[str] = None

    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None

    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None

    responsable_sede: Optional[str] = None
    cargo_responsable: Optional[str] = None

    numero_empleados: int
    activo: bool

    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# RESPONSE ENTERPRISE CON NOMBRE EMPRESA
# ============================================================

class SedeEnterpriseResponse(SedeResponse):
    empresa_nombre: Optional[str] = None
    empresa_nit: Optional[str] = None