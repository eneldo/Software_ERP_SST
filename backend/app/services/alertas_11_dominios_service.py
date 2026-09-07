# ============================================================
# SERVICIO ALERTAS 11 DOMINIOS
# H-020: Consolidador de alertas para todos los módulos SST
# ============================================================

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.notificacion_sst import NotificacionSST
from app.models.matriz_legal import MatrizLegalSST
from app.models.politica_sst import PoliticaSST
from app.models.capacitacion import CapacitacionSST
from app.models.examen_medico import ExamenMedico
from app.models.epp import EPPEntrega
from app.models.inspeccion import InspeccionSST
from app.models.incidente import IncidenteAccidenteSST
from app.models.auditoria_sst import AuditoriaSST
from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.matriz_peligros import MatrizPeligrosSST
from app.models.biblioteca_documental import BibliotecaDocumental


DIAS_AVISO_DEFAULT = [30, 15, 7, 1]


def _crear_notif(db, empresa_id, modulo, tipo, ref_id, titulo, desc, prioridad="MEDIA"):
    existe = (
        db.query(NotificacionSST)
        .filter(
            NotificacionSST.empresa_id == empresa_id,
            NotificacionSST.modulo == modulo,
            NotificacionSST.referencia_id == ref_id,
            NotificacionSST.tipo == tipo,
        )
        .first()
    )
    if existe:
        return False
    notif = NotificacionSST(
        empresa_id=empresa_id,
        modulo=modulo,
        referencia_id=ref_id,
        tipo=tipo,
        titulo=titulo,
        descripcion=desc,
        prioridad=prioridad,
        estado="PENDIENTE",
    )
    db.add(notif)
    return True


def alertas_matriz_legal(db, empresa_id, hoy):
    from app.services.alertas_matriz_legal_service import generar_alertas_vencimiento_legal
    return generar_alertas_vencimiento_legal(db, empresa_id)


def alertas_politicas(db, empresa_id, hoy):
    count = 0
    politicas = (
        db.query(PoliticaSST)
        .filter(PoliticaSST.empresa_id == empresa_id, PoliticaSST.activo == True)
        .all()
    )
    for p in politicas:
        if p.fecha_vigencia_fin and (p.fecha_vigencia_fin - hoy).days in DIAS_AVISO_DEFAULT:
            prioridad = "ALTA" if (p.fecha_vigencia_fin - hoy).days <= 7 else "MEDIA"
            if _crear_notif(db, empresa_id, "POLITICAS", "VIGENCIA_POLITICA", p.id,
                            f"Política {p.tipo_politica} vence en {(p.fecha_vigencia_fin - hoy).days} días",
                            f"La política {p.codigo} vence el {p.fecha_vigencia_fin.isoformat()}. Requiere revisión.",
                            prioridad):
                count += 1
    return count


def alertas_capacitaciones(db, empresa_id, hoy):
    count = 0
    caps = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.estado == "PROGRAMADA",
            CapacitacionSST.fecha_programada != None,
        )
        .all()
    )
    for c in caps:
        dias = (c.fecha_programada - hoy).days
        if dias in [15, 7, 3, 1]:
            prioridad = "ALTA" if dias <= 3 else "MEDIA"
            if _crear_notif(db, empresa_id, "CAPACITACIONES", "CAPACITACION_PROXIMA", c.id,
                            f"Capacitación '{c.titulo}' en {dias} días",
                            f"Programada para {c.fecha_programada.isoformat()}. Tipo: {c.tipo_capacitacion}.",
                            prioridad):
                count += 1
    return count


def alertas_examenes(db, empresa_id, hoy):
    count = 0
    examenes = (
        db.query(ExamenMedico)
        .filter(
            ExamenMedico.fecha_vencimiento != None,
            ExamenMedico.activo == True,
        )
        .all()
    )
    for e in examenes:
        dias = (e.fecha_vencimiento - hoy).days
        if dias in [30, 15, 7, 1]:
            prioridad = "ALTA" if dias <= 7 else "MEDIA"
            if _crear_notif(db, empresa_id, "EXAMENES", "EXAMEN_PROXIMO", e.id,
                            f"Examen médico vence en {dias} días",
                            f"Vence: {e.fecha_vencimiento.isoformat()}. Empleado ID: {e.empleado_id}.",
                            prioridad):
                count += 1
    return count


def alertas_epp(db, empresa_id, hoy):
    count = 0
    epps = (
        db.query(EPPEntrega)
        .filter(
            EPPEntrega.empresa_id == empresa_id,
            EPPEntrega.fecha_reposicion != None,
            EPPEntrega.activo == True,
        )
        .all()
    )
    for e in epps:
        dias = (e.fecha_reposicion - hoy).days
        if dias in [30, 15, 7, 1]:
            prioridad = "ALTA" if dias <= 7 else "MEDIA"
            if _crear_notif(db, empresa_id, "EPP", "EPP_REPOSICION", e.id,
                            f"EPP requiere reposición en {dias} días",
                            f"Reposición: {e.fecha_reposicion.isoformat()}. Marca: {e.marca or 'N/A'}.",
                            prioridad):
                count += 1
    return count


def alertas_inspecciones(db, empresa_id, hoy):
    count = 0
    inspecciones = (
        db.query(InspeccionSST)
        .filter(
            InspeccionSST.empresa_id == empresa_id,
            InspeccionSST.estado == "PROGRAMADA",
            InspeccionSST.fecha_programada != None,
        )
        .all()
    )
    for ins in inspecciones:
        dias = (ins.fecha_programada - hoy).days
        if dias in [7, 3, 1]:
            prioridad = "ALTA" if dias <= 3 else "MEDIA"
            if _crear_notif(db, empresa_id, "INSPECCIONES", "INSPECCION_PROXIMA", ins.id,
                            f"Inspección programada en {dias} días",
                            f"Fecha: {ins.fecha_programada.isoformat()}. Tipo: {ins.tipo_inspeccion}.",
                            prioridad):
                count += 1
    return count


def alertas_incidentes(db, empresa_id, hoy):
    count = 0
    incidentes = (
        db.query(IncidenteAccidenteSST)
        .filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.estado != "CERRADO",
            IncidenteAccidenteSST.activo == True,
        )
        .all()
    )
    for inc in incidentes:
        if inc.fecha_evento:
            dias_abierto = (hoy - inc.fecha_evento).days
            if dias_abierto >= 30:
                prioridad = "ALTA"
                if _crear_notif(db, empresa_id, "INCIDENTES", "INCIDENTE_ABIERTO", inc.id,
                                f"Incidente {inc.codigo} abierto hace {dias_abierto} días",
                                f"Estado: {inc.estado}. Requiere seguimiento y cierre.",
                                prioridad):
                    count += 1
    return count


def alertas_auditorias(db, empresa_id, hoy):
    count = 0
    auditorias = (
        db.query(AuditoriaSST)
        .filter(
            AuditoriaSST.empresa_id == empresa_id,
            AuditoriaSST.estado == "PROGRAMADA",
            AuditoriaSST.fecha_programada != None,
        )
        .all()
    )
    for a in auditorias:
        dias = (a.fecha_programada - hoy).days
        if dias in [30, 15, 7, 1]:
            prioridad = "ALTA" if dias <= 7 else "MEDIA"
            if _crear_notif(db, empresa_id, "AUDITORIAS", "AUDITORIA_PROXIMA", a.id,
                            f"Auditoría programada en {dias} días",
                            f"Fecha: {a.fecha_programada.isoformat()}. Tipo: {a.tipo_auditoria}.",
                            prioridad):
                count += 1
    return count


def alertas_planes_mejora(db, empresa_id, hoy):
    count = 0
    planes = (
        db.query(PlanMejoramientoSST)
        .filter(
            PlanMejoramientoSST.empresa_id == empresa_id,
            PlanMejoramientoSST.estado != "CERRADO",
            PlanMejoramientoSST.activo == True,
        )
        .all()
    )
    for p in planes:
        if p.fecha_compromiso:
            dias = (p.fecha_compromiso - hoy).days
            if dias in [15, 7, 3, 1]:
                prioridad = "ALTA" if dias <= 7 else "MEDIA"
                if _crear_notif(db, empresa_id, "PLANES_MEJORA", "PLAN_VENCIMIENTO", p.id,
                                f"Plan de mejora {p.codigo} vence en {dias} días",
                                f"Fecha compromiso: {p.fecha_compromiso.isoformat()}. Avance: {p.porcentaje_avance or 0}%.",
                                prioridad):
                    count += 1
        if p.fecha_compromiso and p.fecha_compromiso < hoy and p.estado != "CERRADO":
            if _crear_notif(db, empresa_id, "PLANES_MEJORA", "PLAN_VENCIDO", p.id,
                            f"Plan de mejora {p.codigo} VENCIDO",
                            f"Venció el {p.fecha_compromiso.isoformat()}. Estado: {p.estado}.",
                            "ALTA"):
                count += 1
    return count


def alertas_controles(db, empresa_id, hoy):
    count = 0
    controles = (
        db.query(MatrizPeligrosSST)
        .filter(
            MatrizPeligrosSST.empresa_id == empresa_id,
            MatrizPeligrosSST.fecha_proxima_revision != None,
            MatrizPeligrosSST.activo == True,
        )
        .all()
    )
    for c in controles:
        dias = (c.fecha_proxima_revision - hoy).days
        if dias in [30, 15, 7, 1]:
            prioridad = "ALTA" if dias <= 7 else "MEDIA"
            if _crear_notif(db, empresa_id, "CONTROLES", "CONTROL_REVISION", c.id,
                            f"Peligro {c.codigo} requiere revisión en {dias} días",
                            f"Próxima revisión: {c.fecha_proxima_revision.isoformat()}.",
                            prioridad):
                count += 1
    return count


def alertas_documentos(db, empresa_id, hoy):
    count = 0
    docs = (
        db.query(BibliotecaDocumental)
        .filter(
            BibliotecaDocumental.empresa_id == empresa_id,
            BibliotecaDocumental.fecha_vigencia_fin != None,
            BibliotecaDocumental.activo == True,
        )
        .all()
    )
    for d in docs:
        dias = (d.fecha_vigencia_fin - hoy).days
        if dias in [30, 15, 7, 1]:
            prioridad = "ALTA" if dias <= 7 else "MEDIA"
            if _crear_notif(db, empresa_id, "DOCUMENTOS", "DOC_VENCIMIENTO", d.id,
                            f"Documento '{d.titulo}' vence en {dias} días",
                            f"Vigencia hasta: {d.fecha_vigencia_fin.isoformat()}. Requiere actualización.",
                            prioridad):
                count += 1
    return count


FUNCIONES_ALERTAS = [
    ("MATRIZ_LEGAL", alertas_matriz_legal),
    ("POLITICAS", alertas_politicas),
    ("CAPACITACIONES", alertas_capacitaciones),
    ("EXAMENES", alertas_examenes),
    ("EPP", alertas_epp),
    ("INSPECCIONES", alertas_inspecciones),
    ("INCIDENTES", alertas_incidentes),
    ("AUDITORIAS", alertas_auditorias),
    ("PLANES_MEJORA", alertas_planes_mejora),
    ("CONTROLES", alertas_controles),
    ("DOCUMENTOS", alertas_documentos),
]


def generar_alertas_consolidadas(db, empresa_id: int) -> dict:
    hoy = date.today()
    resultado = {"dominios": {}, "total_nuevas": 0}

    for dominio, fn in FUNCIONES_ALERTAS:
        try:
            n = fn(db, empresa_id, hoy)
            resultado["dominios"][dominio] = {"nuevas": n}
            resultado["total_nuevas"] += n
        except Exception as ex:
            resultado["dominios"][dominio] = {"nuevas": 0, "error": str(ex)[:200]}

    if resultado["total_nuevas"] > 0:
        db.commit()

    return resultado


def resumen_alertas_11_dominios(db, empresa_id: int) -> dict:
    hoy = date.today()
    resumen = {}

    for dominio, _ in FUNCIONES_ALERTAS:
        total = (
            db.query(func.count(NotificacionSST.id))
            .filter(
                NotificacionSST.empresa_id == empresa_id,
                NotificacionSST.modulo == dominio,
                NotificacionSST.estado == "PENDIENTE",
            )
            .scalar()
        )
        criticas = (
            db.query(func.count(NotificacionSST.id))
            .filter(
                NotificacionSST.empresa_id == empresa_id,
                NotificacionSST.modulo == dominio,
                NotificacionSST.estado == "PENDIENTE",
                NotificacionSST.prioridad == "ALTA",
            )
            .scalar()
        )
        resumen[dominio] = {"pendientes": total, "criticas": criticas}

    return resumen
