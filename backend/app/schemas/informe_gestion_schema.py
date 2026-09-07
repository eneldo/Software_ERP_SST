# ============================================================
# SCHEMAS Pydantic PARA EL MÓDULO INFORME DE GESTIÓN SG-SST
#
# Ubicación: backend/app/schemas/informe_gestion_schema.py
# ============================================================

from datetime import date, datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ============================================================
# SCHEMAS DEL INFORME PRINCIPAL
# ============================================================

class InformeGestionBase(BaseModel):
    anio: int
    periodo_evaluado: Optional[str] = None
    fecha_inicio_periodo: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None
    sede_id: Optional[int] = None
    responsable_sst_nombre: Optional[str] = None
    representante_legal_nombre: Optional[str] = None
    titulo: Optional[str] = "INFORME ANUAL DE GESTIÓN SG-SST"


class InformeGestionCreate(InformeGestionBase):
    pass


class InformeGestionUpdate(BaseModel):
    titulo: Optional[str] = None
    periodo_evaluado: Optional[str] = None
    fecha_inicio_periodo: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None
    sede_id: Optional[int] = None
    responsable_sst_nombre: Optional[str] = None
    representante_legal_nombre: Optional[str] = None
    resumen_ejecutivo: Optional[str] = None
    estado: Optional[str] = None


class InformeGestionResponse(BaseModel):
    id: int
    empresa_id: int
    codigo: str
    titulo: str
    anio: int
    periodo_evaluado: Optional[str] = None
    fecha_inicio_periodo: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None
    sede_id: Optional[int] = None
    responsable_sst_nombre: Optional[str] = None
    representante_legal_nombre: Optional[str] = None
    version: int
    estado: str
    resumen_ejecutivo: Optional[str] = None
    cumplimiento_global: Optional[float] = None
    cumplimiento_plan_anual: Optional[float] = None
    cumplimiento_estandares: Optional[float] = None
    total_secciones: int
    total_evidencias: int
    total_recomendaciones: int
    fecha_generacion: Optional[datetime] = None
    fecha_presentacion: Optional[datetime] = None
    fecha_aprobacion: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    codigo_documental: Optional[str] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class InformeGestionList(BaseModel):
    id: int
    codigo: str
    titulo: str
    anio: int
    estado: str
    version: int
    cumplimiento_global: Optional[float] = None
    responsable_sst_nombre: Optional[str] = None
    fecha_generacion: Optional[datetime] = None
    activo: bool

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE VERSIONES
# ============================================================

class InformeGestionVersionCreate(BaseModel):
    motivo_cambio: Optional[str] = None


class InformeGestionVersionResponse(BaseModel):
    id: int
    informe_id: int
    version_numero: int
    estado_anterior: Optional[str] = None
    estado_nuevo: str
    motivo_cambio: Optional[str] = None
    usuario_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE SECCIONES
# ============================================================

class InformeGestionSeccionBase(BaseModel):
    codigo_seccion: str
    nombre_seccion: str
    orden: int = 0


class InformeGestionSeccionCreate(InformeGestionSeccionBase):
    datos_seccion: Optional[Any] = None


class InformeGestionSeccionUpdate(BaseModel):
    nombre_seccion: Optional[str] = None
    orden: Optional[int] = None
    datos_seccion: Optional[Any] = None
    estado_seccion: Optional[str] = None
    observaciones: Optional[str] = None


class InformeGestionSeccionResponse(BaseModel):
    id: int
    informe_id: int
    codigo_seccion: str
    nombre_seccion: str
    orden: int
    datos_seccion: Optional[Any] = None
    estado_seccion: str
    observaciones: Optional[str] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE EVIDENCIAS
# ============================================================

class InformeGestionEvidenciaCreate(BaseModel):
    codigo_seccion: Optional[str] = None
    nombre: str
    tipo_archivo: str
    tamano_bytes: Optional[int] = None
    hash_archivo: Optional[str] = None
    archivo_url: Optional[str] = None
    archivo_nombre_original: Optional[str] = None
    modulo_origen: Optional[str] = None
    registro_origen_id: Optional[int] = None


class InformeGestionEvidenciaResponse(BaseModel):
    id: int
    informe_id: int
    codigo_seccion: Optional[str] = None
    nombre: str
    tipo_archivo: str
    tamano_bytes: Optional[int] = None
    archivo_url: Optional[str] = None
    archivo_nombre_original: Optional[str] = None
    modulo_origen: Optional[str] = None
    usuario_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE RECOMENDACIONES
# ============================================================

class InformeGestionRecomendacionBase(BaseModel):
    hallazgo: str
    riesgo: Optional[str] = None
    recomendacion: str
    prioridad: str = "MEDIA"
    accion_propuesta: Optional[str] = None
    responsable_sugerido: Optional[str] = None
    recursos_requeridos: Optional[str] = None
    fecha_recomendada: Optional[date] = None


class InformeGestionRecomendacionCreate(InformeGestionRecomendacionBase):
    pass


class InformeGestionRecomendacionUpdate(BaseModel):
    hallazgo: Optional[str] = None
    riesgo: Optional[str] = None
    recomendacion: Optional[str] = None
    prioridad: Optional[str] = None
    accion_propuesta: Optional[str] = None
    responsable_sugerido: Optional[str] = None
    recursos_requeridos: Optional[str] = None
    fecha_recomendada: Optional[date] = None
    estado: Optional[str] = None


class InformeGestionRecomendacionResponse(BaseModel):
    id: int
    informe_id: int
    hallazgo: str
    riesgo: Optional[str] = None
    recomendacion: str
    prioridad: str
    accion_propuesta: Optional[str] = None
    responsable_sugerido: Optional[str] = None
    recursos_requeridos: Optional[str] = None
    fecha_recomendada: Optional[date] = None
    estado: str
    usuario_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE APROBACIONES
# ============================================================

class InformeGestionAprobacionCreate(BaseModel):
    tipo_accion: str
    resultado: str
    observaciones: Optional[str] = None
    comentarios: Optional[str] = None
    hash_firma: Optional[str] = None


class InformeGestionAprobacionResponse(BaseModel):
    id: int
    informe_id: int
    usuario_id: Optional[int] = None
    tipo_accion: str
    resultado: str
    observaciones: Optional[str] = None
    comentarios: Optional[str] = None
    hash_firma: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE RENDICIÓN DE CUENTAS
# ============================================================

class RendicionCuentasBase(BaseModel):
    persona_nombre: str
    cargo: Optional[str] = None
    rol_sgsst: Optional[str] = None
    responsabilidad_asignada: str
    actividades: Optional[str] = None
    meta: Optional[str] = None
    resultado: Optional[str] = None
    porcentaje_cumplimiento: Optional[float] = None
    dificultades: Optional[str] = None
    actividades_pendientes: Optional[str] = None
    compromisos: Optional[str] = None
    acciones_mejora: Optional[str] = None
    fecha_evaluacion: Optional[date] = None
    observaciones: Optional[str] = None


class RendicionCuentasCreate(RendicionCuentasBase):
    informe_id: Optional[int] = None


class RendicionCuentasUpdate(BaseModel):
    persona_nombre: Optional[str] = None
    cargo: Optional[str] = None
    rol_sgsst: Optional[str] = None
    responsabilidad_asignada: Optional[str] = None
    actividades: Optional[str] = None
    meta: Optional[str] = None
    resultado: Optional[str] = None
    porcentaje_cumplimiento: Optional[float] = None
    estado: Optional[str] = None
    dificultades: Optional[str] = None
    actividades_pendientes: Optional[str] = None
    compromisos: Optional[str] = None
    acciones_mejora: Optional[str] = None
    fecha_evaluacion: Optional[date] = None
    observaciones: Optional[str] = None


class RendicionCuentasResponse(BaseModel):
    id: int
    informe_id: Optional[int] = None
    empresa_id: int
    usuario_id: Optional[int] = None
    persona_nombre: str
    cargo: Optional[str] = None
    rol_sgsst: Optional[str] = None
    responsabilidad_asignada: str
    actividades: Optional[str] = None
    meta: Optional[str] = None
    resultado: Optional[str] = None
    porcentaje_cumplimiento: Optional[float] = None
    estado: str
    dificultades: Optional[str] = None
    actividades_pendientes: Optional[str] = None
    compromisos: Optional[str] = None
    acciones_mejora: Optional[str] = None
    fecha_evaluacion: Optional[date] = None
    observaciones: Optional[str] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class RendicionCuentasResponsabilidadBase(BaseModel):
    responsabilidad: str
    descripcion: Optional[str] = None
    actividades_ejecutadas: Optional[str] = None
    meta: Optional[str] = None
    resultado_obtenido: Optional[str] = None
    porcentaje_cumplimiento: Optional[float] = None
    estado: Optional[str] = "PENDIENTE"
    evidencias: Optional[str] = None
    fecha_cumplimiento: Optional[date] = None


class RendicionCuentasResponsabilidadCreate(RendicionCuentasResponsabilidadBase):
    pass


class RendicionCuentasResponsabilidadResponse(BaseModel):
    id: int
    rendicion_id: int
    responsabilidad: str
    descripcion: Optional[str] = None
    actividades_ejecutadas: Optional[str] = None
    meta: Optional[str] = None
    resultado_obtenido: Optional[str] = None
    porcentaje_cumplimiento: Optional[float] = None
    estado: str
    evidencias: Optional[str] = None
    fecha_cumplimiento: Optional[date] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE DASHBOARD Y CONSOLIDACIÓN
# ============================================================

class DashboardInformeGestion(BaseModel):
    total_informes: int
    informes_borrador: int
    informes_en_revision: int
    informes_aprobados: int
    informes_cerrados: int
    informe_activo: Optional[InformeGestionResponse] = None
    proximo_vencimiento: Optional[date] = None


class ConsolidarInformeRequest(BaseModel):
    informe_id: int
    forzar: Optional[bool] = False


class ConsolidarInformeResponse(BaseModel):
    informe_id: int
    secciones_consolidadas: int
    total_registros: int
    mensaje: str


class GenerarPDFRequest(BaseModel):
    informe_id: int
    incluir_evidencias: Optional[bool] = True
    incluir_graficos: Optional[bool] = True


class GenerarExcelRequest(BaseModel):
    informe_id: int
    hojas: Optional[List[str]] = None


class PresentarInformeRequest(BaseModel):
    informe_id: int
    observaciones: Optional[str] = None


class AprobarInformeRequest(BaseModel):
    informe_id: int
    resultado: str  # APROBADO, APROBADO_CON_OBSERVACIONES, DEVUELTO
    observaciones: Optional[str] = None
    comentarios: Optional[str] = None
    hash_firma: Optional[str] = None
