# ============================================================
# ROUTER EPP SST ENTERPRISE - ERP SST PRO
# FASE 1.1.7.1 — EPP SST BASE
# Archivo: backend/app/routers/epp.py
# ============================================================

from datetime import date, datetime, timedelta
from pathlib import Path
import base64
import io
import logging
import os
import uuid


from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_roles
from app.core.file_security import validate_upload
from app.database import get_db
from app.models.area import Area
from app.models.cargo import Cargo
from app.models.empleado import Empleado
from app.models.empresa import Empresa
from app.models.epp import EPPCatalogo, EPPEntrega
from app.models.archivo_sst import ArchivoSST
from app.models.sede import Sede
from app.schemas.epp_schema import (
    EPPDashboardResponse,
    EPPCatalogoCreate,
    EPPCatalogoResponse,
    EPPCatalogoUpdate,
    EPPEntregaCreate,
    EPPEntregaResponse,
    EPPEntregaUpdate,
    EPPEntregaLoteCreate,
    EPPEntregaLoteResponse,
    EPPConsolidadoEmpleado,
)

router = APIRouter(prefix="/epp", tags=["EPP SST Enterprise"])
ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]
logger = logging.getLogger("app.epp")


UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()
EPP_UPLOAD_DIR = UPLOAD_ROOT / "epp"
EPP_FIRMAS_DIR = UPLOAD_ROOT / "epp" / "firmas"
EPP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EPP_FIRMAS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EPP_EXT = {"pdf", "jpg", "jpeg", "png", "webp"}
ALLOWED_EPP_MIME = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
MAX_EPP_UPLOAD_MB = 20


def _public_upload_url(file_path: Path) -> str:
    try:
        rel = file_path.resolve().relative_to(UPLOAD_ROOT)
        return "/uploads/" + rel.as_posix()
    except Exception:
        return "/uploads/epp/" + file_path.name


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except Exception:
        return 0


def _optimizar_imagen_bytes(content: bytes, extension: str) -> tuple[bytes, str, str]:
    # Conversión inteligente a WEBP para reducir peso y eliminar metadatos.
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(content))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        max_side = 1600
        image.thumbnail((max_side, max_side))
        out = io.BytesIO()
        image.save(out, format="WEBP", quality=72, method=6, optimize=True)
        return out.getvalue(), "webp", "image/webp"
    except Exception:
        return content, extension.lower(), f"image/{'jpeg' if extension.lower() in ['jpg','jpeg'] else extension.lower()}"


def _optimizar_pdf_bytes(content: bytes) -> bytes:
    # Compresión best-effort. Si pikepdf está instalado, recomprime streams y guarda linealizado.
    try:
        import pikepdf
        src = io.BytesIO(content)
        out = io.BytesIO()
        with pikepdf.Pdf.open(src) as pdf:
            pdf.save(out, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate, linearize=True)
        optimized = out.getvalue()
        return optimized if len(optimized) < len(content) else content
    except Exception:
        return content


def _guardar_archivo_epp_upload(upload: UploadFile, subdir: Path) -> tuple[Path, str, str, str, int]:
    validation = validate_upload(upload, allowed_extensions={f".{item}" for item in ALLOWED_EPP_EXT}, max_size_mb=MAX_EPP_UPLOAD_MB)
    original = validation.safe_filename or "evidencia_epp"
    extension = validation.extension.lstrip(".")
    content = validation.content
    mime_type = validation.mime_type

    if extension in {"jpg", "jpeg", "png", "webp"}:
        content, extension, mime_type = _optimizar_imagen_bytes(content, extension)
    elif extension == "pdf":
        content = _optimizar_pdf_bytes(content)
        mime_type = "application/pdf"

    subdir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{extension}"
    path = subdir / filename
    path.write_bytes(content)
    return path, original, filename, mime_type, len(content)

def _guardar_firma_base64(data_url: str) -> tuple[Path, str, str, str, int]:
    if not data_url or "," not in data_url:
        raise HTTPException(status_code=400, detail="Firma inválida")
    header, payload = data_url.split(",", 1)
    try:
        content = base64.b64decode(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo procesar la firma")

    content, extension, mime_type = _optimizar_imagen_bytes(content, "png")
    filename = f"firma_epp_{uuid.uuid4().hex}.{extension}"
    path = EPP_FIRMAS_DIR / filename
    path.write_bytes(content)
    return path, "firma_epp.png", filename, mime_type, len(content)


def _archivo_to_dict(archivo: ArchivoSST):
    return {
        "id": archivo.id,
        "empresa_id": archivo.empresa_id,
        "usuario_id": archivo.usuario_id,
        "tipo": archivo.tipo,
        "nombre_original": archivo.nombre_original,
        "nombre_archivo": archivo.nombre_archivo,
        "ruta": archivo.ruta,
        "url": archivo.url,
        "extension": archivo.extension,
        "mime_type": archivo.mime_type,
        "tamano_bytes": archivo.tamano_bytes,
        "modulo": archivo.modulo,
        "referencia_id": archivo.referencia_id,
        "descripcion": archivo.descripcion,
        "activo": archivo.activo,
        "fecha_creacion": archivo.fecha_creacion,
    }


# ============================================================
# Helpers
# ============================================================
def _limpiar_texto(valor):
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor if valor else None


def _upper(valor, default=None):
    valor = _limpiar_texto(valor)
    return valor.upper() if valor else default


def _calcular_estado(fecha_reposicion, estado_actual="ENTREGADO"):
    estado_actual = _upper(estado_actual, "ENTREGADO")
    if estado_actual in ["REEMPLAZADO", "DEVUELTO", "ANULADO"]:
        return estado_actual
    if not fecha_reposicion:
        return "VIGENTE" if estado_actual == "ENTREGADO" else estado_actual
    hoy = date.today()
    if fecha_reposicion < hoy:
        return "VENCIDO"
    if fecha_reposicion <= hoy + timedelta(days=30):
        return "PROXIMO_REPOSICION"
    return "VIGENTE"


def _dias_reposicion(fecha_reposicion):
    if not fecha_reposicion:
        return None
    return (fecha_reposicion - date.today()).days


def _catalogo_to_response(item: EPPCatalogo):
    data = EPPCatalogoResponse.model_validate(item)
    data.empresa_nombre = item.empresa.nombre if item.empresa else None
    return data


def _entrega_to_response(item: EPPEntrega):
    data = EPPEntregaResponse.model_validate(item)
    data.empresa_nombre = item.empresa.nombre if item.empresa else None
    data.dias_reposicion = _dias_reposicion(item.fecha_reposicion)

    if item.epp:
        data.epp_codigo = item.epp.codigo
        data.epp_nombre = item.epp.nombre
        data.epp_categoria = item.epp.categoria
        data.vida_util_dias = item.epp.vida_util_dias

    if item.empleado:
        emp = item.empleado
        data.empleado_documento = emp.documento
        data.empleado_nombre = f"{emp.nombres} {emp.apellidos}".strip()
        data.empleado_correo = emp.correo
        data.sede_id = emp.sede_id
        data.area_id = emp.area_id
        data.cargo_id = emp.cargo_id
        data.sede_nombre = emp.sede.nombre if emp.sede else None
        data.area_nombre = emp.area.nombre if emp.area else None
        data.cargo_nombre = emp.cargo.nombre if emp.cargo else None
    return data


def _validar_empresa(db: Session, empresa_id: int):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa


def _validar_catalogo(db: Session, epp_id: int):
    epp = db.query(EPPCatalogo).filter(EPPCatalogo.id == epp_id).first()
    if not epp:
        raise HTTPException(status_code=404, detail="Elemento EPP no encontrado")
    return epp


def _validar_empleado(db: Session, empleado_id: int):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


def _query_entregas(
    db: Session,
    empresa_id=None,
    sede_id=None,
    area_id=None,
    cargo_id=None,
    empleado_id=None,
    epp_id=None,
    estado=None,
    q=None,
):
    query = (
        db.query(EPPEntrega)
        .options(
            joinedload(EPPEntrega.empresa),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.sede),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.area),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.cargo),
            joinedload(EPPEntrega.epp),
        )
        .join(Empleado, EPPEntrega.empleado_id == Empleado.id)
        .join(EPPCatalogo, EPPEntrega.epp_id == EPPCatalogo.id)
    )

    if empresa_id:
        query = query.filter(EPPEntrega.empresa_id == empresa_id)
    if sede_id:
        query = query.filter(Empleado.sede_id == sede_id)
    if area_id:
        query = query.filter(Empleado.area_id == area_id)
    if cargo_id:
        query = query.filter(Empleado.cargo_id == cargo_id)
    if empleado_id:
        query = query.filter(EPPEntrega.empleado_id == empleado_id)
    if epp_id:
        query = query.filter(EPPEntrega.epp_id == epp_id)
    if estado:
        query = query.filter(func.upper(EPPEntrega.estado) == estado.upper().strip())
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Empleado.nombres.ilike(like),
                Empleado.apellidos.ilike(like),
                Empleado.documento.ilike(like),
                EPPCatalogo.codigo.ilike(like),
                EPPCatalogo.nombre.ilike(like),
                EPPEntrega.marca.ilike(like),
                EPPEntrega.serial.ilike(like),
            )
        )
    return query.order_by(EPPEntrega.id.desc())


# ============================================================
# Catálogo EPP
# ============================================================
@router.get("/catalogo", response_model=list[EPPCatalogoResponse])
def listar_catalogo(
    empresa_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = db.query(EPPCatalogo).options(joinedload(EPPCatalogo.empresa))
    if empresa_id:
        query = query.filter(EPPCatalogo.empresa_id == empresa_id)
    if estado:
        query = query.filter(func.upper(EPPCatalogo.estado) == estado.upper().strip())
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(EPPCatalogo.codigo.ilike(like), EPPCatalogo.nombre.ilike(like), EPPCatalogo.categoria.ilike(like))
        )
    items = query.order_by(EPPCatalogo.nombre.asc()).all()
    return [_catalogo_to_response(item) for item in items]


@router.post("/catalogo", response_model=EPPCatalogoResponse)
def crear_catalogo(
    data: EPPCatalogoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    _validar_empresa(db, data.empresa_id)
    existe = (
        db.query(EPPCatalogo)
        .filter(EPPCatalogo.empresa_id == data.empresa_id, func.upper(EPPCatalogo.codigo) == data.codigo.upper())
        .first()
    )
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un EPP con ese código para la empresa")
    item = EPPCatalogo(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _catalogo_to_response(item)


@router.put("/catalogo/{catalogo_id}", response_model=EPPCatalogoResponse)
def actualizar_catalogo(
    catalogo_id: int,
    data: EPPCatalogoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EPPCatalogo).filter(EPPCatalogo.id == catalogo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Elemento EPP no encontrado")
    payload = data.model_dump(exclude_unset=True)
    if payload.get("empresa_id"):
        _validar_empresa(db, payload["empresa_id"])
    for key, value in payload.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _catalogo_to_response(item)


@router.delete("/catalogo/{catalogo_id}")
def eliminar_catalogo(
    catalogo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EPPCatalogo).filter(EPPCatalogo.id == catalogo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Elemento EPP no encontrado")
    item.activo = False
    item.estado = "INACTIVO"
    db.commit()
    return {"ok": True, "message": "Elemento EPP desactivado"}


# ============================================================
# Ficha Técnica EPP
# ============================================================
@router.post("/catalogo/{catalogo_id}/ficha-tecnica")
def subir_ficha_tecnica(
    catalogo_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EPPCatalogo).filter(EPPCatalogo.id == catalogo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Elemento EPP no encontrado")

    path, original, filename, mime_type, size = _guardar_archivo_epp_upload(archivo, EPP_UPLOAD_DIR)
    extension = filename.rsplit(".", 1)[-1].lower()

    registro = ArchivoSST(
        empresa_id=item.empresa_id,
        usuario_id=getattr(usuario, "id", None),
        tipo="FICHA_TECNICA",
        nombre_original=original,
        nombre_archivo=filename,
        ruta=str(path),
        url=_public_upload_url(path),
        extension=extension,
        mime_type=mime_type,
        tamano_bytes=size,
        modulo="EPP",
        referencia_id=item.id,
        descripcion=f"Ficha técnica de {item.nombre}",
        activo=True,
    )
    db.add(registro)
    db.flush()

    item.ficha_tecnica_url = registro.url
    item.ficha_tecnica_nombre = original
    item.ficha_tecnica_archivo_id = registro.id
    db.commit()
    db.refresh(item)

    return {
        "ok": True,
        "message": "Ficha técnica cargada correctamente",
        "ficha_tecnica_url": registro.url,
        "ficha_tecnica_nombre": original,
        "ficha_tecnica_archivo_id": registro.id,
    }


@router.delete("/catalogo/{catalogo_id}/ficha-tecnica")
def eliminar_ficha_tecnica(
    catalogo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EPPCatalogo).filter(EPPCatalogo.id == catalogo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Elemento EPP no encontrado")

    if item.ficha_tecnica_archivo_id:
        archivo = db.query(ArchivoSST).filter(ArchivoSST.id == item.ficha_tecnica_archivo_id).first()
        if archivo:
            archivo.activo = False

    item.ficha_tecnica_url = None
    item.ficha_tecnica_nombre = None
    item.ficha_tecnica_archivo_id = None
    db.commit()

    return {"ok": True, "message": "Ficha técnica eliminada"}


# ============================================================
# Entregas EPP
# ============================================================
@router.get("/entregas", response_model=list[EPPEntregaResponse])
def listar_entregas(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    cargo_id: int | None = Query(default=None),
    empleado_id: int | None = Query(default=None),
    epp_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    items = _query_entregas(db, empresa_id, sede_id, area_id, cargo_id, empleado_id, epp_id, estado, q).all()
    return [_entrega_to_response(item) for item in items]


@router.post("/entregas/lote", response_model=EPPEntregaLoteResponse)
def crear_entregas_lote(
    data: EPPEntregaLoteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    _validar_empresa(db, data.empresa_id)
    empleado = _validar_empleado(db, data.empleado_id)
    if empleado.empresa_id != data.empresa_id:
        raise HTTPException(status_code=400, detail="El empleado no pertenece a la empresa seleccionada")

    entregas_creadas = []
    for item_data in data.items:
        epp = _validar_catalogo(db, item_data.epp_id)
        if epp.empresa_id != data.empresa_id:
            raise HTTPException(status_code=400, detail=f"El EPP '{epp.nombre}' no pertenece a la empresa seleccionada")

        payload = {
            "empresa_id": data.empresa_id,
            "empleado_id": data.empleado_id,
            "epp_id": item_data.epp_id,
            "cantidad": item_data.cantidad,
            "fecha_entrega": data.fecha_entrega,
            "talla": item_data.talla,
            "marca": item_data.marca,
            "modelo": item_data.modelo,
            "serial": item_data.serial,
            "observaciones": item_data.observaciones,
            "estado": "ENTREGADO",
        }

        if epp.requiere_reposicion and epp.vida_util_dias:
            payload["fecha_reposicion"] = data.fecha_entrega + timedelta(days=epp.vida_util_dias)

        payload["estado"] = _calcular_estado(payload.get("fecha_reposicion"), payload.get("estado"))
        entrega = EPPEntrega(**payload)
        db.add(entrega)
        db.flush()
        entregas_creadas.append(entrega)

    db.commit()

    detalles = []
    for e in entregas_creadas:
        db.refresh(e)
        detalles.append(obtener_entrega(e.id, db, usuario))

    return EPPEntregaLoteResponse(
        entregas_creadas=len(detalles),
        empleado_nombre=f"{empleado.nombres} {empleado.apellidos}".strip(),
        fecha_entrega=data.fecha_entrega,
        detalles=detalles,
    )


@router.get("/entregas/consolidado", response_model=list[EPPConsolidadoEmpleado])
def consolidado_entregas(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    from app.models.empleado import Empleado

    query = (
        db.query(Empleado)
        .options(
            joinedload(Empleado.empresa),
            joinedload(Empleado.sede),
            joinedload(Empleado.area),
            joinedload(Empleado.cargo),
        )
        .filter(Empleado.activo.is_(True))
    )
    if empresa_id:
        query = query.filter(Empleado.empresa_id == empresa_id)

    empleados = query.order_by(Empleado.nombres.asc()).all()
    resultado = []

    for emp in empleados:
        entregas = (
            db.query(EPPEntrega)
            .options(joinedload(EPPEntrega.epp))
            .filter(
                EPPEntrega.empleado_id == emp.id,
                EPPEntrega.activo.is_(True),
            )
            .order_by(EPPEntrega.fecha_entrega.desc())
            .all()
        )

        if not entregas:
            continue

        epp_lista = []
        for ent in entregas:
            epp_lista.append({
                "entrega_id": ent.id,
                "epp_codigo": ent.epp.codigo if ent.epp else None,
                "epp_nombre": ent.epp.nombre if ent.epp else None,
                "epp_categoria": ent.epp.categoria if ent.epp else None,
                "cantidad": ent.cantidad,
                "talla": ent.talla,
                "marca": ent.marca,
                "modelo": ent.modelo,
                "serial": ent.serial,
                "fecha_entrega": str(ent.fecha_entrega) if ent.fecha_entrega else None,
                "fecha_reposicion": str(ent.fecha_reposicion) if ent.fecha_reposicion else None,
                "estado": ent.estado,
                "recibido": ent.recibido_por_empleado,
            })

        resultado.append(EPPConsolidadoEmpleado(
            empleado_id=emp.id,
            empleado_documento=emp.documento,
            empleado_nombre=f"{emp.nombres} {emp.apellidos}".strip(),
            empresa_nombre=emp.empresa.nombre if emp.empresa else None,
            sede_nombre=emp.sede.nombre if emp.sede else None,
            area_nombre=emp.area.nombre if emp.area else None,
            cargo_nombre=emp.cargo.nombre if emp.cargo else None,
            total_epp=len(epp_lista),
            epp_entregados=epp_lista,
        ))

    return resultado


@router.get("/entregas/{entrega_id}", response_model=EPPEntregaResponse)
def obtener_entrega(
    entrega_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = (
        db.query(EPPEntrega)
        .options(
            joinedload(EPPEntrega.empresa),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.sede),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.area),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.cargo),
            joinedload(EPPEntrega.epp),
        )
        .filter(EPPEntrega.id == entrega_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")
    return _entrega_to_response(item)


@router.post("/entregas", response_model=EPPEntregaResponse)
def crear_entrega(
    data: EPPEntregaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    _validar_empresa(db, data.empresa_id)
    empleado = _validar_empleado(db, data.empleado_id)
    epp = _validar_catalogo(db, data.epp_id)
    if empleado.empresa_id != data.empresa_id:
        raise HTTPException(status_code=400, detail="El empleado no pertenece a la empresa seleccionada")
    if epp.empresa_id != data.empresa_id:
        raise HTTPException(status_code=400, detail="El EPP no pertenece a la empresa seleccionada")

    payload = data.model_dump()
    if not payload.get("fecha_reposicion") and epp.requiere_reposicion and epp.vida_util_dias:
        payload["fecha_reposicion"] = payload["fecha_entrega"] + timedelta(days=epp.vida_util_dias)
    payload["estado"] = _calcular_estado(payload.get("fecha_reposicion"), payload.get("estado"))
    item = EPPEntrega(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return obtener_entrega(item.id, db, usuario)


@router.put("/entregas/{entrega_id}", response_model=EPPEntregaResponse)
def actualizar_entrega(
    entrega_id: int,
    data: EPPEntregaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EPPEntrega).filter(EPPEntrega.id == entrega_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")
    payload = data.model_dump(exclude_unset=True)

    empresa_id = payload.get("empresa_id", item.empresa_id)
    empleado_id = payload.get("empleado_id", item.empleado_id)
    epp_id = payload.get("epp_id", item.epp_id)
    _validar_empresa(db, empresa_id)
    empleado = _validar_empleado(db, empleado_id)
    epp = _validar_catalogo(db, epp_id)
    if empleado.empresa_id != empresa_id:
        raise HTTPException(status_code=400, detail="El empleado no pertenece a la empresa seleccionada")
    if epp.empresa_id != empresa_id:
        raise HTTPException(status_code=400, detail="El EPP no pertenece a la empresa seleccionada")

    for key, value in payload.items():
        setattr(item, key, value)
    if "fecha_reposicion" in payload or "estado" in payload:
        item.estado = _calcular_estado(item.fecha_reposicion, item.estado)
    db.commit()
    db.refresh(item)
    return obtener_entrega(item.id, db, usuario)


@router.patch("/entregas/{entrega_id}/recibido", response_model=EPPEntregaResponse)
def marcar_recibido(
    entrega_id: int,
    recibido: bool = Query(default=True),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EPPEntrega).filter(EPPEntrega.id == entrega_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")
    item.recibido_por_empleado = recibido
    item.fecha_firma = datetime.now() if recibido else None
    db.commit()
    db.refresh(item)
    return obtener_entrega(item.id, db, usuario)


@router.delete("/entregas/{entrega_id}")
def eliminar_entrega(
    entrega_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = db.query(EPPEntrega).filter(EPPEntrega.id == entrega_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")
    item.activo = False
    item.estado = "ANULADO"
    db.commit()
    return {"ok": True, "message": "Entrega EPP anulada"}




# ============================================================
# Evidencias y Firma EPP Enterprise
# Reutiliza archivos_sst con modulo='EPP' y referencia_id=entrega_id
# Incluye compresión inteligente de imágenes y compresión best-effort PDF
# ============================================================
@router.get("/entregas/{entrega_id}/evidencias")
def listar_evidencias_entrega(
    entrega_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    entrega = db.query(EPPEntrega).filter(EPPEntrega.id == entrega_id).first()
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")
    archivos = (
        db.query(ArchivoSST)
        .filter(
            ArchivoSST.modulo == "EPP",
            ArchivoSST.referencia_id == entrega_id,
            ArchivoSST.activo.is_(True),
        )
        .order_by(ArchivoSST.fecha_creacion.desc())
        .all()
    )
    return [_archivo_to_dict(a) for a in archivos]


@router.post("/entregas/{entrega_id}/evidencias")
def subir_evidencia_entrega(
    entrega_id: int,
    tipo_evidencia: str = Form(default="SOPORTE"),
    descripcion: str = Form(default=""),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    entrega = db.query(EPPEntrega).filter(EPPEntrega.id == entrega_id).first()
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")

    path, original, filename, mime_type, size = _guardar_archivo_epp_upload(archivo, EPP_UPLOAD_DIR)
    extension = filename.rsplit(".", 1)[-1].lower()
    tipo = (tipo_evidencia or "SOPORTE").upper().strip()

    registro = ArchivoSST(
        empresa_id=entrega.empresa_id,
        usuario_id=getattr(usuario, "id", None),
        tipo=tipo,
        nombre_original=original,
        nombre_archivo=filename,
        ruta=str(path),
        url=_public_upload_url(path),
        extension=extension,
        mime_type=mime_type,
        tamano_bytes=size,
        modulo="EPP",
        referencia_id=entrega.id,
        descripcion=descripcion or tipo.replace("_", " ").title(),
        activo=True,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return _archivo_to_dict(registro)


@router.delete("/entregas/{entrega_id}/evidencias/{archivo_id}")
def eliminar_evidencia_entrega(
    entrega_id: int,
    archivo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    archivo = (
        db.query(ArchivoSST)
        .filter(
            ArchivoSST.id == archivo_id,
            ArchivoSST.modulo == "EPP",
            ArchivoSST.referencia_id == entrega_id,
        )
        .first()
    )
    if not archivo:
        raise HTTPException(status_code=404, detail="Evidencia EPP no encontrada")
    archivo.activo = False
    db.commit()
    return {"ok": True, "message": "Evidencia desactivada"}


@router.post("/entregas/{entrega_id}/firma", response_model=EPPEntregaResponse)
def firmar_entrega_epp(
    entrega_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    entrega = db.query(EPPEntrega).filter(EPPEntrega.id == entrega_id).first()
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")

    firma_base64 = payload.get("firma_base64") or payload.get("firma")
    nombre_firmante = payload.get("nombre_firmante") or "Empleado"
    descripcion = payload.get("descripcion") or f"Firma de recibido EPP - {nombre_firmante}"

    path, original, filename, mime_type, size = _guardar_firma_base64(firma_base64)
    registro = ArchivoSST(
        empresa_id=entrega.empresa_id,
        usuario_id=getattr(usuario, "id", None),
        tipo="FIRMA_EMPLEADO",
        nombre_original=original,
        nombre_archivo=filename,
        ruta=str(path),
        url=_public_upload_url(path),
        extension=filename.rsplit(".", 1)[-1].lower(),
        mime_type=mime_type,
        tamano_bytes=size,
        modulo="EPP",
        referencia_id=entrega.id,
        descripcion=descripcion,
        activo=True,
    )
    entrega.recibido_por_empleado = True
    entrega.fecha_firma = datetime.now()
    db.add(registro)
    db.commit()
    db.refresh(entrega)
    return obtener_entrega(entrega.id, db, usuario)


# ============================================================
# Dashboard Analytics y Alertas EPP
# FASE 1.1.7.3 — Analytics y Alertas EPP
# ============================================================
@router.get("/dashboard", response_model=EPPDashboardResponse)
def dashboard_epp(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    cargo_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    entregas = _query_entregas(db, empresa_id, sede_id, area_id, cargo_id).all()

    catalogo_query = db.query(EPPCatalogo).filter(EPPCatalogo.activo.is_(True))
    empleados_query = db.query(Empleado).filter(Empleado.activo.is_(True))

    if empresa_id:
        catalogo_query = catalogo_query.filter(EPPCatalogo.empresa_id == empresa_id)
        empleados_query = empleados_query.filter(Empleado.empresa_id == empresa_id)
    if sede_id:
        empleados_query = empleados_query.filter(Empleado.sede_id == sede_id)
    if area_id:
        empleados_query = empleados_query.filter(Empleado.area_id == area_id)
    if cargo_id:
        empleados_query = empleados_query.filter(Empleado.cargo_id == cargo_id)

    hoy = date.today()
    en_7 = hoy + timedelta(days=7)
    en_15 = hoy + timedelta(days=15)
    en_30 = hoy + timedelta(days=30)

    entregas_activas = [x for x in entregas if x.activo]
    entrega_ids = [x.id for x in entregas_activas]

    evidencias_por_entrega: dict[int, int] = {}
    if entrega_ids:
        evid_rows = (
            db.query(ArchivoSST.referencia_id, func.count(ArchivoSST.id))
            .filter(
                ArchivoSST.modulo == "EPP",
                ArchivoSST.activo.is_(True),
                ArchivoSST.referencia_id.in_(entrega_ids),
            )
            .group_by(ArchivoSST.referencia_id)
            .all()
        )
        evidencias_por_entrega = {int(ref): int(total) for ref, total in evid_rows if ref is not None}

    total = len(entregas_activas)
    vigentes = sum(1 for x in entregas_activas if x.estado in ["ENTREGADO", "VIGENTE"])
    proximos = sum(1 for x in entregas_activas if x.estado == "PROXIMO_REPOSICION")
    vencidos = sum(1 for x in entregas_activas if x.estado == "VENCIDO")
    firmados = sum(1 for x in entregas_activas if x.recibido_por_empleado)
    sin_firma = max(total - firmados, 0)

    vencen_7 = sum(1 for x in entregas_activas if x.fecha_reposicion and hoy <= x.fecha_reposicion <= en_7)
    vencen_15 = sum(1 for x in entregas_activas if x.fecha_reposicion and hoy <= x.fecha_reposicion <= en_15)
    vencen_30 = sum(1 for x in entregas_activas if x.fecha_reposicion and hoy <= x.fecha_reposicion <= en_30)

    entregas_con_evidencia = len([x for x in entregas_activas if evidencias_por_entrega.get(x.id, 0) > 0])
    entregas_sin_evidencia = max(total - entregas_con_evidencia, 0)
    entregas_completas = len([
        x for x in entregas_activas
        if x.recibido_por_empleado and evidencias_por_entrega.get(x.id, 0) > 0 and x.estado not in ["VENCIDO", "ANULADO"]
    ])

    catalogo_total = catalogo_query.count()
    empleados_total = empleados_query.count()
    empleados_con_epp = len({x.empleado_id for x in entregas_activas})
    empleados_sin_epp = max(empleados_total - empleados_con_epp, 0)

    cumplimiento_firma = round((firmados / total) * 100, 1) if total else 0
    cumplimiento_evidencia = round((entregas_con_evidencia / total) * 100, 1) if total else 0
    cumplimiento_integral = round((entregas_completas / total) * 100, 1) if total else 0
    cobertura = round((empleados_con_epp / empleados_total) * 100, 1) if empleados_total else 0

    riesgo_score = 0
    riesgo_score += 40 if vencidos else 0
    riesgo_score += 25 if empleados_sin_epp else 0
    riesgo_score += 15 if sin_firma else 0
    riesgo_score += 10 if entregas_sin_evidencia else 0
    riesgo_score += 10 if vencen_30 else 0
    if riesgo_score >= 60:
        riesgo_epp = "ALTO"
        semaforo = "ROJO"
    elif riesgo_score >= 25:
        riesgo_epp = "MEDIO"
        semaforo = "AMARILLO"
    else:
        riesgo_epp = "BAJO"
        semaforo = "VERDE"

    def conteo_por(attr):
        data = {}
        for item in entregas_activas:
            value = attr(item) or "Sin dato"
            data[value] = data.get(value, 0) + 1
        return [{"name": k, "value": v} for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)[:8]]

    def conteo_reposicion():
        data = {
            "Vencen 7 días": vencen_7,
            "Vencen 15 días": max(vencen_15 - vencen_7, 0),
            "Vencen 30 días": max(vencen_30 - vencen_15, 0),
            "Vencidos": vencidos,
        }
        return [{"name": k, "value": v} for k, v in data.items() if v > 0] or [{"name": "Sin pendientes", "value": 0}]

    def conteo_evidencias():
        return [
            {"name": "Con evidencia", "value": entregas_con_evidencia},
            {"name": "Sin evidencia", "value": entregas_sin_evidencia},
        ]

    recomendaciones = []
    if empleados_sin_epp > 0:
        recomendaciones.append("Asignar EPP a empleados sin entregas registradas.")
    if vencidos > 0:
        recomendaciones.append("Gestionar reposición inmediata de EPP vencidos.")
    if vencen_30 > 0:
        recomendaciones.append("Programar reposición preventiva de EPP que vencen en los próximos 30 días.")
    if sin_firma > 0:
        recomendaciones.append("Regularizar firmas pendientes para garantizar trazabilidad legal de recibido.")
    if entregas_sin_evidencia > 0:
        recomendaciones.append("Adjuntar evidencia o acta de entrega para fortalecer soporte documental SST.")
    if not recomendaciones:
        recomendaciones.append("Gestión EPP estable. Mantén seguimiento periódico y auditoría documental.")

    return {
        "kpis": {
            "total_entregas": total,
            "vigentes": vigentes,
            "proximos_reposicion": proximos,
            "vencidos": vencidos,
            "firmados": firmados,
            "catalogo": catalogo_total,
            "empleados_total": empleados_total,
            "empleados_con_epp": empleados_con_epp,
            "empleados_sin_epp": empleados_sin_epp,
            "entregas_con_evidencia": entregas_con_evidencia,
            "entregas_sin_evidencia": entregas_sin_evidencia,
            "entregas_completas": entregas_completas,
            "cumplimiento_firma": cumplimiento_firma,
            "cumplimiento_evidencia": cumplimiento_evidencia,
            "cumplimiento_integral": cumplimiento_integral,
            "cobertura": cobertura,
            "riesgo_score": riesgo_score,
            "riesgo_epp": riesgo_epp,
            "semaforo": semaforo,
            "vencen_7_dias": vencen_7,
            "vencen_15_dias": vencen_15,
            "vencen_30_dias": vencen_30,
        },
        "charts": {
            "por_epp": conteo_por(lambda x: x.epp.nombre if x.epp else None),
            "por_categoria": conteo_por(lambda x: x.epp.categoria if x.epp else None),
            "por_estado": conteo_por(lambda x: x.estado),
            "por_area": conteo_por(lambda x: x.empleado.area.nombre if x.empleado and x.empleado.area else "Sin área"),
            "por_cargo": conteo_por(lambda x: x.empleado.cargo.nombre if x.empleado and x.empleado.cargo else "Sin cargo"),
            "por_reposicion": conteo_reposicion(),
            "por_evidencia": conteo_evidencias(),
        },
        "alertas": {
            "vencen_7_dias": vencen_7,
            "vencen_15_dias": vencen_15,
            "vencen_30_dias": vencen_30,
            "proximos_reposicion": proximos,
            "vencidos": vencidos,
            "empleados_sin_epp": empleados_sin_epp,
            "sin_firma": sin_firma,
            "sin_evidencia": entregas_sin_evidencia,
        },
        "recomendaciones": recomendaciones,
    }


# ============================================================
# Exportación PDF / Excel EPP
# FASE 1.1.7.4 — Exportación PDF / Excel EPP SST Enterprise
# ============================================================

def _safe_text(value):
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _entrega_export_rows(items: list[EPPEntrega]):
    rows = []
    for item in items:
        empleado = item.empleado
        epp = item.epp
        rows.append({
            "ID": item.id,
            "Empleado": f"{empleado.nombres} {empleado.apellidos}".strip() if empleado else "",
            "Documento": empleado.documento if empleado else "",
            "Empresa": item.empresa.nombre if item.empresa else "",
            "Sede": empleado.sede.nombre if empleado and empleado.sede else "",
            "Área": empleado.area.nombre if empleado and empleado.area else "",
            "Cargo": empleado.cargo.nombre if empleado and empleado.cargo else "",
            "Código EPP": epp.codigo if epp else "",
            "EPP": epp.nombre if epp else "",
            "Categoría": epp.categoria if epp else "",
            "Cantidad": item.cantidad,
            "Talla": item.talla,
            "Marca": item.marca,
            "Modelo": item.modelo,
            "Serial": item.serial,
            "Fecha entrega": item.fecha_entrega,
            "Fecha reposición": item.fecha_reposicion,
            "Días reposición": _dias_reposicion(item.fecha_reposicion),
            "Estado": item.estado,
            "Firmado": "Sí" if item.recibido_por_empleado else "No",
            "Fecha firma": item.fecha_firma,
            "Observaciones": item.observaciones,
        })
    return rows


def _catalogo_export_rows(items: list[EPPCatalogo]):
    rows = []
    for item in items:
        rows.append({
            "ID": item.id,
            "Empresa": item.empresa.nombre if item.empresa else "",
            "Código": item.codigo,
            "Nombre": item.nombre,
            "Categoría": item.categoria,
            "Descripción": item.descripcion,
            "Vida útil días": item.vida_util_dias,
            "Requiere reposición": "Sí" if item.requiere_reposicion else "No",
            "Requiere firma": "Sí" if item.requiere_firma else "No",
            "Requiere evidencia": "Sí" if item.requiere_evidencia else "No",
            "Estado": item.estado,
            "Activo": "Sí" if item.activo else "No",
        })
    return rows


def _excel_response(rows: list[dict], filename: str, sheet_name: str = "Datos"):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except Exception as exc:
        logger.exception("Dependencia Excel no disponible para exportacion EPP")
        raise HTTPException(status_code=500, detail="No fue posible generar el Excel.") from exc

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]

    if not rows:
        rows = [{"Mensaje": "Sin registros para exportar"}]

    headers = list(rows[0].keys())
    ws.append(headers)

    header_fill = PatternFill("solid", fgColor="10265D")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin", color="D9E2F3")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = Border(bottom=thin)

    for row in rows:
        ws.append([_safe_text(row.get(header)) for header in headers])

    for idx, header in enumerate(headers, start=1):
        max_len = max([len(str(header))] + [len(_safe_text(row.get(header))) for row in rows])
        ws.column_dimensions[get_column_letter(idx)].width = min(max(max_len + 3, 12), 42)

    ws.freeze_panes = "A2"
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _pdf_response(title: str, rows: list[dict], filename: str, subtitle: str = ""):
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except Exception as exc:
        logger.exception("Dependencia PDF no disponible para exportacion EPP")
        raise HTTPException(status_code=500, detail="No fue posible generar el PDF.") from exc

    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(letter),
        rightMargin=0.8 * cm,
        leftMargin=0.8 * cm,
        topMargin=0.8 * cm,
        bottomMargin=0.8 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "EPPTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        textColor=colors.HexColor("#10265D"),
        spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "EPPSub",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )

    story = [
        Paragraph(title, title_style),
        Paragraph(subtitle or f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style),
        Spacer(1, 8),
    ]

    if not rows:
        story.append(Paragraph("Sin registros para exportar.", styles["Normal"]))
    else:
        # Reducir columnas para PDFs de listado general.
        headers = list(rows[0].keys())
        table_data = [headers]
        for row in rows:
            table_data.append([_safe_text(row.get(h))[:58] for h in headers])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10265D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)

    doc.build(story)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _pdf_ficha_entrega(item: EPPEntrega):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except Exception as exc:
        logger.exception("Dependencia PDF no disponible para exportacion EPP")
        raise HTTPException(status_code=500, detail="No fue posible generar el PDF.") from exc

    empleado = item.empleado
    epp = item.epp
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleEPP", parent=styles["Title"], fontSize=17, textColor=colors.HexColor("#10265D"), spaceAfter=10)

    story = [
        Paragraph("Ficha Individual de Entrega EPP", title_style),
        Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 12),
    ]

    data = [
        ["Empleado", f"{empleado.nombres} {empleado.apellidos}".strip() if empleado else ""],
        ["Documento", empleado.documento if empleado else ""],
        ["Empresa", item.empresa.nombre if item.empresa else ""],
        ["Sede", empleado.sede.nombre if empleado and empleado.sede else ""],
        ["Área", empleado.area.nombre if empleado and empleado.area else ""],
        ["Cargo", empleado.cargo.nombre if empleado and empleado.cargo else ""],
        ["EPP", epp.nombre if epp else ""],
        ["Código EPP", epp.codigo if epp else ""],
        ["Categoría", epp.categoria if epp else ""],
        ["Cantidad", _safe_text(item.cantidad)],
        ["Talla", _safe_text(item.talla)],
        ["Marca / Modelo / Serial", f"{_safe_text(item.marca)} / {_safe_text(item.modelo)} / {_safe_text(item.serial)}"],
        ["Fecha entrega", _safe_text(item.fecha_entrega)],
        ["Fecha reposición", _safe_text(item.fecha_reposicion)],
        ["Estado", _safe_text(item.estado)],
        ["Firmado", "Sí" if item.recibido_por_empleado else "No"],
        ["Fecha firma", _safe_text(item.fecha_firma)],
        ["Observaciones", _safe_text(item.observaciones)],
    ]

    table = Table(data, colWidths=[4.3 * cm, 12.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF4FF")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#10265D")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(table)
    story.append(Spacer(1, 24))
    story.append(Paragraph("Firma trabajador: __________________________________________", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Responsable SST: __________________________________________", styles["Normal"]))

    doc.build(story)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ficha_entrega_epp_{item.id}.pdf"'},
    )


def _get_filtered_entregas_for_export(
    db: Session,
    empresa_id=None,
    sede_id=None,
    area_id=None,
    cargo_id=None,
    empleado_id=None,
    epp_id=None,
    estado=None,
    q=None,
):
    return _query_entregas(db, empresa_id, sede_id, area_id, cargo_id, empleado_id, epp_id, estado, q).all()


@router.get("/export/catalogo/excel")
def exportar_catalogo_epp_excel(
    empresa_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = db.query(EPPCatalogo).options(joinedload(EPPCatalogo.empresa))
    if empresa_id:
        query = query.filter(EPPCatalogo.empresa_id == empresa_id)
    if estado:
        query = query.filter(func.upper(EPPCatalogo.estado) == estado.upper().strip())
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(EPPCatalogo.codigo.ilike(like), EPPCatalogo.nombre.ilike(like), EPPCatalogo.categoria.ilike(like)))
    rows = _catalogo_export_rows(query.order_by(EPPCatalogo.nombre.asc()).all())
    return _excel_response(rows, "catalogo_epp_sst.xlsx", "Catalogo EPP")


@router.get("/export/entregas/excel")
def exportar_entregas_epp_excel(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    cargo_id: int | None = Query(default=None),
    empleado_id: int | None = Query(default=None),
    epp_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    rows = _entrega_export_rows(_get_filtered_entregas_for_export(db, empresa_id, sede_id, area_id, cargo_id, empleado_id, epp_id, estado, q))
    return _excel_response(rows, "entregas_epp_sst.xlsx", "Entregas EPP")


@router.get("/export/entregas/pdf")
def exportar_entregas_epp_pdf(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    cargo_id: int | None = Query(default=None),
    empleado_id: int | None = Query(default=None),
    epp_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    raw_rows = _entrega_export_rows(_get_filtered_entregas_for_export(db, empresa_id, sede_id, area_id, cargo_id, empleado_id, epp_id, estado, q))
    rows = [
        {
            "Empleado": r["Empleado"],
            "Documento": r["Documento"],
            "Empresa": r["Empresa"],
            "EPP": r["EPP"],
            "Categoría": r["Categoría"],
            "Entrega": r["Fecha entrega"],
            "Reposición": r["Fecha reposición"],
            "Estado": r["Estado"],
            "Firmado": r["Firmado"],
        }
        for r in raw_rows
    ]
    return _pdf_response("Reporte General de Entregas EPP", rows, "entregas_epp_sst.pdf")


@router.get("/export/reposiciones/excel")
def exportar_reposiciones_epp_excel(
    dias: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    hoy = date.today()
    limite = hoy + timedelta(days=dias)
    items = (
        db.query(EPPEntrega)
        .options(
            joinedload(EPPEntrega.empresa),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.sede),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.area),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.cargo),
            joinedload(EPPEntrega.epp),
        )
        .filter(EPPEntrega.activo.is_(True), EPPEntrega.fecha_reposicion.isnot(None), EPPEntrega.fecha_reposicion <= limite)
        .order_by(EPPEntrega.fecha_reposicion.asc())
        .all()
    )
    return _excel_response(_entrega_export_rows(items), f"reposiciones_epp_{dias}_dias.xlsx", "Reposiciones")


@router.get("/export/reposiciones/pdf")
def exportar_reposiciones_epp_pdf(
    dias: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    hoy = date.today()
    limite = hoy + timedelta(days=dias)
    items = (
        db.query(EPPEntrega)
        .options(
            joinedload(EPPEntrega.empresa),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.sede),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.area),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.cargo),
            joinedload(EPPEntrega.epp),
        )
        .filter(EPPEntrega.activo.is_(True), EPPEntrega.fecha_reposicion.isnot(None), EPPEntrega.fecha_reposicion <= limite)
        .order_by(EPPEntrega.fecha_reposicion.asc())
        .all()
    )
    raw_rows = _entrega_export_rows(items)
    rows = [
        {
            "Empleado": r["Empleado"],
            "EPP": r["EPP"],
            "Entrega": r["Fecha entrega"],
            "Reposición": r["Fecha reposición"],
            "Días": r["Días reposición"],
            "Estado": r["Estado"],
            "Firmado": r["Firmado"],
        }
        for r in raw_rows
    ]
    return _pdf_response(f"Reporte de Reposiciones EPP - {dias} días", rows, f"reposiciones_epp_{dias}_dias.pdf")


@router.get("/export/firmas/excel")
def exportar_pendientes_firma_epp_excel(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    items = (
        db.query(EPPEntrega)
        .options(
            joinedload(EPPEntrega.empresa),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.sede),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.area),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.cargo),
            joinedload(EPPEntrega.epp),
        )
        .filter(EPPEntrega.activo.is_(True), EPPEntrega.recibido_por_empleado.is_(False))
        .order_by(EPPEntrega.id.desc())
        .all()
    )
    return _excel_response(_entrega_export_rows(items), "pendientes_firma_epp.xlsx", "Pendientes Firma")


@router.get("/export/firmas/pdf")
def exportar_pendientes_firma_epp_pdf(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    raw_rows = _entrega_export_rows(
        db.query(EPPEntrega)
        .options(
            joinedload(EPPEntrega.empresa),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.sede),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.area),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.cargo),
            joinedload(EPPEntrega.epp),
        )
        .filter(EPPEntrega.activo.is_(True), EPPEntrega.recibido_por_empleado.is_(False))
        .order_by(EPPEntrega.id.desc())
        .all()
    )
    rows = [{"Empleado": r["Empleado"], "Documento": r["Documento"], "EPP": r["EPP"], "Entrega": r["Fecha entrega"], "Estado": r["Estado"]} for r in raw_rows]
    return _pdf_response("Reporte de Entregas EPP Pendientes de Firma", rows, "pendientes_firma_epp.pdf")


@router.get("/export/entregas/{entrega_id}/pdf")
def exportar_ficha_entrega_epp_pdf(
    entrega_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    item = (
        db.query(EPPEntrega)
        .options(
            joinedload(EPPEntrega.empresa),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.sede),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.area),
            joinedload(EPPEntrega.empleado).joinedload(Empleado.cargo),
            joinedload(EPPEntrega.epp),
        )
        .filter(EPPEntrega.id == entrega_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Entrega EPP no encontrada")
    return _pdf_ficha_entrega(item)
