# ============================================================
# SCHEMAS ALERTAS MEDIDAS CORRECTIVAS SST
# ERP SST PRO - FASE 1.1.8.7.3
# ============================================================
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AlertaMedidaCorrectivaResponse(BaseModel):
    id:int; empresa_id:int; capa_id:int; usuario_id:int|None=None
    tipo_alerta:str; prioridad:str|None=None; estado:str|None=None
    titulo:str; mensaje:str; accion_recomendada:str|None=None; url_destino:str|None=None
    leida:bool=False; archivada:bool=False; activa:bool=True
    fecha_evento:datetime|None=None; fecha_vencimiento:datetime|None=None; fecha_lectura:datetime|None=None
    fecha_creacion:datetime|None=None; fecha_actualizacion:datetime|None=None
    capa_codigo:str|None=None; capa_titulo:str|None=None; empresa_nombre:str|None=None
    model_config=ConfigDict(from_attributes=True)

class AlertaMedidaCorrectivaResumen(BaseModel):
    total:int=0; pendientes:int=0; leidas:int=0; criticas:int=0; altas:int=0
    por_tipo:dict[str,int]={}

class AlertasMedidasResponse(BaseModel):
    resumen:AlertaMedidaCorrectivaResumen
    alertas:list[AlertaMedidaCorrectivaResponse]

class WorkflowTransicionRequest(BaseModel):
    nuevo_estado:str
    observacion:str|None=None

class EficaciaEvaluacionRequest(BaseModel):
    resultado:str=Field(..., description="SI, PARCIAL o NO")
    porcentaje_eficacia:float|None=None
    verificacion_eficacia:str=Field(..., min_length=5)
    observacion:str|None=None

class WorkflowEstadoResponse(BaseModel):
    capa_id:int
    estado_actual:str
    pasos:list[dict]
    puede_avanzar:bool
    siguiente_estado:str|None=None
    bloqueos:list[str]=[]
