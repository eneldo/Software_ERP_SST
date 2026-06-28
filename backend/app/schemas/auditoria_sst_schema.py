# ============================================================
# SCHEMAS
# AUDITORÍA SST INTELIGENTE
# FASE 1.7
# ERP SST PRO
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditoriaHallazgoCreate(BaseModel):
    tipo_hallazgo: str = "OBSERVACION"
    requisito: Optional[str] = None
    descripcion: str
    evidencia: Optional[str] = None
    causa: Optional[str] = None
    accion_recomendada: Optional[str] = None
    responsable: Optional[str] = None
    fecha_compromiso: Optional[date] = None
    estado: str = "ABIERTO"


class AuditoriaHallazgoUpdate(BaseModel):
    tipo_hallazgo: Optional[str] = None
    requisito: Optional[str] = None
    descripcion: Optional[str] = None
    evidencia: Optional[str] = None
    causa: Optional[str] = None
    accion_recomendada: Optional[str] = None
    responsable: Optional[str] = None
    fecha_compromiso: Optional[date] = None
    estado: Optional[str] = None


class AuditoriaHallazgoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    auditoria_id: int
    empresa_id: int
    usuario_id: Optional[int]

    codigo: str
    tipo_hallazgo: str
    requisito: Optional[str]
    descripcion: str
    evidencia: Optional[str]
    causa: Optional[str]
    accion_recomendada: Optional[str]
    responsable: Optional[str]
    fecha_compromiso: Optional[date]
    estado: str
    plan_mejoramiento_id: Optional[int]
    activo: bool

    fecha_creacion: Optional[datetime]
    fecha_actualizacion: Optional[datetime]


class AuditoriaCreate(BaseModel):
    empresa_id: int
    nombre: str

    tipo_auditoria: str = "INTERNA"
    estado: str = "PROGRAMADA"

    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    criterio: Optional[str] = None

    auditor_lider: Optional[str] = None
    equipo_auditor: Optional[str] = None

    fecha_programada: Optional[date] = None
    fecha_inicio: Optional[date] = None
    fecha_cierre: Optional[date] = None

    conclusiones: Optional[str] = None
    recomendaciones: Optional[str] = None


class AuditoriaUpdate(BaseModel):
    nombre: Optional[str] = None

    tipo_auditoria: Optional[str] = None
    estado: Optional[str] = None

    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    criterio: Optional[str] = None

    auditor_lider: Optional[str] = None
    equipo_auditor: Optional[str] = None

    fecha_programada: Optional[date] = None
    fecha_inicio: Optional[date] = None
    fecha_cierre: Optional[date] = None

    conclusiones: Optional[str] = None
    recomendaciones: Optional[str] = None

    porcentaje_cierre: Optional[int] = None
    activo: Optional[bool] = None


class AuditoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: int
    usuario_id: Optional[int]

    codigo: str
    nombre: str

    tipo_auditoria: str
    estado: str

    objetivo: Optional[str]
    alcance: Optional[str]
    criterio: Optional[str]

    auditor_lider: Optional[str]
    equipo_auditor: Optional[str]

    fecha_programada: Optional[date]
    fecha_inicio: Optional[date]
    fecha_cierre: Optional[date]

    total_hallazgos: int
    no_conformidades: int
    observaciones: int
    oportunidades_mejora: int

    porcentaje_cierre: int

    conclusiones: Optional[str]
    recomendaciones: Optional[str]

    activo: bool

    fecha_creacion: Optional[datetime]
    fecha_actualizacion: Optional[datetime]

    hallazgos: list[AuditoriaHallazgoResponse] = []


class AuditoriaDashboard(BaseModel):
    total_auditorias: int
    programadas: int
    en_proceso: int
    cerradas: int

    total_hallazgos: int
    no_conformidades: int
    observaciones: int
    oportunidades_mejora: int

    hallazgos_abiertos: int = 0
    hallazgos_en_proceso: int = 0
    hallazgos_cerrados: int = 0

    no_conformidades_abiertas: int = 0

    planes_generados: int = 0
    planes_pendientes: int = 0

    riesgo_alto: int = 0
    riesgo_medio: int = 0
    riesgo_bajo: int = 0

    porcentaje_cierre_general: float
    cumplimiento_hallazgos: float = 0