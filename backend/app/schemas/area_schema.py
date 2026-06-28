# ============================================================
# SCHEMAS ÁREA - ERP SST PRO
# FASE 1.1.3 — ÁREAS SST ENTERPRISE 360°
# ============================================================

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AreaBase(BaseModel):
    empresa_id: int
    sede_id: Optional[int] = None

    nombre: str = Field(..., min_length=2, max_length=150)
    codigo_area: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=500)

    tipo_area: Optional[str] = Field(default="OPERATIVA", max_length=50)
    nivel_riesgo: Optional[str] = Field(default="MEDIO", max_length=30)
    proceso_asociado: Optional[str] = Field(default=None, max_length=150)

    responsable_area: Optional[str] = Field(default=None, max_length=255)
    cargo_responsable: Optional[str] = Field(default=None, max_length=255)
    correo_responsable: Optional[EmailStr] = None
    telefono_responsable: Optional[str] = Field(default=None, max_length=50)

    numero_empleados: int = Field(default=0, ge=0)


class AreaCreate(AreaBase):
    pass


class AreaUpdate(BaseModel):
    empresa_id: Optional[int] = None
    sede_id: Optional[int] = None

    nombre: Optional[str] = Field(default=None, min_length=2, max_length=150)
    codigo_area: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=500)

    tipo_area: Optional[str] = Field(default=None, max_length=50)
    nivel_riesgo: Optional[str] = Field(default=None, max_length=30)
    proceso_asociado: Optional[str] = Field(default=None, max_length=150)

    responsable_area: Optional[str] = Field(default=None, max_length=255)
    cargo_responsable: Optional[str] = Field(default=None, max_length=255)
    correo_responsable: Optional[EmailStr] = None
    telefono_responsable: Optional[str] = Field(default=None, max_length=50)

    numero_empleados: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = None


class AreaResponse(BaseModel):
    id: int
    empresa_id: int
    sede_id: Optional[int] = None

    nombre: str
    codigo_area: Optional[str] = None
    descripcion: Optional[str] = None

    tipo_area: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    proceso_asociado: Optional[str] = None

    responsable_area: Optional[str] = None
    cargo_responsable: Optional[str] = None
    correo_responsable: Optional[EmailStr] = None
    telefono_responsable: Optional[str] = None

    numero_empleados: int
    activo: bool

    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class AreaEnterpriseResponse(AreaResponse):
    empresa_nombre: Optional[str] = None
    empresa_nit: Optional[str] = None
    sede_nombre: Optional[str] = None
    sede_codigo: Optional[str] = None
    sede_ciudad: Optional[str] = None
