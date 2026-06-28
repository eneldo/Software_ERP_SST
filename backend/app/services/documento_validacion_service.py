# ============================================================
# SERVICE
# DOCUMENTOS VALIDACIÓN SST
# FASE 1.7.4.2.5
# ============================================================

import hashlib
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.documento_validacion import DocumentoValidacionSST


def calcular_hash_sha256(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def generar_codigo_validacion(tipo: str, referencia_id: int) -> str:
    fecha = datetime.now().strftime("%Y%m%d")
    token = uuid4().hex[:8].upper()
    return f"VAL-{tipo}-{referencia_id:06d}-{fecha}-{token}"


def registrar_documento_validacion(
    db: Session,
    tipo_documento: str,
    referencia_id: int,
    empresa_id: int | None,
    usuario_id: int | None,
    nombre_archivo: str,
    contenido_pdf: bytes,
    url_archivo: str | None = None,
    observacion: str | None = None,
):
    hash_sha256 = calcular_hash_sha256(contenido_pdf)

    codigo = generar_codigo_validacion(
        tipo=tipo_documento,
        referencia_id=referencia_id,
    )

    registro = DocumentoValidacionSST(
        codigo_validacion=codigo,
        tipo_documento=tipo_documento,
        referencia_id=referencia_id,
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        nombre_archivo=nombre_archivo,
        hash_sha256=hash_sha256,
        url_archivo=url_archivo,
        estado="VALIDO",
        observacion=observacion,
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro


def obtener_documento_por_codigo(
    db: Session,
    codigo_validacion: str,
):
    documento = (
        db.query(DocumentoValidacionSST)
        .filter(DocumentoValidacionSST.codigo_validacion == codigo_validacion)
        .first()
    )

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento de validación no encontrado",
        )

    return documento


def verificar_archivo_con_codigo(
    db: Session,
    codigo_validacion: str,
    contenido_archivo: bytes,
):
    documento = obtener_documento_por_codigo(db, codigo_validacion)

    hash_calculado = calcular_hash_sha256(contenido_archivo)

    return {
        "codigo_validacion": documento.codigo_validacion,
        "estado_documento": documento.estado,
        "hash_registrado": documento.hash_sha256,
        "hash_archivo_subido": hash_calculado,
        "coincide": hash_calculado == documento.hash_sha256,
    }