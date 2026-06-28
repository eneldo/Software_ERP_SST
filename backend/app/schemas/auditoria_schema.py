
# ============================================================
# SCHEMAS AUDITORÍA SISTEMA PRO
# ERP SST PRO ENTERPRISE - FASE 35.4.1
# ============================================================
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AuditoriaResponse(BaseModel):
    id:int
    usuario_id:int|None=None
    empresa_id:int|None=None
    metodo:str|None=None
    ruta:str|None=None
    accion:str|None=None
    ip:str|None=None
    user_agent:str|None=None
    fecha:datetime|None=None
    model_config=ConfigDict(from_attributes=True)

class AuditoriaDetalleResponse(AuditoriaResponse):
    usuario_nombre:str|None=None
    usuario_correo:str|None=None
    empresa_nombre:str|None=None

class AuditoriaKPIResponse(BaseModel):
    total_eventos:int=0
    eventos_get:int=0
    eventos_post:int=0
    eventos_put:int=0
    eventos_delete:int=0
    eventos_patch:int=0
    usuarios_unicos:int=0
    ips_unicas:int=0
    rutas_unicas:int=0
    eventos_sin_usuario:int=0

class AuditoriaSistemaResponse(BaseModel):
    kpis:AuditoriaKPIResponse
    eventos:list[AuditoriaDetalleResponse]
    metodos:dict[str,int]={}
    rutas_top:list[dict]=[]
    usuarios_top:list[dict]=[]
    recomendaciones:list[str]=[]
