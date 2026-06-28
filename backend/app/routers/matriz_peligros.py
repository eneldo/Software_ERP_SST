# ============================================================
# ROUTER MATRIZ DE PELIGROS SST
# FASE 2.5.3 - HARDENING ENTERPRISE + UPLOAD GLOBAL
# Archivo: backend/app/routers/matriz_peligros.py
# ============================================================

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles

from app.models.empresa import Empresa
from app.models.archivo_sst import ArchivoSST
from app.models.matriz_peligros import MatrizPeligrosSST

from app.services.upload_service import guardar_evidencia_sst

from app.schemas.matriz_peligros_schema import (
    MatrizPeligrosCreate,
    MatrizPeligrosUpdate,
    MatrizPeligrosResponse,
    MatrizPeligrosResumenResponse,
)


router = APIRouter(
    prefix="/planear/matriz-peligros",
    tags=["PLANEAR - Matriz de Peligros SST PRO"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


PELIGROS_BASE = [
    {
        "codigo": "MP-SST-001",
        "proceso": "Administrativo",
        "actividad": "Trabajo en oficina",
        "tarea": "Uso de computador",
        "peligro": "Posturas prolongadas y movimientos repetitivos.",
        "clasificacion_peligro": "Biomecánico",
        "efectos_posibles": "Dolor lumbar, fatiga muscular, túnel del carpo.",
        "probabilidad": 2,
        "consecuencia": 2,
        "medidas_intervencion": "Pausas activas, ergonomía del puesto de trabajo, capacitación.",
    },
    {
        "codigo": "MP-SST-002",
        "proceso": "Servicios Generales",
        "actividad": "Aseo y limpieza",
        "tarea": "Uso de sustancias químicas",
        "peligro": "Exposición a productos químicos de limpieza.",
        "clasificacion_peligro": "Químico",
        "efectos_posibles": "Irritación ocular, dermatitis, afectación respiratoria.",
        "probabilidad": 3,
        "consecuencia": 3,
        "medidas_intervencion": "Uso de EPP, fichas de seguridad, ventilación, capacitación.",
    },
    {
        "codigo": "MP-SST-003",
        "proceso": "Mantenimiento",
        "actividad": "Intervención de equipos",
        "tarea": "Trabajo eléctrico básico",
        "peligro": "Contacto eléctrico directo o indirecto.",
        "clasificacion_peligro": "Eléctrico",
        "efectos_posibles": "Quemaduras, choque eléctrico, muerte.",
        "probabilidad": 3,
        "consecuencia": 5,
        "medidas_intervencion": "Bloqueo y etiquetado, personal competente, EPP dieléctrico.",
    },
]


def calcular_riesgo(item: MatrizPeligrosSST):
    item.nivel_riesgo = int(item.probabilidad or 1) * int(item.consecuencia or 1)

    if item.nivel_riesgo <= 4:
        item.interpretacion_riesgo = "BAJO"
        item.aceptabilidad = "ACEPTABLE"
    elif item.nivel_riesgo <= 9:
        item.interpretacion_riesgo = "MEDIO"
        item.aceptabilidad = "MEJORABLE"
    elif item.nivel_riesgo <= 16:
        item.interpretacion_riesgo = "ALTO"
        item.aceptabilidad = "NO ACEPTABLE"
    else:
        item.interpretacion_riesgo = "CRITICO"
        item.aceptabilidad = "NO ACEPTABLE CRITICO"

    return item


def serializar(item: MatrizPeligrosSST):
    archivo = item.archivo

    return {
        "id": item.id,
        "empresa_id": item.empresa_id,
        "usuario_id": item.usuario_id,
        "archivo_id": item.archivo_id,
        "codigo": item.codigo,
        "proceso": item.proceso,
        "actividad": item.actividad,
        "tarea": item.tarea,
        "peligro": item.peligro,
        "clasificacion_peligro": item.clasificacion_peligro,
        "efectos_posibles": item.efectos_posibles,
        "controles_fuente": item.controles_fuente,
        "controles_medio": item.controles_medio,
        "controles_individuo": item.controles_individuo,
        "probabilidad": item.probabilidad,
        "consecuencia": item.consecuencia,
        "nivel_riesgo": item.nivel_riesgo,
        "interpretacion_riesgo": item.interpretacion_riesgo,
        "aceptabilidad": item.aceptabilidad,
        "medidas_intervencion": item.medidas_intervencion,
        "responsable": item.responsable,
        "fecha_revision": item.fecha_revision,
        "fecha_vencimiento": item.fecha_vencimiento,
        "estado": item.estado,
        "evidencia": item.evidencia,
        "observaciones": item.observaciones,
        "archivo_url": archivo.url if archivo else None,
        "archivo_nombre": archivo.nombre_original if archivo else None,
        "archivo_extension": archivo.extension if archivo else None,
        "activo": item.activo,
        "fecha_creacion": item.fecha_creacion,
        "fecha_actualizacion": item.fecha_actualizacion,
    }


@router.post("/", response_model=MatrizPeligrosResponse)
def crear_peligro(
    data: MatrizPeligrosCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    item = MatrizPeligrosSST(**data.model_dump(), usuario_id=usuario.id)
    calcular_riesgo(item)

    db.add(item)
    db.commit()
    db.refresh(item)

    item = (
        db.query(MatrizPeligrosSST)
        .options(joinedload(MatrizPeligrosSST.archivo))
        .filter(MatrizPeligrosSST.id == item.id)
        .first()
    )

    return serializar(item)


@router.post("/cargar-base/{empresa_id}")
def cargar_base_peligros(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    creados = 0

    for data in PELIGROS_BASE:
        existe = (
            db.query(MatrizPeligrosSST)
            .filter(
                MatrizPeligrosSST.empresa_id == empresa_id,
                MatrizPeligrosSST.codigo == data["codigo"],
            )
            .first()
        )

        if existe:
            continue

        item = MatrizPeligrosSST(
            empresa_id=empresa_id,
            usuario_id=usuario.id,
            estado="PENDIENTE",
            **data,
        )

        calcular_riesgo(item)
        db.add(item)
        creados += 1

    db.commit()

    return {
        "mensaje": "Base de peligros cargada correctamente",
        "creados": creados,
    }


@router.get("/", response_model=list[MatrizPeligrosResponse])
def listar_peligros(
    empresa_id: int | None = None,
    proceso: str | None = None,
    clasificacion_peligro: str | None = None,
    interpretacion_riesgo: str | None = None,
    estado: str | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    query = (
        db.query(MatrizPeligrosSST)
        .options(joinedload(MatrizPeligrosSST.archivo))
        .filter(MatrizPeligrosSST.activo == True)
    )

    if empresa_id:
        query = query.filter(MatrizPeligrosSST.empresa_id == empresa_id)

    if proceso:
        query = query.filter(MatrizPeligrosSST.proceso.ilike(f"%{proceso}%"))

    if clasificacion_peligro:
        query = query.filter(
            MatrizPeligrosSST.clasificacion_peligro == clasificacion_peligro
        )

    if interpretacion_riesgo:
        query = query.filter(
            MatrizPeligrosSST.interpretacion_riesgo == interpretacion_riesgo
        )

    if estado:
        query = query.filter(MatrizPeligrosSST.estado == estado)

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            MatrizPeligrosSST.codigo.ilike(patron)
            | MatrizPeligrosSST.proceso.ilike(patron)
            | MatrizPeligrosSST.actividad.ilike(patron)
            | MatrizPeligrosSST.peligro.ilike(patron)
        )

    items = query.order_by(MatrizPeligrosSST.id.desc()).all()

    return [serializar(item) for item in items]


@router.get("/resumen/{empresa_id}", response_model=MatrizPeligrosResumenResponse)
def resumen_peligros(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    items = (
        db.query(MatrizPeligrosSST)
        .filter(
            MatrizPeligrosSST.empresa_id == empresa_id,
            MatrizPeligrosSST.activo == True,
        )
        .all()
    )

    total = len(items)
    bajos = len([i for i in items if i.interpretacion_riesgo == "BAJO"])
    medios = len([i for i in items if i.interpretacion_riesgo == "MEDIO"])
    altos = len([i for i in items if i.interpretacion_riesgo == "ALTO"])
    criticos = len([i for i in items if i.interpretacion_riesgo == "CRITICO"])
    pendientes = len([i for i in items if i.estado == "PENDIENTE"])
    porcentaje_criticos = round((criticos / total) * 100) if total > 0 else 0

    return {
        "total": total,
        "bajos": bajos,
        "medios": medios,
        "altos": altos,
        "criticos": criticos,
        "pendientes": pendientes,
        "porcentaje_criticos": porcentaje_criticos,
    }


@router.get("/{item_id}", response_model=MatrizPeligrosResponse)
def obtener_peligro(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    item = (
        db.query(MatrizPeligrosSST)
        .options(joinedload(MatrizPeligrosSST.archivo))
        .filter(MatrizPeligrosSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Peligro no encontrado")

    return serializar(item)


@router.put("/{item_id}", response_model=MatrizPeligrosResponse)
def actualizar_peligro(
    item_id: int,
    data: MatrizPeligrosUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = (
        db.query(MatrizPeligrosSST)
        .options(joinedload(MatrizPeligrosSST.archivo))
        .filter(MatrizPeligrosSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Peligro no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    calcular_riesgo(item)

    db.commit()
    db.refresh(item)

    return serializar(item)


@router.post("/{item_id}/evidencia", response_model=MatrizPeligrosResponse)
def subir_evidencia_peligro(
    item_id: int,
    descripcion: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    item = (
        db.query(MatrizPeligrosSST)
        .filter(MatrizPeligrosSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Peligro no encontrado")

    resultado = guardar_evidencia_sst(
        file=file,
        modulo="matriz-peligros",
        formato_imagen="webp",
    )

    archivo = ArchivoSST(
        empresa_id=item.empresa_id,
        usuario_id=usuario.id,
        tipo="EVIDENCIA",
        nombre_original=file.filename,
        nombre_archivo=resultado["nombre_archivo"],
        ruta=resultado["ruta_fisica"],
        url=resultado["url"],
        extension=resultado["extension"],
        mime_type=resultado["mime_type"],
        tamano_bytes=resultado["tamano_bytes"],
        modulo="MATRIZ_PELIGROS",
        referencia_id=item.id,
        descripcion=descripcion or f"Evidencia matriz de peligros {item.codigo}",
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
        db.query(MatrizPeligrosSST)
        .options(joinedload(MatrizPeligrosSST.archivo))
        .filter(MatrizPeligrosSST.id == item.id)
        .first()
    )

    return serializar(item)


@router.delete("/{item_id}/evidencia")
def eliminar_evidencia_peligro(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = (
        db.query(MatrizPeligrosSST)
        .options(joinedload(MatrizPeligrosSST.archivo))
        .filter(MatrizPeligrosSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Peligro no encontrado")

    if item.archivo:
        item.archivo.activo = False

    item.archivo_id = None
    item.evidencia = None

    db.commit()

    return {"mensaje": "Evidencia retirada correctamente"}


@router.delete("/{item_id}")
def eliminar_peligro(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    item = (
        db.query(MatrizPeligrosSST)
        .filter(MatrizPeligrosSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Peligro no encontrado")

    item.activo = False
    db.commit()

    return {"mensaje": "Peligro desactivado correctamente"}