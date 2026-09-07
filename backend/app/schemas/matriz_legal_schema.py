# ============================================================
# SCHEMAS MATRIZ LEGAL SST
# FASE 1.8.5.2 - MATRIZ LEGAL SST BI EXECUTIVE
# Mantiene compatibilidad con FASE 2.4 y agrega respuestas BI
# ============================================================

from typing import Optional, List
from datetime import date, datetime
from pydantic import ConfigDict,  BaseModel


class MatrizLegalCreate(BaseModel):
    empresa_id: int
    codigo: str = "ML-SST-001"
    norma: str
    tipo_norma: Optional[str] = None
    numero_norma: Optional[str] = None
    anio: Optional[str] = None
    articulo: Optional[str] = None
    requisito_legal: str
    tema: Optional[str] = None
    entidad_emisora: Optional[str] = None
    aplicabilidad: str = "APLICA"
    estado_cumplimiento: str = "PENDIENTE"
    estado_norma: str = "VIGENTE"
    responsable: Optional[str] = None
    fecha_revision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None


class MatrizLegalUpdate(BaseModel):
    codigo: Optional[str] = None
    norma: Optional[str] = None
    tipo_norma: Optional[str] = None
    numero_norma: Optional[str] = None
    anio: Optional[str] = None
    articulo: Optional[str] = None
    requisito_legal: Optional[str] = None
    tema: Optional[str] = None
    entidad_emisora: Optional[str] = None
    aplicabilidad: Optional[str] = None
    estado_cumplimiento: Optional[str] = None
    estado_norma: Optional[str] = None
    responsable: Optional[str] = None
    fecha_revision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None
    activo: Optional[bool] = None


class MatrizLegalResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None
    archivo_id: Optional[int] = None

    codigo: str
    norma: str
    tipo_norma: Optional[str] = None
    numero_norma: Optional[str] = None
    anio: Optional[str] = None
    articulo: Optional[str] = None
    requisito_legal: str
    tema: Optional[str] = None
    entidad_emisora: Optional[str] = None
    aplicabilidad: str
    estado_cumplimiento: str
    estado_norma: str
    responsable: Optional[str] = None
    fecha_revision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None

    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_extension: Optional[str] = None

    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MatrizLegalResumenResponse(BaseModel):
    total: int
    cumplen: int
    pendientes: int
    no_cumplen: int
    vigentes: int
    derogadas: int
    porcentaje_cumplimiento: int


# ============================================================
# FASE 1.8.5.1 / 1.8.5.2 - Schemas Dashboard y BI Executive
# ============================================================

class MatrizLegalSerieItem(BaseModel):
    nombre: str
    total: int


class MatrizLegalResponsableItem(BaseModel):
    nombre: str
    total: int


class MatrizLegalRevisionItem(BaseModel):
    id: int
    codigo: str
    norma: str
    fecha: date
    dias: int
    tipo: str


class MatrizLegalTendenciaItem(BaseModel):
    mes: str
    cumplimiento: int


class MatrizLegalDashboardResponse(BaseModel):
    total: int
    cumplen: int
    pendientes: int
    no_cumplen: int
    vigentes: int
    derogadas: int
    modificadas: int
    sin_evidencia: int
    con_evidencia: int
    sin_responsable: int
    responsables: int
    proximas_revision: int
    vencidas_revision: int
    porcentaje_cumplimiento: int
    porcentaje_evidencias: int
    riesgo_legal: str
    por_tipo_norma: List[MatrizLegalSerieItem] = []
    por_cumplimiento: List[MatrizLegalSerieItem] = []
    por_estado_norma: List[MatrizLegalSerieItem] = []
    temas_criticos: List[MatrizLegalSerieItem] = []
    responsables_top: List[MatrizLegalResponsableItem] = []
    proximas_revision_items: List[MatrizLegalRevisionItem] = []
    tendencia_cumplimiento: List[MatrizLegalTendenciaItem] = []


class MatrizLegalBIResponse(MatrizLegalDashboardResponse):
    pass
