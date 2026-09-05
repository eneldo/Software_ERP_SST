# ============================================================
# SCHEMAS
# PLAN DE MEJORAMIENTO SST
# FASE 1.5.1
# ERP SST PRO
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


ORIGENES_HALLAZGO_PLAN = [
    "AUDITORIA",
    "INSPECCION",
    "INCIDENTE",
    "ACCIDENTE",
    "ESTANDAR_MINIMO",
    "INDICADOR",
    "REVISION_DIRECCION",
    "REQUISITO_LEGAL",
    "OTRO",
]


# ============================================================
# BASE
# ============================================================

RESULTADOS_VERIFICACION_PLAN = [
    "APROBADO",
    "RECHAZADO",
]


class PlanMejoramientoBase(BaseModel):
    empresa_id: int

    evaluacion_id: Optional[int] = None
    item_evaluacion_id: Optional[int] = None

    origen_hallazgo: str = "OTRO"
    origen_id: Optional[int] = None

    verificado_por: Optional[int] = None
    fecha_verificacion: Optional[date] = None
    resultado_verificacion: Optional[str] = None

    @field_validator("origen_hallazgo")
    @classmethod
    def validar_origen(cls, value):
        valor = str(value or "OTRO").strip().upper()
        if valor not in ORIGENES_HALLAZGO_PLAN:
            raise ValueError("Origen de hallazgo no válido")
        return valor

    @field_validator("resultado_verificacion")
    @classmethod
    def validar_resultado_verificacion(cls, value):
        if value is None:
            return value
        valor = str(value).strip().upper()
        if valor not in RESULTADOS_VERIFICACION_PLAN:
            raise ValueError("Resultado de verificación no válido")
        return valor

    titulo: str = Field(..., max_length=255)

    descripcion: Optional[str] = None

    causa: Optional[str] = None

    accion_correctiva: str

    responsable: Optional[str] = None

    prioridad: str = "MEDIA"

    estado: str = "PENDIENTE"

    fecha_apertura: Optional[date] = None

    fecha_compromiso: Optional[date] = None

    fecha_cierre: Optional[date] = None

    porcentaje_avance: int = 0

    evidencia: Optional[str] = None

    observaciones: Optional[str] = None

    activo: bool = True


# ============================================================
# CREAR
# ============================================================

class PlanMejoramientoCreate(PlanMejoramientoBase):
    pass


# ============================================================
# ACTUALIZAR
# ============================================================

class PlanMejoramientoUpdate(BaseModel):
    titulo: Optional[str] = None

    origen_hallazgo: Optional[str] = None
    origen_id: Optional[int] = None

    verificado_por: Optional[int] = None
    fecha_verificacion: Optional[date] = None
    resultado_verificacion: Optional[str] = None

    descripcion: Optional[str] = None

    causa: Optional[str] = None

    accion_correctiva: Optional[str] = None

    responsable: Optional[str] = None

    prioridad: Optional[str] = None

    estado: Optional[str] = None

    fecha_apertura: Optional[date] = None

    fecha_compromiso: Optional[date] = None

    fecha_cierre: Optional[date] = None

    porcentaje_avance: Optional[int] = None

    evidencia: Optional[str] = None

    observaciones: Optional[str] = None

    activo: Optional[bool] = None

    @field_validator("origen_hallazgo")
    @classmethod
    def validar_origen(cls, value):
        if value is None:
            return value
        valor = str(value).strip().upper()
        if valor not in ORIGENES_HALLAZGO_PLAN:
            raise ValueError("Origen de hallazgo no válido")
        return valor

    @field_validator("resultado_verificacion")
    @classmethod
    def validar_resultado_verificacion(cls, value):
        if value is None:
            return value
        valor = str(value).strip().upper()
        if valor not in RESULTADOS_VERIFICACION_PLAN:
            raise ValueError("Resultado de verificación no válido")
        return valor


# ============================================================
# RESPUESTA
# ============================================================

class PlanMejoramientoResponse(PlanMejoramientoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

    usuario_id: Optional[int] = None

    codigo: str

    fecha_creacion: Optional[datetime] = None

    fecha_actualizacion: Optional[datetime] = None


# ============================================================
# DASHBOARD KPI
# ============================================================

class PlanMejoramientoDashboard(BaseModel):
    
    total_acciones: int

    pendientes: int

    en_proceso: int

    vencidas: int

    finalizadas: int

    cumplimiento: float
    
    total_seguimientos: int = 0
    acciones_con_seguimiento: int = 0
    acciones_sin_seguimiento: int = 0
    seguimientos_proximos: int = 0
    seguimientos_vencidos: int = 0


# ============================================================
# GENERACIÓN AUTOMÁTICA
# ============================================================

class GenerarPlanDesdeEvaluacionRequest(BaseModel):
    evaluacion_id: int


# ============================================================
# FILTROS
# ============================================================

class PlanMejoramientoFiltro(BaseModel):
    empresa_id: Optional[int] = None

    estado: Optional[str] = None

    prioridad: Optional[str] = None

    responsable: Optional[str] = None

    buscar: Optional[str] = None


# ============================================================
# CAMBIO DE ESTADO
# ============================================================

class CambioEstadoPlan(BaseModel):
    estado: str


# ============================================================
# CAMBIO DE AVANCE
# ============================================================

class CambioAvancePlan(BaseModel):
    porcentaje_avance: int


# ============================================================
# CIERRE DE ACCIÓN
# ============================================================

class CerrarPlanRequest(BaseModel):
    observaciones: Optional[str] = None


class VerificarPlanRequest(BaseModel):
    resultado: str
    observaciones: Optional[str] = None

    @field_validator("resultado")
    @classmethod
    def validar_resultado(cls, value):
        valor = str(value or "").strip().upper()
        if valor not in RESULTADOS_VERIFICACION_PLAN:
            raise ValueError("Resultado de verificación no válido")
        return valor


# ============================================================
# ESTADOS OFICIALES SST
# ============================================================

ESTADOS_PLAN_SST = [
    "PENDIENTE",
    "EN_PROCESO",
    "VENCIDO",
    "FINALIZADO",
]


# ============================================================
# PRIORIDADES OFICIALES SST
# ============================================================

PRIORIDADES_PLAN_SST = [
    "ALTA",
    "MEDIA",
    "BAJA",
]