# ============================================================
# SCHEMAS: Firma Documental SST
# Archivo: backend/app/schemas/firma_documental_schema.py
# FASE 1.8.4.3.10.4 - Firma Digital Certificada y Evidencia
# ============================================================

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import ConfigDict,  BaseModel, Field


class FirmaDocumentalBase(BaseModel):
    documento_id: int = Field(..., description="ID del documento en biblioteca_documental")
    rol_firmante: str = Field(..., max_length=80, description="RESPONSABLE_SST, GERENCIA, COORDINADOR, AUDITOR")
    nombre_firmante: str = Field(..., max_length=255)
    cargo_firmante: Optional[str] = Field(default=None, max_length=255)
    observaciones: Optional[str] = None


class FirmaDocumentalCreate(FirmaDocumentalBase):
    firma_digital_id: Optional[int] = None


class FirmaDocumentalAprobar(BaseModel):
    observaciones: Optional[str] = None
    firma_digital_id: Optional[int] = None


class FirmaDocumentalRechazar(BaseModel):
    motivo_rechazo: str
    observaciones: Optional[str] = None


class FirmaDocumentalResponse(BaseModel):
    id: int
    empresa_id: int
    documento_id: int
    usuario_id: Optional[int] = None
    firma_digital_id: Optional[int] = None
    rol_firmante: str
    nombre_firmante: str
    cargo_firmante: Optional[str] = None
    tipo_accion: str
    estado: str
    observaciones: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None
    hash_firma: Optional[str] = None
    activo: bool
    fecha_firma: datetime
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FirmaDocumentalDocumentoItem(BaseModel):
    id: int
    codigo_documental: str
    titulo: str
    categoria: str
    version: str
    estado: str
    estado_revision: Optional[str] = None
    responsable: Optional[str] = None
    aprobador: Optional[str] = None
    fecha_aprobacion: Optional[str] = None
    fecha_vencimiento: Optional[str] = None
    total_firmas: int = 0
    firmado_responsable_sst: bool = False
    firmado_gerencia: bool = False


class FirmaDocumentalResumen(BaseModel):
    total_documentos: int
    documentos_firmados: int
    documentos_pendientes: int
    aprobados: int
    rechazados: int
    firmas_registradas: int
    cumplimiento_firmas: float
    firmas_sst: int = 0
    firmas_gerencia: int = 0
    certificados_disponibles: int = 0


class FirmaDocumentalHistorialResponse(BaseModel):
    documento_id: int
    total: int
    firmas: List[FirmaDocumentalResponse]


class FirmaDocumentalWorkflowResponse(BaseModel):
    documento_id: int
    codigo: Optional[str] = None
    titulo: Optional[str] = None
    estado: Optional[str] = None
    estado_revision: Optional[str] = None
    workflow: Dict[str, bool]


class FirmaDocumentalCertificadoResponse(BaseModel):
    firma_id: int
    documento_id: int
    codigo_documental: Optional[str] = None
    titulo: Optional[str] = None
    version: Optional[str] = None
    estado_documento: Optional[str] = None
    estado_revision: Optional[str] = None
    rol_firmante: str
    nombre_firmante: str
    cargo_firmante: Optional[str] = None
    tipo_accion: str
    estado_firma: str
    observaciones: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None
    hash_firma: Optional[str] = None
    fecha_firma: datetime
    empresa_id: int
