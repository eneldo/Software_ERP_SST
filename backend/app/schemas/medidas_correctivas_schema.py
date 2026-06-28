from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class MedidaCorrectivaCreate(BaseModel):
    empresa_id:int; sede_id:int|None=None; area_id:int|None=None; cargo_id:int|None=None; empleado_id:int|None=None
    inspeccion_id:int|None=None; hallazgo_id:int|None=None
    codigo:str=Field(...,max_length=80); titulo:str=Field(...,max_length=255); descripcion:str
    tipo_accion:str='CORRECTIVA'; origen:str='MANUAL'; prioridad:str='MEDIA'; estado:str='ABIERTA'
    responsable:str|None=None; fecha_apertura:date|None=None; fecha_compromiso:date|None=None; avance:Decimal|None=0
    causa_raiz:str|None=None; porque_1:str|None=None; porque_2:str|None=None; porque_3:str|None=None; porque_4:str|None=None; porque_5:str|None=None; ishikawa_json:str|None=None
    accion_inmediata:str|None=None; accion_correctiva:str|None=None; accion_preventiva:str|None=None
    costo_estimado:Decimal|None=0; costo_real:Decimal|None=0; requiere_aprobacion:bool|None=False; observaciones:str|None=None

class MedidaCorrectivaUpdate(BaseModel):
    sede_id:int|None=None; area_id:int|None=None; cargo_id:int|None=None; empleado_id:int|None=None; inspeccion_id:int|None=None; hallazgo_id:int|None=None
    codigo:str|None=None; titulo:str|None=None; descripcion:str|None=None; tipo_accion:str|None=None; origen:str|None=None; prioridad:str|None=None; estado:str|None=None
    responsable:str|None=None; fecha_apertura:date|None=None; fecha_compromiso:date|None=None; avance:Decimal|None=None
    causa_raiz:str|None=None; porque_1:str|None=None; porque_2:str|None=None; porque_3:str|None=None; porque_4:str|None=None; porque_5:str|None=None; ishikawa_json:str|None=None
    accion_inmediata:str|None=None; accion_correctiva:str|None=None; accion_preventiva:str|None=None
    costo_estimado:Decimal|None=None; costo_real:Decimal|None=None; requiere_aprobacion:bool|None=None; observaciones:str|None=None

class MedidaCorrectivaResponse(BaseModel):
    id:int; empresa_id:int; sede_id:int|None=None; area_id:int|None=None; cargo_id:int|None=None; empleado_id:int|None=None; inspeccion_id:int|None=None; hallazgo_id:int|None=None; usuario_id:int|None=None
    codigo:str; titulo:str; descripcion:str|None=None; tipo_accion:str|None=None; origen:str|None=None; prioridad:str|None=None; estado:str|None=None; responsable:str|None=None
    fecha_apertura:date|None=None; fecha_compromiso:date|None=None; fecha_cierre:date|None=None; avance:Decimal|None=0
    causa_raiz:str|None=None; porque_1:str|None=None; porque_2:str|None=None; porque_3:str|None=None; porque_4:str|None=None; porque_5:str|None=None; ishikawa_json:str|None=None
    accion_inmediata:str|None=None; accion_correctiva:str|None=None; accion_preventiva:str|None=None
    efectiva:bool|None=None; verificacion_eficacia:str|None=None; costo_estimado:Decimal|None=0; costo_real:Decimal|None=0; requiere_aprobacion:bool|None=False; aprobada_por:int|None=None; fecha_aprobacion:datetime|None=None
    trazabilidad:str|None=None; observaciones:str|None=None; activo:bool|None=True; fecha_creacion:datetime|None=None; fecha_actualizacion:datetime|None=None
    empresa_nombre:str|None=None; sede_nombre:str|None=None; area_nombre:str|None=None; cargo_nombre:str|None=None; empleado_nombre:str|None=None; inspeccion_codigo:str|None=None; hallazgo_descripcion:str|None=None
    total_seguimientos:int=0; total_evidencias:int=0; dias_vencimiento:int|None=None; vencida:bool=False
    model_config=ConfigDict(from_attributes=True)

class MedidaCorrectivaSeguimientoCreate(BaseModel):
    fecha_seguimiento:date|None=None; responsable:str|None=None; avance:Decimal|None=0; resultado:str|None=None; comentario:str|None=None; proxima_accion:str|None=None; fecha_proximo_seguimiento:date|None=None
class MedidaCorrectivaSeguimientoUpdate(BaseModel):
    fecha_seguimiento:date|None=None; responsable:str|None=None; avance:Decimal|None=None; resultado:str|None=None; comentario:str|None=None; proxima_accion:str|None=None; fecha_proximo_seguimiento:date|None=None
class MedidaCorrectivaSeguimientoResponse(BaseModel):
    id:int; capa_id:int; empresa_id:int; usuario_id:int|None=None; fecha_seguimiento:date|None=None; responsable:str|None=None; avance:Decimal|None=0; resultado:str|None=None; comentario:str|None=None; proxima_accion:str|None=None; fecha_proximo_seguimiento:date|None=None; activo:bool|None=True; fecha_creacion:datetime|None=None; fecha_actualizacion:datetime|None=None
    model_config=ConfigDict(from_attributes=True)
class MedidaCorrectivaCierreRequest(BaseModel):
    efectiva:bool=True; verificacion_eficacia:str=Field(...,min_length=5); observacion:str|None=None
class MedidaCorrectivaAprobacionRequest(BaseModel):
    observacion:str|None=None
class MedidaCorrectivaDashboardResponse(BaseModel):
    kpis:dict; charts:dict; alertas:dict; recomendaciones:list[str]
