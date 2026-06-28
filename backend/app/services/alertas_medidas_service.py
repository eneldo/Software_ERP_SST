# ============================================================
# SERVICE ALERTAS MEDIDAS CORRECTIVAS
# ERP SST PRO - FASE 1.1.8.7.3
# ============================================================
from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.archivo_sst import ArchivoSST
from app.models.capa import CapaSST, CapaSeguimientoSST
from app.models.alerta_medida_correctiva import AlertaMedidaCorrectivaSST
ESTADOS_CERRADOS={"CERRADA","ANULADA"}

def _alerta_existente(db,capa_id,tipo):
    return db.query(AlertaMedidaCorrectivaSST).filter(AlertaMedidaCorrectivaSST.capa_id==capa_id,AlertaMedidaCorrectivaSST.tipo_alerta==tipo,AlertaMedidaCorrectivaSST.activa.is_(True),AlertaMedidaCorrectivaSST.archivada.is_(False)).first()

def crear_alerta_si_no_existe(db:Session,item:CapaSST,tipo_alerta:str,titulo:str,mensaje:str,prioridad:str="MEDIA",accion_recomendada:str|None=None):
    ex=_alerta_existente(db,item.id,tipo_alerta)
    if ex: return ex
    alerta=AlertaMedidaCorrectivaSST(empresa_id=item.empresa_id,capa_id=item.id,usuario_id=getattr(item,"usuario_id",None),tipo_alerta=tipo_alerta,prioridad=prioridad,estado="PENDIENTE",titulo=titulo,mensaje=mensaje,accion_recomendada=accion_recomendada,url_destino=f"/verificar/acciones-correctivas?id={item.id}",leida=False,archivada=False,activa=True,fecha_evento=datetime.utcnow(),fecha_vencimiento=datetime.combine(item.fecha_compromiso, datetime.min.time()) if item.fecha_compromiso else None)
    db.add(alerta); return alerta

def _total_evidencias(db,capa_id):
    return db.query(func.count(ArchivoSST.id)).filter(ArchivoSST.modulo.in_(["CAPA","MEDIDAS_CORRECTIVAS"]), ArchivoSST.referencia_id==capa_id, ArchivoSST.activo.is_(True)).scalar() or 0

def _total_seguimientos(db,capa_id):
    return db.query(func.count(CapaSeguimientoSST.id)).filter(CapaSeguimientoSST.capa_id==capa_id, CapaSeguimientoSST.activo.is_(True)).scalar() or 0

def generar_alertas_para_medida(db:Session,item:CapaSST):
    alertas=[]; estado=str(item.estado or "").upper()
    if estado in ESTADOS_CERRADOS or not item.activo: return alertas
    if not item.responsable: alertas.append(crear_alerta_si_no_existe(db,item,"SIN_RESPONSABLE","Medida correctiva sin responsable",f"La medida {item.codigo} no tiene responsable asignado.","ALTA","Asignar un responsable."))
    if not item.fecha_compromiso: alertas.append(crear_alerta_si_no_existe(db,item,"SIN_FECHA","Medida correctiva sin fecha compromiso",f"La medida {item.codigo} no tiene fecha compromiso.","MEDIA","Definir fecha compromiso."))
    if _total_seguimientos(db,item.id)==0 and estado in {"ABIERTA","PLANIFICADA","EN_EJECUCION"}: alertas.append(crear_alerta_si_no_existe(db,item,"SIN_SEGUIMIENTO","Medida correctiva sin seguimiento",f"La medida {item.codigo} no registra seguimientos activos.","MEDIA","Registrar seguimiento."))
    if _total_evidencias(db,item.id)==0 and estado in {"EN_EJECUCION","VERIFICACION","PENDIENTE_APROBACION"}: alertas.append(crear_alerta_si_no_existe(db,item,"SIN_EVIDENCIA","Medida correctiva sin evidencia",f"La medida {item.codigo} requiere evidencias antes del cierre.","ALTA","Adjuntar evidencia."))
    if item.fecha_compromiso:
        dias=(item.fecha_compromiso-date.today()).days
        if dias<0: alertas.append(crear_alerta_si_no_existe(db,item,"VENCIDA","Medida correctiva vencida",f"La medida {item.codigo} venció hace {abs(dias)} día(s).","CRITICA","Reprogramar o cerrar con evidencia."))
        elif dias<=7: alertas.append(crear_alerta_si_no_existe(db,item,"PROXIMA_A_VENCER_7","Medida próxima a vencer",f"La medida {item.codigo} vence en {dias} día(s).","ALTA","Priorizar ejecución."))
        elif dias<=15: alertas.append(crear_alerta_si_no_existe(db,item,"PROXIMA_A_VENCER_15","Medida próxima a vencer",f"La medida {item.codigo} vence en {dias} día(s).","MEDIA","Revisar avance."))
        elif dias<=30: alertas.append(crear_alerta_si_no_existe(db,item,"PROXIMA_A_VENCER_30","Medida próxima a vencer",f"La medida {item.codigo} vence en {dias} día(s).","BAJA","Mantener seguimiento."))
    if estado=="PENDIENTE_APROBACION": alertas.append(crear_alerta_si_no_existe(db,item,"PENDIENTE_APROBACION","Medida pendiente de aprobación",f"La medida {item.codigo} requiere aprobación para cierre.","ALTA","Revisar y aprobar."))
    if float(item.avance or 0)>=100 and not item.verificacion_eficacia: alertas.append(crear_alerta_si_no_existe(db,item,"EFICACIA_PENDIENTE","Eficacia pendiente",f"La medida {item.codigo} tiene avance 100% pero no tiene verificación de eficacia.","ALTA","Evaluar eficacia."))
    return [a for a in alertas if a is not None]

def generar_alertas_masivas(db:Session, empresa_id:int|None=None):
    q=db.query(CapaSST).filter(CapaSST.activo.is_(True), ~CapaSST.estado.in_(["CERRADA","ANULADA"]))
    if empresa_id: q=q.filter(CapaSST.empresa_id==empresa_id)
    creadas=[]
    for item in q.all(): creadas.extend(generar_alertas_para_medida(db,item))
    db.commit(); return creadas
