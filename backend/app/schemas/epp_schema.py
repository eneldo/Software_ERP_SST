# ============================================================
# SCHEMAS EPP SST ENTERPRISE - ERP SST PRO
# FASE 1.1.7.1 — EPP SST BASE
# Archivo: backend/app/schemas/epp_schema.py
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


ESTADOS_CATALOGO = {"ACTIVO", "INACTIVO"}
ESTADOS_ENTREGA = {
    "ENTREGADO",
    "VIGENTE",
    "PROXIMO_REPOSICION",
    "VENCIDO",
    "REEMPLAZADO",
    "DEVUELTO",
    "ANULADO",
}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class EPPCatalogoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int = Field(..., gt=0)
    codigo: str = Field(..., min_length=2, max_length=50)
    nombre: str = Field(..., min_length=2, max_length=255)
    categoria: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = None
    vida_util_dias: Optional[int] = Field(default=365, ge=0)
    requiere_reposicion: bool = True
    requiere_firma: bool = True
    requiere_evidencia: bool = False
    estado: str = "ACTIVO"
    activo: bool = True

    @field_validator("codigo")
    @classmethod
    def codigo_upper(cls, value):
        return str(value).strip().upper()

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "ACTIVO")
        if value not in ESTADOS_CATALOGO:
            raise ValueError("Estado de EPP no válido")
        return value


class EPPCatalogoCreate(EPPCatalogoBase):
    pass


class EPPCatalogoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = Field(default=None, gt=0)
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=50)
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=255)
    categoria: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = None
    vida_util_dias: Optional[int] = Field(default=None, ge=0)
    requiere_reposicion: Optional[bool] = None
    requiere_firma: Optional[bool] = None
    requiere_evidencia: Optional[bool] = None
    estado: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("codigo")
    @classmethod
    def codigo_upper(cls, value):
        return str(value).strip().upper() if value is not None else value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        if value is None:
            return value
        value = _upper_clean(value, "ACTIVO")
        if value not in ESTADOS_CATALOGO:
            raise ValueError("Estado de EPP no válido")
        return value


class EPPCatalogoResponse(EPPCatalogoBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    empresa_nombre: Optional[str] = None
    ficha_tecnica_url: Optional[str] = None
    ficha_tecnica_nombre: Optional[str] = None
    ficha_tecnica_archivo_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class EPPEntregaBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int = Field(..., gt=0)
    empleado_id: int = Field(..., gt=0)
    epp_id: int = Field(..., gt=0)
    cantidad: int = Field(default=1, gt=0)
    fecha_entrega: date
    fecha_reposicion: Optional[date] = None
    talla: Optional[str] = Field(default=None, max_length=50)
    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)
    serial: Optional[str] = Field(default=None, max_length=100)
    estado: str = "ENTREGADO"
    recibido_por_empleado: bool = False
    observaciones: Optional[str] = None
    activo: bool = True

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "ENTREGADO")
        if value not in ESTADOS_ENTREGA:
            raise ValueError("Estado de entrega EPP no válido")
        return value


class EPPEntregaCreate(EPPEntregaBase):
    pass


class EPPEntregaUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    epp_id: Optional[int] = Field(default=None, gt=0)
    cantidad: Optional[int] = Field(default=None, gt=0)
    fecha_entrega: Optional[date] = None
    fecha_reposicion: Optional[date] = None
    talla: Optional[str] = Field(default=None, max_length=50)
    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)
    serial: Optional[str] = Field(default=None, max_length=100)
    estado: Optional[str] = None
    recibido_por_empleado: Optional[bool] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        if value is None:
            return value
        value = _upper_clean(value, "ENTREGADO")
        if value not in ESTADOS_ENTREGA:
            raise ValueError("Estado de entrega EPP no válido")
        return value


class EPPEntregaResponse(EPPEntregaBase):
    id: int
    fecha_firma: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    empresa_nombre: Optional[str] = None
    empleado_documento: Optional[str] = None
    empleado_nombre: Optional[str] = None
    empleado_correo: Optional[str] = None
    sede_id: Optional[int] = None
    sede_nombre: Optional[str] = None
    area_id: Optional[int] = None
    area_nombre: Optional[str] = None
    cargo_id: Optional[int] = None
    cargo_nombre: Optional[str] = None
    epp_codigo: Optional[str] = None
    epp_nombre: Optional[str] = None
    epp_categoria: Optional[str] = None
    vida_util_dias: Optional[int] = None
    dias_reposicion: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class EPPEntregaItemLote(BaseModel):
    model_config = ConfigDict(extra="ignore")

    epp_id: int = Field(..., gt=0)
    cantidad: int = Field(default=1, gt=0)
    talla: Optional[str] = Field(default=None, max_length=50)
    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)
    serial: Optional[str] = Field(default=None, max_length=100)
    observaciones: Optional[str] = None


class EPPEntregaLoteCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int = Field(..., gt=0)
    empleado_id: int = Field(..., gt=0)
    fecha_entrega: date
    items: list[EPPEntregaItemLote] = Field(..., min_length=1)


class EPPEntregaLoteResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entregas_creadas: int
    empleado_nombre: str
    fecha_entrega: date
    detalles: list[EPPEntregaResponse]


class EPPConsolidadoEmpleado(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    empleado_id: int
    empleado_documento: Optional[str] = None
    empleado_nombre: str
    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    total_epp: int
    epp_entregados: list[dict]


class EPPDashboardResponse(BaseModel):
    kpis: dict
    charts: dict
    alertas: dict
    recomendaciones: list[str]
