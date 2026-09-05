# ============================================================
# SCHEMA DASHBOARD EJECUTIVO SST PRO ENTERPRISE
# FASE 1.6 - ERP SST PRO
# ============================================================

from pydantic import BaseModel
from typing import List, Optional


class KpiCard(BaseModel):
    codigo: str
    titulo: str
    valor: int | float | str
    subtitulo: Optional[str] = None
    estado: str = "OK"
    url_detalle: Optional[str] = None


class SerieSimple(BaseModel):
    nombre: str
    valor: int | float


class ActividadReciente(BaseModel):
    id: int
    modulo: str
    accion: str
    ruta: str
    metodo: str
    status_code: Optional[int] = None
    fecha: str


class DashboardEjecutivoSSTResponse(BaseModel):
    empresa_id: Optional[int] = None
    empresa_nombre: str
    cumplimiento_sg_sst: float
    cumplimiento_resolucion_0312: float
    nivel_alerta: str
    kpis: List[KpiCard]
    empleados_estado: List[SerieSimple]
    estructura_organizacional: List[SerieSimple]
    seguridad_auditoria: List[SerieSimple]
    avance_phva: List[SerieSimple]
    actividades_recientes: List[ActividadReciente]
