# ============================================================
# ROUTER WORKFLOW + EFICACIA + ALERTAS MEDIDAS CORRECTIVAS
# ERP SST PRO - FASE 1.1.8.7.3
# ============================================================
from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.alerta_medida_correctiva import AlertaMedidaCorrectivaSST
from app.models.capa import CapaSST
from app.models.empresa import Empresa
from app.schemas.alerta_medida_correctiva_schema import AlertaMedidaCorrectivaResponse,AlertaMedidaCorrectivaResumen,AlertasMedidasResponse,EficaciaEvaluacionRequest,WorkflowEstadoResponse,WorkflowTransicionRequest
from app.services.alertas_medidas_service import generar_alertas_masivas,generar_alertas_para_medida
from app.services.workflow_medidas_service import avanzar_workflow,construir_workflow_estado,evaluar_eficacia
router=APIRouter(prefix="/medidas-correctivas-enterprise", tags=["Workflow Medidas Correctivas Enterprise"])
ROLES_SST=["SUPER_ADMIN","ADMIN_EMPRESA","RESPONSABLE_SST","AUDITOR"]

def _validar_empresa_usuario(usuario, empresa_id:int|None):
    if not empresa_id or getattr(usuario,"rol",None)=="SUPER_ADMIN": return
    if getattr(usuario,"empresa_id",None) and int(usuario.empresa_id)==int(empresa_id): return
    raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")

def _alerta_to_response(db, alerta):
    capa=db.query(CapaSST).filter(CapaSST.id==alerta.capa_id).first(); empresa=db.query(Empresa).filter(Empresa.id==alerta.empresa_id).first()
    return AlertaMedidaCorrectivaResponse(id=alerta.id,empresa_id=alerta.empresa_id,capa_id=alerta.capa_id,usuario_id=alerta.usuario_id,tipo_alerta=alerta.tipo_alerta,prioridad=alerta.prioridad,estado=alerta.estado,titulo=alerta.titulo,mensaje=alerta.mensaje,accion_recomendada=alerta.accion_recomendada,url_destino=alerta.url_destino,leida=alerta.leida,archivada=alerta.archivada,activa=alerta.activa,fecha_evento=alerta.fecha_evento,fecha_vencimiento=alerta.fecha_vencimiento,fecha_lectura=alerta.fecha_lectura,fecha_creacion=alerta.fecha_creacion,fecha_actualizacion=alerta.fecha_actualizacion,capa_codigo=capa.codigo if capa else None,capa_titulo=capa.titulo if capa else None,empresa_nombre=empresa.nombre if empresa else None)

@router.get("/alertas", response_model=AlertasMedidasResponse)
def listar_alertas_medidas(empresa_id:int|None=Query(default=None), tipo_alerta:str|None=Query(default=None), prioridad:str|None=Query(default=None), leida:bool|None=Query(default=None), solo_pendientes:bool=Query(default=True), limit:int=Query(default=300, ge=1, le=2000), db:Session=Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    _validar_empresa_usuario(usuario,empresa_id)
    q=db.query(AlertaMedidaCorrectivaSST).filter(AlertaMedidaCorrectivaSST.activa.is_(True))
    if getattr(usuario,"rol",None)!="SUPER_ADMIN" and getattr(usuario,"empresa_id",None): q=q.filter(AlertaMedidaCorrectivaSST.empresa_id==usuario.empresa_id)
    if empresa_id: q=q.filter(AlertaMedidaCorrectivaSST.empresa_id==empresa_id)
    if tipo_alerta: q=q.filter(func.upper(AlertaMedidaCorrectivaSST.tipo_alerta)==tipo_alerta.upper().strip())
    if prioridad: q=q.filter(func.upper(AlertaMedidaCorrectivaSST.prioridad)==prioridad.upper().strip())
    if leida is not None: q=q.filter(AlertaMedidaCorrectivaSST.leida.is_(leida))
    if solo_pendientes: q=q.filter(AlertaMedidaCorrectivaSST.archivada.is_(False))
    alertas=q.order_by(AlertaMedidaCorrectivaSST.id.desc()).limit(limit).all(); por_tipo={}
    for a in alertas: por_tipo[a.tipo_alerta]=por_tipo.get(a.tipo_alerta,0)+1
    resumen=AlertaMedidaCorrectivaResumen(total=len(alertas),pendientes=sum(1 for a in alertas if not a.leida),leidas=sum(1 for a in alertas if a.leida),criticas=sum(1 for a in alertas if a.prioridad=="CRITICA"),altas=sum(1 for a in alertas if a.prioridad=="ALTA"),por_tipo=por_tipo)
    return AlertasMedidasResponse(resumen=resumen, alertas=[_alerta_to_response(db,a) for a in alertas])

@router.post("/alertas/generar")
def generar_alertas(empresa_id:int|None=Query(default=None), db:Session=Depends(get_db), usuario=Depends(require_roles(["SUPER_ADMIN","ADMIN_EMPRESA","RESPONSABLE_SST"]))):
    _validar_empresa_usuario(usuario,empresa_id); creadas=generar_alertas_masivas(db,empresa_id=empresa_id); return {"ok":True,"total_generadas":len(creadas)}

@router.post("/alertas/{alerta_id}/leer")
def marcar_alerta_leida(alerta_id:int, db:Session=Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    alerta=db.query(AlertaMedidaCorrectivaSST).filter(AlertaMedidaCorrectivaSST.id==alerta_id).first()
    if not alerta: raise HTTPException(status_code=404, detail="Alerta no encontrada")
    _validar_empresa_usuario(usuario,alerta.empresa_id); alerta.leida=True; alerta.fecha_lectura=datetime.utcnow(); db.commit(); return {"ok":True}

@router.post("/alertas/{alerta_id}/archivar")
def archivar_alerta(alerta_id:int, db:Session=Depends(get_db), usuario=Depends(require_roles(["SUPER_ADMIN","ADMIN_EMPRESA","RESPONSABLE_SST"]))):
    alerta=db.query(AlertaMedidaCorrectivaSST).filter(AlertaMedidaCorrectivaSST.id==alerta_id).first()
    if not alerta: raise HTTPException(status_code=404, detail="Alerta no encontrada")
    _validar_empresa_usuario(usuario,alerta.empresa_id); alerta.archivada=True; alerta.leida=True; alerta.fecha_lectura=alerta.fecha_lectura or datetime.utcnow(); db.commit(); return {"ok":True}

@router.get("/{medida_id}/workflow", response_model=WorkflowEstadoResponse)
def obtener_workflow_medida(medida_id:int, db:Session=Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    item=db.query(CapaSST).filter(CapaSST.id==medida_id,CapaSST.activo.is_(True)).first()
    if not item: raise HTTPException(status_code=404, detail="Medida correctiva no encontrada")
    _validar_empresa_usuario(usuario,item.empresa_id); return construir_workflow_estado(db,item)

@router.post("/{medida_id}/workflow/avanzar", response_model=WorkflowEstadoResponse)
def avanzar_workflow_medida(medida_id:int,data:WorkflowTransicionRequest,db:Session=Depends(get_db),usuario=Depends(require_roles(["SUPER_ADMIN","ADMIN_EMPRESA","RESPONSABLE_SST"]))):
    item=db.query(CapaSST).filter(CapaSST.id==medida_id,CapaSST.activo.is_(True)).first()
    if not item: raise HTTPException(status_code=404, detail="Medida correctiva no encontrada")
    _validar_empresa_usuario(usuario,item.empresa_id)
    try:
        avanzar_workflow(db,item,data.nuevo_estado,getattr(usuario,"id",None),data.observacion); generar_alertas_para_medida(db,item); db.commit(); db.refresh(item)
    except ValueError as exc:
        db.rollback(); raise HTTPException(status_code=400, detail=str(exc))
    return construir_workflow_estado(db,item)

@router.post("/{medida_id}/eficacia", response_model=WorkflowEstadoResponse)
def evaluar_eficacia_medida(medida_id:int,data:EficaciaEvaluacionRequest,db:Session=Depends(get_db),usuario=Depends(require_roles(["SUPER_ADMIN","ADMIN_EMPRESA","RESPONSABLE_SST"]))):
    item=db.query(CapaSST).filter(CapaSST.id==medida_id,CapaSST.activo.is_(True)).first()
    if not item: raise HTTPException(status_code=404, detail="Medida correctiva no encontrada")
    _validar_empresa_usuario(usuario,item.empresa_id)
    try:
        evaluar_eficacia(item,data.resultado,data.porcentaje_eficacia,data.verificacion_eficacia,getattr(usuario,"id",None),data.observacion); generar_alertas_para_medida(db,item); db.commit(); db.refresh(item)
    except ValueError as exc:
        db.rollback(); raise HTTPException(status_code=400, detail=str(exc))
    return construir_workflow_estado(db,item)
