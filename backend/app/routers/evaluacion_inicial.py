# ============================================================
# ROUTER EVALUACIÓN INICIAL SST
# FASE SST PRO 1.3 - EVALUACIÓN INICIAL INTELIGENTE
# Carga automática 3 / 7 / 21 / 60 estándares según empresa
# ============================================================

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles

from app.models.empresa import Empresa
from app.models.archivo_sst import ArchivoSST
from app.models.evaluacion_inicial import (
    EvaluacionInicialSST,
    EvaluacionInicialItemSST,
)

from app.services.upload_service import guardar_evidencia_sst
from app.services.estandares_evaluacion_sst import (
    clave_orden_numeral,
    obtener_criterios_evaluacion,
    obtener_criterios_parametrizados,
)

from app.schemas.evaluacion_inicial_schema import (
    EvaluacionInicialCreate,
    EvaluacionInicialUpdate,
    EvaluacionInicialResponse,
    EvaluacionInicialItemCreate,
    EvaluacionInicialItemUpdate,
    EvaluacionInicialItemResponse,
    EvaluacionInicialRespuestaMasiva,
)


router = APIRouter(
    prefix="/planear/evaluacion-inicial",
    tags=["PLANEAR - Evaluación Inicial SST PRO"],
)


ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


TIPOS_ESTANDARES_VALIDOS = {"3", "7", "21", "60"}


@router.get("/criterios/{tipo}", response_model=list[dict])
def listar_criterios(
    tipo: str,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    """Catálogo de criterios Res. 0312: BD parametrizable con respaldo en base normativa."""
    if str(tipo).strip() not in TIPOS_ESTANDARES_VALIDOS:
        raise HTTPException(status_code=400, detail="Tipo de estándares no válido")
    return obtener_criterios_parametrizados(db, str(tipo).strip())


def calcular_resumen(evaluacion: EvaluacionInicialSST):
    items_activos = [item for item in evaluacion.items if item.activo]

    total_evaluables = len(
        [item for item in items_activos if item.respuesta != "NO_APLICA"]
    )

    cumplen = len([item for item in items_activos if item.respuesta == "CUMPLE"])
    no_cumplen = len([item for item in items_activos if item.respuesta == "NO_CUMPLE"])
    no_aplican = len([item for item in items_activos if item.respuesta == "NO_APLICA"])

    porcentaje = round((cumplen / total_evaluables) * 100) if total_evaluables > 0 else 0

    if porcentaje >= 86:
        nivel = "ACEPTABLE"
    elif porcentaje >= 61:
        nivel = "MODERADO"
    else:
        nivel = "CRITICO"

    evaluacion.total_items = len(items_activos)
    evaluacion.items_cumplen = cumplen
    evaluacion.items_no_cumplen = no_cumplen
    evaluacion.items_no_aplican = no_aplican
    evaluacion.porcentaje_cumplimiento = porcentaje
    evaluacion.nivel = nivel

    return evaluacion


def serializar_item(item: EvaluacionInicialItemSST):
    archivo = item.archivo

    return {
        "id": item.id,
        "evaluacion_id": item.evaluacion_id,
        "archivo_id": item.archivo_id,
        "estandar": item.estandar,
        "numeral": item.numeral,
        "criterio": item.criterio,
        "respuesta": item.respuesta,
        "puntaje": item.puntaje,
        "evidencia": item.evidencia,
        "observaciones": item.observaciones,
        "responsable": item.responsable,
        "archivo_url": archivo.url if archivo else None,
        "archivo_nombre": archivo.nombre_original if archivo else None,
        "archivo_extension": archivo.extension if archivo else None,
        "activo": item.activo,
        "fecha_creacion": item.fecha_creacion,
        "fecha_actualizacion": item.fecha_actualizacion,
    }


def serializar_evaluacion(evaluacion: EvaluacionInicialSST):
    return {
        "id": evaluacion.id,
        "empresa_id": evaluacion.empresa_id,
        "usuario_id": evaluacion.usuario_id,
        "codigo": evaluacion.codigo,
        "nombre": evaluacion.nombre,
        "fecha_evaluacion": evaluacion.fecha_evaluacion,
        "responsable": evaluacion.responsable,
        "total_items": evaluacion.total_items,
        "items_cumplen": evaluacion.items_cumplen,
        "items_no_cumplen": evaluacion.items_no_cumplen,
        "items_no_aplican": evaluacion.items_no_aplican,
        "porcentaje_cumplimiento": evaluacion.porcentaje_cumplimiento,
        "nivel": evaluacion.nivel,
        "estado": evaluacion.estado,
        "observaciones_generales": evaluacion.observaciones_generales,
        "activo": evaluacion.activo,
        "fecha_creacion": evaluacion.fecha_creacion,
        "fecha_actualizacion": evaluacion.fecha_actualizacion,
        "items": [
            serializar_item(item)
            for item in sorted(
                evaluacion.items,
                key=lambda current: (
                    clave_orden_numeral(current),
                    current.id or 0,
                ),
            )
            if item.activo
        ],
    }


def obtener_evaluacion_con_items(db: Session, evaluacion_id: int):
    return (
        db.query(EvaluacionInicialSST)
        .options(
            joinedload(EvaluacionInicialSST.items).joinedload(
                EvaluacionInicialItemSST.archivo
            )
        )
        .filter(EvaluacionInicialSST.id == evaluacion_id)
        .first()
    )


@router.post("/", response_model=EvaluacionInicialResponse)
def crear_evaluacion_inicial(
    data: EvaluacionInicialCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    evaluacion = EvaluacionInicialSST(
        empresa_id=data.empresa_id,
        usuario_id=usuario.id,
        codigo=data.codigo,
        nombre=data.nombre,
        fecha_evaluacion=data.fecha_evaluacion,
        responsable=data.responsable,
        observaciones_generales=data.observaciones_generales,
        estado="BORRADOR",
    )

    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)

    if data.items:
        items_base = data.items
    else:
        tipo_estandares = getattr(empresa, "total_estandares_sst", None) or getattr(
            empresa, "tipo_estandares_sst", "7"
        )

        criterios = obtener_criterios_evaluacion(tipo_estandares)
        items_base = [EvaluacionInicialItemCreate(**criterio) for criterio in criterios]

    for item in items_base:
        db.add(
            EvaluacionInicialItemSST(
                evaluacion_id=evaluacion.id,
                **item.model_dump(),
            )
        )

    db.commit()

    evaluacion = obtener_evaluacion_con_items(db, evaluacion.id)

    calcular_resumen(evaluacion)
    db.commit()
    db.refresh(evaluacion)

    return serializar_evaluacion(evaluacion)


@router.get("/", response_model=list[EvaluacionInicialResponse])
def listar_evaluaciones_iniciales(
    empresa_id: int | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    query = (
        db.query(EvaluacionInicialSST)
        .options(
            joinedload(EvaluacionInicialSST.items).joinedload(
                EvaluacionInicialItemSST.archivo
            )
        )
        .filter(EvaluacionInicialSST.activo == True)
    )

    if empresa_id:
        query = query.filter(EvaluacionInicialSST.empresa_id == empresa_id)

    if estado:
        query = query.filter(EvaluacionInicialSST.estado == estado.upper())

    evaluaciones = query.order_by(EvaluacionInicialSST.id.desc()).all()

    return [serializar_evaluacion(evaluacion) for evaluacion in evaluaciones]


@router.get("/{evaluacion_id}", response_model=EvaluacionInicialResponse)
def obtener_evaluacion_inicial(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    evaluacion = obtener_evaluacion_con_items(db, evaluacion_id)

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    return serializar_evaluacion(evaluacion)


@router.put("/{evaluacion_id}", response_model=EvaluacionInicialResponse)
def actualizar_evaluacion_inicial(
    evaluacion_id: int,
    data: EvaluacionInicialUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    evaluacion = obtener_evaluacion_con_items(db, evaluacion_id)

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(evaluacion, key, value)

    calcular_resumen(evaluacion)

    db.commit()
    db.refresh(evaluacion)

    return serializar_evaluacion(evaluacion)


@router.post("/{evaluacion_id}/items", response_model=EvaluacionInicialItemResponse)
def agregar_item_evaluacion(
    evaluacion_id: int,
    data: EvaluacionInicialItemCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    evaluacion = (
        db.query(EvaluacionInicialSST)
        .filter(EvaluacionInicialSST.id == evaluacion_id)
        .first()
    )

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    item = EvaluacionInicialItemSST(
        evaluacion_id=evaluacion_id,
        **data.model_dump(),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    evaluacion = obtener_evaluacion_con_items(db, evaluacion_id)
    calcular_resumen(evaluacion)
    db.commit()

    item = (
        db.query(EvaluacionInicialItemSST)
        .options(joinedload(EvaluacionInicialItemSST.archivo))
        .filter(EvaluacionInicialItemSST.id == item.id)
        .first()
    )

    return serializar_item(item)


@router.put("/items/{item_id}", response_model=EvaluacionInicialItemResponse)
def actualizar_item_evaluacion(
    item_id: int,
    data: EvaluacionInicialItemUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = (
        db.query(EvaluacionInicialItemSST)
        .options(joinedload(EvaluacionInicialItemSST.archivo))
        .filter(EvaluacionInicialItemSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    evaluacion = obtener_evaluacion_con_items(db, item.evaluacion_id)
    calcular_resumen(evaluacion)
    db.commit()

    return serializar_item(item)


@router.post("/items/{item_id}/evidencia", response_model=EvaluacionInicialItemResponse)
def subir_evidencia_item(
    item_id: int,
    descripcion: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    item = (
        db.query(EvaluacionInicialItemSST)
        .options(joinedload(EvaluacionInicialItemSST.evaluacion))
        .filter(EvaluacionInicialItemSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")

    evaluacion = item.evaluacion

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    resultado = guardar_evidencia_sst(
        file=file,
        modulo="evaluacion-inicial",
        formato_imagen="webp",
    )

    archivo = ArchivoSST(
        empresa_id=evaluacion.empresa_id,
        usuario_id=usuario.id,
        tipo="EVIDENCIA",
        nombre_original=file.filename,
        nombre_archivo=resultado["nombre_archivo"],
        ruta=resultado["ruta_fisica"],
        url=resultado["url"],
        extension=resultado["extension"],
        mime_type=resultado["mime_type"],
        tamano_bytes=resultado["tamano_bytes"],
        modulo="EVALUACION_INICIAL",
        referencia_id=item.id,
        descripcion=descripcion or f"Evidencia del criterio {item.numeral or item.id}",
        activo=True,
    )

    db.add(archivo)
    db.commit()
    db.refresh(archivo)

    item.archivo_id = archivo.id
    item.evidencia = resultado["url"]

    db.commit()
    db.refresh(item)

    item = (
        db.query(EvaluacionInicialItemSST)
        .options(joinedload(EvaluacionInicialItemSST.archivo))
        .filter(EvaluacionInicialItemSST.id == item_id)
        .first()
    )

    return serializar_item(item)


@router.post("/{evaluacion_id}/guardar-respuestas", response_model=EvaluacionInicialResponse)
def guardar_respuestas_masivo(
    evaluacion_id: int,
    respuestas: list[EvaluacionInicialRespuestaMasiva],
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    evaluacion = obtener_evaluacion_con_items(db, evaluacion_id)

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    items_por_id = {item.id: item for item in evaluacion.items}

    for respuesta in respuestas:
        item = items_por_id.get(respuesta.item_id)

        if not item:
            continue

        data = respuesta.model_dump(exclude_unset=True)
        data.pop("item_id", None)

        for key, value in data.items():
            setattr(item, key, value)

    calcular_resumen(evaluacion)

    db.commit()
    db.refresh(evaluacion)

    evaluacion = obtener_evaluacion_con_items(db, evaluacion_id)

    return serializar_evaluacion(evaluacion)


@router.delete("/items/{item_id}")
def eliminar_item_evaluacion(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = (
        db.query(EvaluacionInicialItemSST)
        .filter(EvaluacionInicialItemSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")

    item.activo = False

    db.commit()

    evaluacion = obtener_evaluacion_con_items(db, item.evaluacion_id)
    calcular_resumen(evaluacion)
    db.commit()

    return {"mensaje": "Ítem desactivado correctamente"}


@router.patch("/{evaluacion_id}/finalizar", response_model=EvaluacionInicialResponse)
def finalizar_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    evaluacion = obtener_evaluacion_con_items(db, evaluacion_id)

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    calcular_resumen(evaluacion)
    evaluacion.estado = "FINALIZADA"

    db.commit()
    db.refresh(evaluacion)

    return serializar_evaluacion(evaluacion)


@router.delete("/{evaluacion_id}")
def eliminar_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    evaluacion = (
        db.query(EvaluacionInicialSST)
        .filter(EvaluacionInicialSST.id == evaluacion_id)
        .first()
    )

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    evaluacion.activo = False
    evaluacion.estado = "OBSOLETA"

    db.commit()

    return {"mensaje": "Evaluación inicial desactivada correctamente"}
