# ============================================================
# SCHEMAS: Dashboard Documental
# Archivo: backend/app/schemas/dashboard_documental_schema.py
# FASE 1.8.4.3.9 - Centro de Control Documental SST Enterprise
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class DashboardDocumentalKPI(BaseModel):
    total_documentos: int = 0
    vigentes: int = 0
    borradores: int = 0
    obsoletos: int = 0
    vencidos: int = 0
    proximos_vencer: int = 0
    pendientes_revision: int = 0
    total_versiones: int = 0
    cumplimiento_documental: float = 0


class ConteoAgrupado(BaseModel):
    nombre: str
    total: int


class DocumentoVencimientoItem(BaseModel):
    id: int
    codigo_documental: str
    titulo: str
    categoria: str
    tipo_documento: str
    estado: str
    responsable: Optional[str] = None
    version: str
    fecha_vencimiento: Optional[date] = None
    dias_restantes: Optional[int] = None
    semaforo: str


class VersionRecienteItem(BaseModel):
    id: int
    documento_id: int
    codigo_documental: Optional[str] = None
    titulo: Optional[str] = None
    version: str
    descripcion_cambio: Optional[str] = None
    usuario: Optional[str] = None
    fecha_creacion: Optional[datetime] = None


class DashboardDocumentalResponse(BaseModel):
    kpis: DashboardDocumentalKPI
    estados: list[ConteoAgrupado]
    categorias: list[ConteoAgrupado]
    responsables: list[ConteoAgrupado]
    proximos_vencer: list[DocumentoVencimientoItem]
    vencidos: list[DocumentoVencimientoItem]
    versiones_recientes: list[VersionRecienteItem]
