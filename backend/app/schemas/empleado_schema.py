# ============================================================
# SCHEMAS EMPLEADOS - ERP SST PRO
# FASE 1.1.5.3 — EXPORTACIÓN PDF / EXCEL
# Archivo: backend/app/schemas/empleado_schema.py
# ============================================================

from typing import Optional
from datetime import date
from pydantic import ConfigDict,  BaseModel, EmailStr


class EmpleadoCreate(BaseModel):
    nombres: str
    apellidos: str
    tipo_documento: str = "CC"
    documento: str
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    tipo_contrato: Optional[str] = None
    estado_laboral: str = "ACTIVO"
    empresa_id: int
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None
    genero: Optional[str] = None
    grupo_etnico: Optional[str] = None
    discapacidad: Optional[str] = None
    rango_edad: Optional[str] = None
    nivel_escolaridad: Optional[str] = None
    estado_civil: Optional[str] = None
    tipo_sangre: Optional[str] = None


class EmpleadoUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    tipo_documento: Optional[str] = None
    documento: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    tipo_contrato: Optional[str] = None
    estado_laboral: Optional[str] = None
    empresa_id: Optional[int] = None
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None
    activo: Optional[bool] = None
    genero: Optional[str] = None
    grupo_etnico: Optional[str] = None
    discapacidad: Optional[str] = None
    rango_edad: Optional[str] = None
    nivel_escolaridad: Optional[str] = None
    estado_civil: Optional[str] = None
    tipo_sangre: Optional[str] = None


class EmpleadoResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    tipo_documento: str
    documento: str
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    tipo_contrato: Optional[str] = None
    estado_laboral: str
    empresa_id: int
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None
    genero: Optional[str] = None
    grupo_etnico: Optional[str] = None
    discapacidad: Optional[str] = None
    rango_edad: Optional[str] = None
    nivel_escolaridad: Optional[str] = None
    estado_civil: Optional[str] = None
    tipo_sangre: Optional[str] = None
    activo: bool

    # Campos calculados para que el frontend no dependa de hacer cruces manuales.
    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
