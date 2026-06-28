# ============================================================
# SERVICE WORKFLOW MEDIDAS CORRECTIVAS
# ERP SST PRO - FASE 1.1.8.7.3
# ============================================================

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.archivo_sst import ArchivoSST
from app.models.capa import CapaSST, CapaSeguimientoSST


WORKFLOW_ESTADOS = [
    "BORRADOR",
    "ABIERTA",
    "PLANIFICADA",
    "EN_EJECUCION",
    "VERIFICACION",
    "PENDIENTE_APROBACION",
    "CERRADA",
]

ESTADOS_FINALES = {"CERRADA", "ANULADA"}


def normalizar_estado(estado: str | None) -> str:
    value = str(estado or "ABIERTA").strip().upper()

    if value == "EN_PROCESO":
        return "EN_EJECUCION"

    if value == "VERIFICACIÓN":
        return "VERIFICACION"

    return value or "ABIERTA"


def agregar_traza_medida(item: CapaSST, texto: str):
    linea = f"[{datetime.utcnow().isoformat()}] {texto}"

    item.trazabilidad = (
        (item.trazabilidad + "\n" if item.trazabilidad else "")
        + linea
    )


def conteo_evidencias(db: Session, capa_id: int) -> int:
    return (
        db.query(func.count(ArchivoSST.id))
        .filter(
            ArchivoSST.modulo.in_(["CAPA", "MEDIDAS_CORRECTIVAS"]),
            ArchivoSST.referencia_id == capa_id,
            ArchivoSST.activo.is_(True),
        )
        .scalar()
        or 0
    )


def conteo_seguimientos(db: Session, capa_id: int) -> int:
    return (
        db.query(func.count(CapaSeguimientoSST.id))
        .filter(
            CapaSeguimientoSST.capa_id == capa_id,
            CapaSeguimientoSST.activo.is_(True),
        )
        .scalar()
        or 0
    )


def evaluar_bloqueos_estado(db: Session, item: CapaSST) -> list[str]:
    bloqueos = []
    estado = normalizar_estado(item.estado)

    if estado in ESTADOS_FINALES:
        return bloqueos

    if estado in {"BORRADOR", "ABIERTA"}:
        if not item.responsable:
            bloqueos.append("Debe asignar responsable.")
        if not item.fecha_compromiso:
            bloqueos.append("Debe definir fecha compromiso.")
        if not item.prioridad:
            bloqueos.append("Debe definir prioridad.")

    if estado in {"PLANIFICADA", "EN_EJECUCION"}:
        if (
            not item.accion_correctiva
            and not item.accion_preventiva
            and not item.accion_inmediata
        ):
            bloqueos.append("Debe registrar al menos una acción.")

        if conteo_seguimientos(db, item.id) == 0:
            bloqueos.append("Debe registrar al menos un seguimiento.")

    if estado == "VERIFICACION":
        if float(item.avance or 0) < 100:
            bloqueos.append("El avance debe ser 100%.")

        if conteo_evidencias(db, item.id) == 0:
            bloqueos.append("Debe adjuntar evidencias.")

        if not item.verificacion_eficacia:
            bloqueos.append("Debe evaluar la eficacia.")

    if estado == "PENDIENTE_APROBACION":
        if getattr(item, "requiere_aprobacion", False) and not getattr(
            item, "aprobada_por", None
        ):
            bloqueos.append("La medida requiere aprobación antes del cierre.")

    return bloqueos


def obtener_siguiente_estado(item: CapaSST) -> str | None:
    estado = normalizar_estado(item.estado)

    if estado not in WORKFLOW_ESTADOS:
        return "ABIERTA"

    index = WORKFLOW_ESTADOS.index(estado)

    if index >= len(WORKFLOW_ESTADOS) - 1:
        return None

    return WORKFLOW_ESTADOS[index + 1]


def construir_workflow_estado(db: Session, item: CapaSST) -> dict:
    actual = normalizar_estado(item.estado)

    index_actual = (
        WORKFLOW_ESTADOS.index(actual)
        if actual in WORKFLOW_ESTADOS
        else 1
    )

    pasos = []

    for index, estado in enumerate(WORKFLOW_ESTADOS):
        if index < index_actual:
            status = "COMPLETADO"
        elif index == index_actual:
            status = "ACTUAL"
        else:
            status = "PENDIENTE"

        pasos.append(
            {
                "estado": estado,
                "status": status,
                "orden": index + 1,
            }
        )

    bloqueos = evaluar_bloqueos_estado(db, item)
    siguiente_estado = obtener_siguiente_estado(item)

    return {
        "capa_id": item.id,
        "estado_actual": actual,
        "pasos": pasos,
        "puede_avanzar": len(bloqueos) == 0 and siguiente_estado is not None,
        "siguiente_estado": siguiente_estado,
        "bloqueos": bloqueos,
    }


def avanzar_workflow(
    db: Session,
    item: CapaSST,
    nuevo_estado: str | None,
    usuario_id: int | None = None,
    observacion: str | None = None,
) -> CapaSST:
    actual = normalizar_estado(item.estado)

    destino = (
        normalizar_estado(nuevo_estado)
        if nuevo_estado
        else obtener_siguiente_estado(item)
    )

    if not destino:
        raise ValueError("No existe un siguiente estado para la medida.")

    if destino not in WORKFLOW_ESTADOS and destino != "ANULADA":
        raise ValueError("Estado de workflow no permitido.")

    if actual != "PENDIENTE_APROBACION":
        bloqueos = evaluar_bloqueos_estado(db, item)

        if bloqueos:
            raise ValueError("No se puede avanzar: " + " ".join(bloqueos))

    if destino == "CERRADA":
        if float(item.avance or 0) < 100:
            raise ValueError("No se puede cerrar. El avance debe ser 100%.")

        if conteo_evidencias(db, item.id) == 0:
            raise ValueError("No se puede cerrar. Debe tener evidencias.")

        if not item.verificacion_eficacia:
            raise ValueError("No se puede cerrar. Debe evaluar eficacia.")

        item.fecha_cierre = item.fecha_cierre or date.today()

    item.estado = destino

    agregar_traza_medida(
        item,
        f"Workflow cambiado de {actual} a {destino} por usuario "
        f"{usuario_id or ''}. {observacion or ''}",
    )

    return item


def evaluar_eficacia(
    item: CapaSST,
    resultado: str,
    porcentaje: float | None,
    verificacion: str,
    usuario_id: int | None = None,
    observacion: str | None = None,
):
    resultado_normalizado = str(resultado or "").strip().upper()

    if resultado_normalizado in {"SI", "SÍ", "EFECTIVA", "EFICAZ"}:
        item.efectiva = True
        porcentaje_final = 100.0 if porcentaje is None else porcentaje

    elif resultado_normalizado in {"PARCIAL", "PARCIALMENTE"}:
        item.efectiva = False
        porcentaje_final = 50.0 if porcentaje is None else porcentaje

    elif resultado_normalizado in {"NO", "NO_EFECTIVA", "INEFICAZ"}:
        item.efectiva = False
        porcentaje_final = 0.0 if porcentaje is None else porcentaje

    else:
        raise ValueError("Resultado de eficacia no permitido. Use SI, PARCIAL o NO.")

    setattr(item, "porcentaje_eficacia", porcentaje_final)
    setattr(item, "fecha_verificacion_eficacia", date.today())
    setattr(item, "verificada_por", usuario_id)

    item.verificacion_eficacia = verificacion

    if float(item.avance or 0) >= 100:
        item.estado = (
            "PENDIENTE_APROBACION"
            if getattr(item, "requiere_aprobacion", False)
            else "VERIFICACION"
        )

    agregar_traza_medida(
        item,
        f"Eficacia evaluada como {resultado_normalizado} "
        f"({porcentaje_final}%) por usuario {usuario_id or ''}. "
        f"{observacion or ''}",
    )

    return item