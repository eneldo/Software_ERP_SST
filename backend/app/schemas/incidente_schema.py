# ============================================================
# SCHEMAS INCIDENTES Y ACCIDENTES SST ENTERPRISE
# FASE 1.1.8.8.3 — INVESTIGACIÓN Y ÁRBOL DE CAUSAS
# Archivo: backend/app/schemas/incidente_schema.py
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


TIPOS_EVENTO = {"INCIDENTE", "ACCIDENTE"}
CLASIFICACIONES = {"INCIDENTE", "ACCIDENTE_LEVE", "ACCIDENTE_GRAVE", "ACCIDENTE_MORTAL"}
ESTADOS_EVENTO = {"REPORTADO", "EN_INVESTIGACION", "CON_CAPA", "CERRADO", "ANULADO"}
ESTADOS_INVESTIGACION = {"PENDIENTE", "EN_PROCESO", "ANALISIS_CAUSAL", "PLAN_ACCION", "CERRADA"}
SEVERIDADES = {"BAJA", "MEDIA", "ALTA", "CRITICA"}
GRAVEDADES_LESION = {"LEVE", "MODERADA", "GRAVE", "MORTAL"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class IncidenteBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int = Field(..., gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)

    codigo: str = Field(..., min_length=2, max_length=80)
    tipo_evento: str = Field(default="INCIDENTE", max_length=40)
    clasificacion: str = Field(default="INCIDENTE", max_length=60)
    titulo: str = Field(..., min_length=3, max_length=255)
    descripcion: str = Field(..., min_length=5)
    lugar: Optional[str] = Field(default=None, max_length=255)

    fecha_evento: date
    hora_evento: Optional[str] = Field(default=None, max_length=20)
    fecha_reporte: Optional[date] = None

    estado: str = "REPORTADO"
    severidad: str = "BAJA"
    consecuencia: Optional[str] = Field(default=None, max_length=120)
    dias_incapacidad: Optional[int] = Field(default=0, ge=0)
    requiere_investigacion: bool = True
    requiere_capa: bool = False
    capa_id: Optional[int] = Field(default=None, gt=0)

    acto_inseguro: Optional[str] = None
    condicion_insegura: Optional[str] = None
    causa_inmediata: Optional[str] = None
    causa_basica: Optional[str] = None
    causa_raiz: Optional[str] = None
    accion_inmediata: Optional[str] = None

    # FASE 1.1.8.8.3 — Investigación y Árbol de Causas
    equipo_investigador: Optional[str] = None
    investigador_lider: Optional[str] = Field(default=None, max_length=255)
    fecha_investigacion: Optional[date] = None
    metodologia_investigacion: Optional[str] = Field(default="5_PORQUES", max_length=80)
    estado_investigacion: Optional[str] = "PENDIENTE"
    descripcion_hechos: Optional[str] = None
    agente_material: Optional[str] = Field(default=None, max_length=255)
    mecanismo_evento: Optional[str] = Field(default=None, max_length=255)
    tipo_contacto: Optional[str] = Field(default=None, max_length=255)
    porque_1: Optional[str] = None
    porque_2: Optional[str] = None
    porque_3: Optional[str] = None
    porque_4: Optional[str] = None
    porque_5: Optional[str] = None
    factores_personales: Optional[str] = None
    factores_trabajo: Optional[str] = None
    factores_organizacionales: Optional[str] = None
    causas_directas: Optional[str] = None
    causas_indirectas: Optional[str] = None
    arbol_causas: Optional[str] = None
    controles_existentes: Optional[str] = None
    controles_recomendados: Optional[str] = None
    plan_investigacion: Optional[str] = None
    conclusion_investigacion: Optional[str] = None
    recomendaciones_investigacion: Optional[str] = None
    investigacion_cerrada: bool = False
    fecha_cierre_investigacion: Optional[datetime] = None

    observaciones: Optional[str] = None
    trazabilidad: Optional[str] = None
    activo: bool = True

    @field_validator("codigo", "tipo_evento", "clasificacion", "estado", "severidad", "estado_investigacion", "metodologia_investigacion")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value)

    @field_validator("tipo_evento")
    @classmethod
    def validar_tipo(cls, value):
        value = _upper_clean(value, "INCIDENTE")
        if value not in TIPOS_EVENTO:
            raise ValueError("Tipo de evento no válido")
        return value

    @field_validator("clasificacion")
    @classmethod
    def validar_clasificacion(cls, value):
        value = _upper_clean(value, "INCIDENTE")
        if value not in CLASIFICACIONES:
            raise ValueError("Clasificación no válida")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "REPORTADO")
        if value not in ESTADOS_EVENTO:
            raise ValueError("Estado no válido")
        return value

    @field_validator("severidad")
    @classmethod
    def validar_severidad(cls, value):
        value = _upper_clean(value, "BAJA")
        if value not in SEVERIDADES:
            raise ValueError("Severidad no válida")
        return value


class IncidenteCreate(IncidenteBase):
    pass


class IncidenteUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = Field(default=None, gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=80)
    tipo_evento: Optional[str] = Field(default=None, max_length=40)
    clasificacion: Optional[str] = Field(default=None, max_length=60)
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=5)
    lugar: Optional[str] = Field(default=None, max_length=255)
    fecha_evento: Optional[date] = None
    hora_evento: Optional[str] = Field(default=None, max_length=20)
    fecha_reporte: Optional[date] = None
    estado: Optional[str] = None
    severidad: Optional[str] = None
    consecuencia: Optional[str] = Field(default=None, max_length=120)
    dias_incapacidad: Optional[int] = Field(default=None, ge=0)
    requiere_investigacion: Optional[bool] = None
    requiere_capa: Optional[bool] = None
    capa_id: Optional[int] = Field(default=None, gt=0)
    acto_inseguro: Optional[str] = None
    condicion_insegura: Optional[str] = None
    causa_inmediata: Optional[str] = None
    causa_basica: Optional[str] = None
    causa_raiz: Optional[str] = None
    accion_inmediata: Optional[str] = None

    equipo_investigador: Optional[str] = None
    investigador_lider: Optional[str] = Field(default=None, max_length=255)
    fecha_investigacion: Optional[date] = None
    metodologia_investigacion: Optional[str] = Field(default=None, max_length=80)
    estado_investigacion: Optional[str] = None
    descripcion_hechos: Optional[str] = None
    agente_material: Optional[str] = Field(default=None, max_length=255)
    mecanismo_evento: Optional[str] = Field(default=None, max_length=255)
    tipo_contacto: Optional[str] = Field(default=None, max_length=255)
    porque_1: Optional[str] = None
    porque_2: Optional[str] = None
    porque_3: Optional[str] = None
    porque_4: Optional[str] = None
    porque_5: Optional[str] = None
    factores_personales: Optional[str] = None
    factores_trabajo: Optional[str] = None
    factores_organizacionales: Optional[str] = None
    causas_directas: Optional[str] = None
    causas_indirectas: Optional[str] = None
    arbol_causas: Optional[str] = None
    controles_existentes: Optional[str] = None
    controles_recomendados: Optional[str] = None
    plan_investigacion: Optional[str] = None
    conclusion_investigacion: Optional[str] = None
    recomendaciones_investigacion: Optional[str] = None
    investigacion_cerrada: Optional[bool] = None
    fecha_cierre_investigacion: Optional[datetime] = None

    observaciones: Optional[str] = None
    trazabilidad: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("codigo", "tipo_evento", "clasificacion", "estado", "severidad", "estado_investigacion", "metodologia_investigacion")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class IncidenteResponse(IncidenteBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None
    empleado_documento: Optional[str] = None
    total_lesionados: int = 0
    total_testigos: int = 0
    total_evidencias: int = 0
    vencido: bool = False
    dias_desde_evento: Optional[int] = None
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class IncidenteDashboardResponse(BaseModel):
    kpis: dict
    charts: dict
    alertas: dict
    recomendaciones: list[str]


class IncidenteInvestigacionUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    equipo_investigador: Optional[str] = None
    investigador_lider: Optional[str] = Field(default=None, max_length=255)
    fecha_investigacion: Optional[date] = None
    metodologia_investigacion: Optional[str] = Field(default="5_PORQUES", max_length=80)
    estado_investigacion: Optional[str] = "EN_PROCESO"
    descripcion_hechos: Optional[str] = None
    agente_material: Optional[str] = Field(default=None, max_length=255)
    mecanismo_evento: Optional[str] = Field(default=None, max_length=255)
    tipo_contacto: Optional[str] = Field(default=None, max_length=255)
    acto_inseguro: Optional[str] = None
    condicion_insegura: Optional[str] = None
    causa_inmediata: Optional[str] = None
    causa_basica: Optional[str] = None
    causa_raiz: Optional[str] = None
    porque_1: Optional[str] = None
    porque_2: Optional[str] = None
    porque_3: Optional[str] = None
    porque_4: Optional[str] = None
    porque_5: Optional[str] = None
    factores_personales: Optional[str] = None
    factores_trabajo: Optional[str] = None
    factores_organizacionales: Optional[str] = None
    causas_directas: Optional[str] = None
    causas_indirectas: Optional[str] = None
    arbol_causas: Optional[str] = None
    controles_existentes: Optional[str] = None
    controles_recomendados: Optional[str] = None
    plan_investigacion: Optional[str] = None
    conclusion_investigacion: Optional[str] = None
    recomendaciones_investigacion: Optional[str] = None

    @field_validator("estado_investigacion", "metodologia_investigacion")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class IncidenteArbolCausasUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    descripcion_hechos: Optional[str] = None
    arbol_causas: Optional[str] = None
    causa_inmediata: Optional[str] = None
    causa_basica: Optional[str] = None
    causa_raiz: Optional[str] = None
    porque_1: Optional[str] = None
    porque_2: Optional[str] = None
    porque_3: Optional[str] = None
    porque_4: Optional[str] = None
    porque_5: Optional[str] = None
    factores_personales: Optional[str] = None
    factores_trabajo: Optional[str] = None
    factores_organizacionales: Optional[str] = None
    controles_recomendados: Optional[str] = None


class IncidenteCierreInvestigacionRequest(BaseModel):
    conclusion_investigacion: str = Field(..., min_length=5)
    recomendaciones_investigacion: Optional[str] = None
    requiere_capa: bool = False
    observacion: Optional[str] = None


class LesionadoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    incidente_id: int = Field(..., gt=0)
    empresa_id: int = Field(..., gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    nombre: str = Field(..., min_length=2, max_length=255)
    documento: Optional[str] = Field(default=None, max_length=80)
    cargo: Optional[str] = Field(default=None, max_length=255)
    parte_cuerpo_afectada: Optional[str] = Field(default=None, max_length=180)
    tipo_lesion: Optional[str] = Field(default=None, max_length=180)
    gravedad: str = "LEVE"
    dias_incapacidad: int = Field(default=0, ge=0)
    atencion_medica: bool = False
    descripcion_lesion: Optional[str] = None
    activo: bool = True

    @field_validator("gravedad")
    @classmethod
    def validar_gravedad(cls, value):
        value = _upper_clean(value, "LEVE")
        if value not in GRAVEDADES_LESION:
            raise ValueError("Gravedad de lesión no válida")
        return value


class LesionadoCreate(LesionadoBase):
    pass


class LesionadoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    empleado_id: Optional[int] = Field(default=None, gt=0)
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=255)
    documento: Optional[str] = Field(default=None, max_length=80)
    cargo: Optional[str] = Field(default=None, max_length=255)
    parte_cuerpo_afectada: Optional[str] = Field(default=None, max_length=180)
    tipo_lesion: Optional[str] = Field(default=None, max_length=180)
    gravedad: Optional[str] = None
    dias_incapacidad: Optional[int] = Field(default=None, ge=0)
    atencion_medica: Optional[bool] = None
    descripcion_lesion: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("gravedad")
    @classmethod
    def upper_gravedad(cls, value):
        return _upper_clean(value) if value is not None else value


class LesionadoResponse(LesionadoBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class TestigoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    incidente_id: int = Field(..., gt=0)
    empresa_id: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=2, max_length=255)
    documento: Optional[str] = Field(default=None, max_length=80)
    cargo: Optional[str] = Field(default=None, max_length=255)
    telefono: Optional[str] = Field(default=None, max_length=80)
    correo: Optional[str] = Field(default=None, max_length=255)
    declaracion: Optional[str] = None
    firma: Optional[str] = None
    activo: bool = True


class TestigoCreate(TestigoBase):
    pass


class TestigoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=255)
    documento: Optional[str] = Field(default=None, max_length=80)
    cargo: Optional[str] = Field(default=None, max_length=255)
    telefono: Optional[str] = Field(default=None, max_length=80)
    correo: Optional[str] = Field(default=None, max_length=255)
    declaracion: Optional[str] = None
    firma: Optional[str] = None
    activo: Optional[bool] = None


class TestigoResponse(TestigoBase):
    id: int
    firma_fecha: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, extra="ignore")
