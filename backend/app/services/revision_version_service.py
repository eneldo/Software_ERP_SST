# ============================================================
# ERP SST PRO ENTERPRISE
# MÓDULO: VERSIONADO DOCUMENTAL
# ARCHIVO: backend/app/services/revision_version_service.py
#
# USO:
# Servicio encargado de crear, listar, comparar y restaurar
# versiones documentales de Revisión por la Dirección SST.
#
# Permite:
# - Crear snapshot V1, V2, V3...
# - Guardar datos históricos en JSONB
# - Calcular hash SHA256 del snapshot
# - Comparar versiones
# - Restaurar una versión anterior creando una nueva versión
#
# FASE 1.8.4.3 — VERSIONADO DOCUMENTAL ENTERPRISE PRO
# ============================================================

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.revision_direccion import RevisionDireccionSST
from app.models.revision_version import RevisionDireccionVersionSST


# ============================================================
# UTILIDADES
# ============================================================

def convertir_valor_json(valor: Any):
    """
    Convierte valores especiales de Python a tipos compatibles con JSON.
    """

    if isinstance(valor, (datetime, date)):
        return valor.isoformat()

    if isinstance(valor, Decimal):
        return float(valor)

    return valor


def calcular_hash_snapshot(datos: Dict[str, Any]) -> str:
    """
    Calcula SHA256 estable a partir del JSON del snapshot.
    """

    contenido = json.dumps(
        datos,
        ensure_ascii=False,
        sort_keys=True,
        default=convertir_valor_json,
    )

    return hashlib.sha256(
        contenido.encode("utf-8")
    ).hexdigest()


def obtener_siguiente_version(
    db: Session,
    revision_id: int,
) -> int:
    """
    Obtiene el siguiente número de versión disponible.
    """

    ultima = (
        db.query(RevisionDireccionVersionSST)
        .filter(
            RevisionDireccionVersionSST.revision_id == revision_id
        )
        .order_by(
            RevisionDireccionVersionSST.version_numero.desc()
        )
        .first()
    )

    if not ultima:
        return 1

    return ultima.version_numero + 1


def revision_a_snapshot(
    revision: RevisionDireccionSST,
) -> Dict[str, Any]:
    """
    Convierte una revisión completa a JSON histórico.
    """

    compromisos = []

    for compromiso in revision.compromisos or []:
        if getattr(compromiso, "activo", True):
            compromisos.append(
                {
                    "id": compromiso.id,
                    "revision_id": compromiso.revision_id,
                    "empresa_id": compromiso.empresa_id,
                    "compromiso": compromiso.compromiso,
                    "responsable": compromiso.responsable,
                    "fecha_compromiso": convertir_valor_json(
                        compromiso.fecha_compromiso
                    ),
                    "fecha_cierre": convertir_valor_json(
                        compromiso.fecha_cierre
                    ),
                    "prioridad": compromiso.prioridad,
                    "estado": compromiso.estado,
                    "observaciones": compromiso.observaciones,
                    "activo": compromiso.activo,
                    "fecha_creacion": convertir_valor_json(
                        compromiso.fecha_creacion
                    ),
                    "fecha_actualizacion": convertir_valor_json(
                        compromiso.fecha_actualizacion
                    ),
                }
            )

    return {
        "id": revision.id,
        "empresa_id": revision.empresa_id,
        "usuario_id": revision.usuario_id,
        "gerente_usuario_id": revision.gerente_usuario_id,
        "responsable_sst_usuario_id": revision.responsable_sst_usuario_id,
        "codigo": revision.codigo,
        "titulo": revision.titulo,
        "fecha_revision": convertir_valor_json(revision.fecha_revision),
        "periodo_evaluado": revision.periodo_evaluado,
        "gerente": revision.gerente,
        "responsable_sst": revision.responsable_sst,
        "participantes": revision.participantes,
        "objetivo": revision.objetivo,
        "alcance": revision.alcance,
        "agenda": revision.agenda,
        "resumen_auditorias": revision.resumen_auditorias,
        "resumen_indicadores": revision.resumen_indicadores,
        "resumen_planes_mejora": revision.resumen_planes_mejora,
        "resumen_accidentes": revision.resumen_accidentes,
        "resumen_capacitaciones": revision.resumen_capacitaciones,
        "resumen_cumplimiento_legal": revision.resumen_cumplimiento_legal,
        "conclusiones": revision.conclusiones,
        "decisiones": revision.decisiones,
        "recomendaciones": revision.recomendaciones,
        "total_compromisos": revision.total_compromisos,
        "compromisos_pendientes": revision.compromisos_pendientes,
        "compromisos_cerrados": revision.compromisos_cerrados,
        "porcentaje_cumplimiento": convertir_valor_json(
            revision.porcentaje_cumplimiento
        ),
        "estado": revision.estado,
        "activo": revision.activo,
        "bloqueado": revision.bloqueado,
        "fecha_bloqueo": convertir_valor_json(revision.fecha_bloqueo),
        "bloqueado_por_usuario_id": revision.bloqueado_por_usuario_id,
        "fecha_aprobacion": convertir_valor_json(revision.fecha_aprobacion),
        "aprobado_por_usuario_id": revision.aprobado_por_usuario_id,
        "motivo_bloqueo": revision.motivo_bloqueo,
        "version_documental": revision.version_documental,
        "hash_final_sha256": revision.hash_final_sha256,
        "codigo_validacion_final": revision.codigo_validacion_final,
        "fecha_creacion": convertir_valor_json(revision.fecha_creacion),
        "fecha_actualizacion": convertir_valor_json(
            revision.fecha_actualizacion
        ),
        "compromisos": compromisos,
    }


# ============================================================
# CREAR SNAPSHOT
# ============================================================

def crear_snapshot_revision(
    db: Session,
    revision: RevisionDireccionSST,
    usuario_id: int | None = None,
    accion: str = "SNAPSHOT",
    observacion: str | None = None,
) -> RevisionDireccionVersionSST:
    """
    Crea una versión documental de la revisión actual.
    """

    version_numero = obtener_siguiente_version(
        db=db,
        revision_id=revision.id,
    )

    datos = revision_a_snapshot(revision)
    hash_snapshot = calcular_hash_snapshot(datos)

    version = RevisionDireccionVersionSST(
        revision_id=revision.id,
        version_numero=version_numero,
        codigo_version=f"{revision.codigo}-V{version_numero}",
        usuario_id=usuario_id,
        accion=accion,
        datos_json=datos,
        hash_sha256=hash_snapshot,
        observacion=observacion,
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return version


# ============================================================
# LISTAR VERSIONES
# ============================================================

def listar_versiones_revision(
    db: Session,
    revision_id: int,
):
    """
    Lista las versiones documentales de una revisión.
    """

    return (
        db.query(RevisionDireccionVersionSST)
        .filter(
            RevisionDireccionVersionSST.revision_id == revision_id
        )
        .order_by(
            RevisionDireccionVersionSST.version_numero.desc()
        )
        .all()
    )


def obtener_version_o_404(
    db: Session,
    version_id: int,
) -> RevisionDireccionVersionSST:
    """
    Obtiene una versión por ID o retorna error 404.
    """

    version = (
        db.query(RevisionDireccionVersionSST)
        .filter(
            RevisionDireccionVersionSST.id == version_id
        )
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=404,
            detail="Versión documental no encontrada.",
        )

    return version


# ============================================================
# COMPARAR VERSIONES
# ============================================================

def comparar_diccionarios(
    origen: Dict[str, Any],
    destino: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compara dos snapshots y retorna campos modificados.
    """

    diferencias = {}

    claves = sorted(
        set(origen.keys()) | set(destino.keys())
    )

    for clave in claves:
        valor_origen = origen.get(clave)
        valor_destino = destino.get(clave)

        if valor_origen != valor_destino:
            diferencias[clave] = {
                "antes": valor_origen,
                "despues": valor_destino,
            }

    return diferencias


def comparar_versiones(
    db: Session,
    version_origen_id: int,
    version_destino_id: int,
) -> Dict[str, Any]:
    """
    Compara dos versiones documentales.
    """

    version_origen = obtener_version_o_404(
        db=db,
        version_id=version_origen_id,
    )

    version_destino = obtener_version_o_404(
        db=db,
        version_id=version_destino_id,
    )

    if version_origen.revision_id != version_destino.revision_id:
        raise HTTPException(
            status_code=400,
            detail="Las versiones no pertenecen a la misma revisión.",
        )

    diferencias = comparar_diccionarios(
        version_origen.datos_json,
        version_destino.datos_json,
    )

    return {
        "version_origen": version_origen.version_numero,
        "version_destino": version_destino.version_numero,
        "diferencias": diferencias,
    }


# ============================================================
# RESTAURAR VERSION
# ============================================================

def restaurar_version_revision(
    db: Session,
    version_id: int,
    usuario_id: int | None = None,
    observacion: str | None = None,
) -> RevisionDireccionVersionSST:
    """
    Restaura una versión histórica creando una nueva versión.
    No sobrescribe el historial.
    """

    version = obtener_version_o_404(
        db=db,
        version_id=version_id,
    )

    revision = (
        db.query(RevisionDireccionSST)
        .filter(
            RevisionDireccionSST.id == version.revision_id,
            RevisionDireccionSST.activo == True,
        )
        .first()
    )

    if not revision:
        raise HTTPException(
            status_code=404,
            detail="Revisión original no encontrada.",
        )

    if getattr(revision, "bloqueado", False):
        raise HTTPException(
            status_code=403,
            detail=(
                "La revisión está bloqueada legalmente y no puede restaurarse."
            ),
        )

    datos = version.datos_json

    campos_restaurables = [
        "empresa_id",
        "gerente_usuario_id",
        "responsable_sst_usuario_id",
        "titulo",
        "fecha_revision",
        "periodo_evaluado",
        "gerente",
        "responsable_sst",
        "participantes",
        "objetivo",
        "alcance",
        "agenda",
        "resumen_auditorias",
        "resumen_indicadores",
        "resumen_planes_mejora",
        "resumen_accidentes",
        "resumen_capacitaciones",
        "resumen_cumplimiento_legal",
        "conclusiones",
        "decisiones",
        "recomendaciones",
        "estado",
    ]

    for campo in campos_restaurables:
        if campo in datos:
            setattr(
                revision,
                campo,
                datos.get(campo),
            )

    db.commit()
    db.refresh(revision)

    return crear_snapshot_revision(
        db=db,
        revision=revision,
        usuario_id=usuario_id,
        accion="RESTAURAR",
        observacion=(
            observacion
            or f"Restauración desde {version.codigo_version}"
        ),
    )