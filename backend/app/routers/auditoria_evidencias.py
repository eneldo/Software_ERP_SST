# ============================================================
# ROUTER AUDITORÍA INTEGRAL DE EVIDENCIAS
# ERP SST PRO ENTERPRISE
# FASE 35.4 — Auditoría Integral de Evidencias
# Archivo: backend/app/routers/auditoria_evidencias.py
# ============================================================

from __future__ import annotations

from pathlib import Path
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.archivo_sst import ArchivoSST
from app.schemas.auditoria_evidencias_schema import (
    EvidenciaAuditoriaItem,
    EvidenciaAuditoriaResponse,
    EvidenciaAuditoriaResumen,
    EvidenciaHealthResponse,
)

router = APIRouter(
    prefix="/auditoria-evidencias",
    tags=["Auditoría Integral de Evidencias"],
)

ROLES_AUDITORIA_EVIDENCIAS = ["SUPER_ADMIN", "AUDITOR"]
UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()

MODULOS_CONOCIDOS = [
    "INSPECCIONES",
    "CAPA",
    "INCIDENTES",
    "REPORTE_INSEGURIDAD",
    "REPORTE_ANONIMO_SST",
    "EPP",
    "EXAMENES_MEDICOS",
    "BIBLIOTECA_DOCUMENTAL",
    "AUDITORIAS",
    "PLAN_MEJORAMIENTO",
]


def _safe_join_upload(url_o_ruta: str | None) -> Path | None:
    if not url_o_ruta:
        return None

    valor = str(url_o_ruta).strip()

    if valor.startswith("/uploads/"):
        relativo = valor.replace("/uploads/", "", 1)
        return (UPLOAD_ROOT / relativo).resolve()

    posible = Path(valor)
    if posible.is_absolute():
        return posible.resolve()

    return (UPLOAD_ROOT / valor).resolve()


def _archivo_existe(url_o_ruta: str | None) -> bool:
    path = _safe_join_upload(url_o_ruta)
    if not path:
        return False
    try:
        return path.exists() and path.is_file()
    except Exception:
        return False


def _variant_path_from_archivo(archivo: ArchivoSST, variant: str) -> Path | None:
    """
    Detecta variantes generadas por los diferentes routers:
    - inspecciones/previews/<filename>.webp
    - inspecciones/thumbs/<filename>.webp
    - capa/<stem>_preview.webp
    - capa/<stem>_thumb.webp
    - incidentes/<stem>_preview.webp
    - incidentes/<stem>_thumb.webp
    """
    if not archivo or not archivo.nombre_archivo:
        return None

    modulo = (archivo.modulo or "").upper()
    nombre = archivo.nombre_archivo
    stem = Path(nombre).stem

    if modulo == "INSPECCIONES":
        carpeta = "previews" if variant == "preview" else "thumbs"
        return UPLOAD_ROOT / "inspecciones" / carpeta / nombre

    base = _safe_join_upload(archivo.url) or _safe_join_upload(archivo.ruta)
    if base:
        return base.parent / f"{stem}_{variant}.webp"

    return None


def _variant_existe(archivo: ArchivoSST, variant: str) -> bool:
    path = _variant_path_from_archivo(archivo, variant)
    if not path:
        return False
    try:
        return path.exists() and path.is_file()
    except Exception:
        return False


def _es_imagen(archivo: ArchivoSST) -> bool:
    mime = (archivo.mime_type or "").lower()
    ext = (archivo.extension or "").lower()
    return mime.startswith("image/") or ext in {"jpg", "jpeg", "png", "webp"}


def _es_pdf(archivo: ArchivoSST) -> bool:
    mime = (archivo.mime_type or "").lower()
    ext = (archivo.extension or "").lower()
    return mime == "application/pdf" or ext == "pdf"


def _item_auditoria(archivo: ArchivoSST) -> EvidenciaAuditoriaItem:
    existe_archivo = _archivo_existe(archivo.ruta) or _archivo_existe(archivo.url)
    es_imagen = _es_imagen(archivo)
    existe_preview = _variant_existe(archivo, "preview") if es_imagen else False
    existe_thumbnail = _variant_existe(archivo, "thumb") if es_imagen else False
    optimizada_webp = (archivo.extension or "").lower() == "webp" or (archivo.mime_type or "").lower() == "image/webp"

    hallazgos: list[str] = []

    if bool(archivo.activo) and not existe_archivo:
        hallazgos.append("Evidencia activa sin archivo físico localizable")

    if es_imagen and bool(archivo.activo):
        if not optimizada_webp:
            hallazgos.append("Imagen activa no optimizada a WEBP")
        if not existe_preview:
            hallazgos.append("Imagen activa sin preview")
        if not existe_thumbnail:
            hallazgos.append("Imagen activa sin miniatura")

    if not archivo.modulo:
        hallazgos.append("Evidencia sin módulo asociado")

    if archivo.referencia_id is None:
        hallazgos.append("Evidencia sin referencia_id")

    if not archivo.url:
        hallazgos.append("Evidencia sin URL pública")

    preview_url = None
    thumbnail_url = None
    if existe_preview:
        path = _variant_path_from_archivo(archivo, "preview")
        try:
            preview_url = "/uploads/" + path.resolve().relative_to(UPLOAD_ROOT).as_posix()
        except Exception:
            preview_url = None

    if existe_thumbnail:
        path = _variant_path_from_archivo(archivo, "thumb")
        try:
            thumbnail_url = "/uploads/" + path.resolve().relative_to(UPLOAD_ROOT).as_posix()
        except Exception:
            thumbnail_url = None

    return EvidenciaAuditoriaItem(
        id=archivo.id,
        empresa_id=archivo.empresa_id,
        usuario_id=archivo.usuario_id,
        tipo=archivo.tipo,
        modulo=archivo.modulo,
        referencia_id=archivo.referencia_id,
        nombre_original=archivo.nombre_original,
        nombre_archivo=archivo.nombre_archivo,
        url=archivo.url,
        preview_url=preview_url,
        thumbnail_url=thumbnail_url,
        extension=archivo.extension,
        mime_type=archivo.mime_type,
        tamano_bytes=archivo.tamano_bytes,
        activo=archivo.activo,
        fecha_creacion=archivo.fecha_creacion,
        existe_archivo=existe_archivo,
        existe_preview=existe_preview,
        existe_thumbnail=existe_thumbnail,
        optimizada_webp=optimizada_webp,
        hallazgos=hallazgos,
    )


@router.get("/health", response_model=EvidenciaHealthResponse)
def health_evidencias(
    usuario=Depends(require_roles(ROLES_AUDITORIA_EVIDENCIAS)),
):
    carpetas = {
        "root": UPLOAD_ROOT.exists(),
        "inspecciones": (UPLOAD_ROOT / "inspecciones").exists(),
        "inspecciones_previews": (UPLOAD_ROOT / "inspecciones" / "previews").exists(),
        "inspecciones_thumbs": (UPLOAD_ROOT / "inspecciones" / "thumbs").exists(),
        "capa": (UPLOAD_ROOT / "capa").exists(),
        "incidentes": (UPLOAD_ROOT / "incidentes").exists(),
        "evidencias": (UPLOAD_ROOT / "evidencias").exists(),
        "examenes_medicos": (UPLOAD_ROOT / "examenes-medicos").exists(),
    }

    ok = bool(carpetas["root"])
    return EvidenciaHealthResponse(
        ok=ok,
        mensaje="Directorio de evidencias disponible" if ok else "UPLOAD_DIR no existe o no es accesible",
        upload_root=str(UPLOAD_ROOT),
        carpetas=carpetas,
    )


@router.get("/", response_model=EvidenciaAuditoriaResponse)
def auditar_evidencias(
    empresa_id: int | None = Query(default=None),
    modulo: str | None = Query(default=None),
    solo_hallazgos: bool = Query(default=False),
    activo: bool | None = Query(default=True),
    limit: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_AUDITORIA_EVIDENCIAS)),
):
    query = db.query(ArchivoSST)

    if empresa_id:
        query = query.filter(ArchivoSST.empresa_id == empresa_id)

    if modulo:
        query = query.filter(func.upper(ArchivoSST.modulo) == modulo.upper().strip())

    if activo is not None:
        query = query.filter(ArchivoSST.activo.is_(activo))

    archivos = query.order_by(ArchivoSST.fecha_creacion.desc()).limit(limit).all()
    items = [_item_auditoria(archivo) for archivo in archivos]

    if solo_hallazgos:
        items = [item for item in items if item.hallazgos]

    resumen = EvidenciaAuditoriaResumen()
    resumen.total = len(items)
    resumen.activas = sum(1 for i in items if i.activo)
    resumen.inactivas = sum(1 for i in items if not i.activo)
    resumen.imagenes = sum(1 for i in items if str(i.mime_type or "").startswith("image/") or str(i.extension or "").lower() in {"jpg", "jpeg", "png", "webp"})
    resumen.pdfs = sum(1 for i in items if str(i.mime_type or "").lower() == "application/pdf" or str(i.extension or "").lower() == "pdf")
    resumen.otros = max(resumen.total - resumen.imagenes - resumen.pdfs, 0)
    resumen.webp = sum(1 for i in items if i.optimizada_webp)
    resumen.sin_archivo_fisico = sum(1 for i in items if i.activo and not i.existe_archivo)
    resumen.sin_preview = sum(1 for i in items if i.activo and str(i.mime_type or "").startswith("image/") and not i.existe_preview)
    resumen.sin_thumbnail = sum(1 for i in items if i.activo and str(i.mime_type or "").startswith("image/") and not i.existe_thumbnail)
    resumen.con_hallazgos = sum(1 for i in items if i.hallazgos)
    resumen.peso_total_mb = round(sum(int(i.tamano_bytes or 0) for i in items) / (1024 * 1024), 2)

    modulos: dict[str, int] = {}
    for item in items:
        key = item.modulo or "SIN_MODULO"
        modulos[key] = modulos.get(key, 0) + 1
    resumen.modulos = modulos

    recomendaciones: list[str] = []
    if resumen.sin_archivo_fisico:
        recomendaciones.append("Revisar evidencias activas sin archivo físico. Pueden ser registros huérfanos o rutas antiguas.")
    if resumen.sin_preview or resumen.sin_thumbnail:
        recomendaciones.append("Regenerar previews/miniaturas para imágenes antiguas o migradas.")
    if resumen.imagenes and resumen.webp < resumen.imagenes:
        recomendaciones.append("Normalizar imágenes antiguas a WEBP para reducir almacenamiento y mejorar carga.")
    if not recomendaciones:
        recomendaciones.append("Auditoría de evidencias sin hallazgos críticos.")

    return EvidenciaAuditoriaResponse(
        resumen=resumen,
        evidencias=items,
        recomendaciones=recomendaciones,
    )


@router.get("/modulos")
def modulos_evidencias(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_AUDITORIA_EVIDENCIAS)),
):
    rows = (
        db.query(ArchivoSST.modulo, func.count(ArchivoSST.id))
        .group_by(ArchivoSST.modulo)
        .order_by(func.count(ArchivoSST.id).desc())
        .all()
    )

    encontrados = [{"modulo": row[0] or "SIN_MODULO", "total": row[1]} for row in rows]

    return {
        "modulos_conocidos": MODULOS_CONOCIDOS,
        "modulos_encontrados": encontrados,
    }
