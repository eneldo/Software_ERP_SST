# ============================================================
# ROUTER CAPACITACIONES SST
# FASE 2.7.1 - HACER SST PRO ENTERPRISE
# ============================================================

from datetime import date
from pathlib import Path
from uuid import uuid4
from app.services.image_optimizer import guardar_upload_optimizado
from app.services.upload_service import guardar_evidencia_sst
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db

from app.models.capacitacion import (
    CapacitacionSST,
    CapacitacionAsistenteSST
)

from app.schemas.capacitacion import (
    CapacitacionCreate,
    CapacitacionUpdate,
    CapacitacionResponse,
    CapacitacionResumenResponse,
    CapacitacionAsistenteCreate
)

router = APIRouter(
    prefix="/hacer/capacitaciones",
    tags=["HACER - Capacitaciones SST PRO"]
)

UPLOAD_DIR = Path("app/uploads/capacitaciones")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LISTAR
# ============================================================

@router.get("/", response_model=list[CapacitacionResponse])
def listar_capacitaciones(
    empresa_id: int,
    db: Session = Depends(get_db)
):

    registros = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.activo == True
        )
        .order_by(CapacitacionSST.id.desc())
        .all()
    )

    return registros


# ============================================================
# OBTENER
# ============================================================

@router.get("/{item_id}", response_model=CapacitacionResponse)
def obtener_capacitacion(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = (
        db.query(CapacitacionSST)
        .filter(CapacitacionSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Capacitación no encontrada"
        )

    return item


# ============================================================
# CREAR
# ============================================================

@router.post("/", response_model=CapacitacionResponse)
def crear_capacitacion(
    datos: CapacitacionCreate,
    db: Session = Depends(get_db)
):

    usuario_id = 1

    item = CapacitacionSST(
        empresa_id=datos.empresa_id,
        usuario_id=usuario_id,
        codigo=datos.codigo,
        nombre=datos.nombre,
        tema=datos.tema,
        objetivo=datos.objetivo,
        tipo=datos.tipo,
        modalidad=datos.modalidad,
        capacitador=datos.capacitador,
        responsable=datos.responsable,
        fecha_programada=datos.fecha_programada,
        fecha_ejecucion=datos.fecha_ejecucion,
        duracion_horas=datos.duracion_horas,
        lugar=datos.lugar,
        poblacion_objetivo=datos.poblacion_objetivo,
        total_asistentes=datos.total_asistentes,
        estado=datos.estado,
        cumplimiento=datos.cumplimiento,
        evidencia=datos.evidencia,
        observaciones=datos.observaciones,
        archivo_id=datos.archivo_id
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


# ============================================================
# ACTUALIZAR
# ============================================================

@router.put("/{item_id}", response_model=CapacitacionResponse)
def actualizar_capacitacion(
    item_id: int,
    datos: CapacitacionUpdate,
    db: Session = Depends(get_db)
):

    item = (
        db.query(CapacitacionSST)
        .filter(CapacitacionSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Capacitación no encontrada"
        )

    update_data = datos.model_dump(exclude_unset=True)

    for campo, valor in update_data.items():
        setattr(item, campo, valor)

    db.commit()
    db.refresh(item)

    return item


# ============================================================
# ELIMINAR
# ============================================================

@router.delete("/{item_id}")
def eliminar_capacitacion(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = (
        db.query(CapacitacionSST)
        .filter(CapacitacionSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Capacitación no encontrada"
        )

    item.activo = False

    db.commit()

    return {
        "mensaje": "Capacitación eliminada correctamente"
    }


# ============================================================
# FINALIZAR
# ============================================================

@router.patch("/{item_id}/finalizar")
def finalizar_capacitacion(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = (
        db.query(CapacitacionSST)
        .filter(CapacitacionSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Capacitación no encontrada"
        )

    item.estado = "EJECUTADA"
    item.cumplimiento = 100

    if item.fecha_ejecucion is None:
        item.fecha_ejecucion = date.today()

    db.commit()

    return {
        "mensaje": "Capacitación finalizada correctamente"
    }


# ============================================================
# RESUMEN
# ============================================================

@router.get(
    "/resumen/{empresa_id}",
    response_model=CapacitacionResumenResponse
)
def resumen_capacitaciones(
    empresa_id: int,
    db: Session = Depends(get_db)
):

    items = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.activo == True
        )
        .all()
    )

    total = len(items)

    programadas = len([
        x for x in items
        if x.estado == "PROGRAMADA"
    ])

    ejecutadas = len([
        x for x in items
        if x.estado == "EJECUTADA"
    ])

    canceladas = len([
        x for x in items
        if x.estado == "CANCELADA"
    ])

    vencidas = len([
        x for x in items
        if x.estado == "VENCIDA"
    ])

    total_asistentes = sum([
        x.total_asistentes or 0
        for x in items
    ])

    cumplimiento = 0

    if total > 0:
        cumplimiento = round(
            (ejecutadas / total) * 100
        )

    return {
        "total": total,
        "programadas": programadas,
        "ejecutadas": ejecutadas,
        "canceladas": canceladas,
        "vencidas": vencidas,
        "total_asistentes": total_asistentes,
        "cumplimiento": cumplimiento
    }


# ============================================================
# CARGAR BASE
# ============================================================

@router.post("/cargar-base/{empresa_id}")
def cargar_base_capacitaciones(
    empresa_id: int,
    db: Session = Depends(get_db)
):

    existentes = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id
        )
        .count()
    )

    if existentes > 0:
        return {
            "mensaje": "La base ya existe"
        }

    base = [

        (
            "CAP-SST-001",
            "Inducción SST",
            "Inducción SG-SST"
        ),

        (
            "CAP-SST-002",
            "Pausas Activas",
            "Ergonomía"
        ),

        (
            "CAP-SST-003",
            "Uso de EPP",
            "Elementos Protección Personal"
        ),

        (
            "CAP-SST-004",
            "Brigada Emergencias",
            "Emergencias"
        ),

        (
            "CAP-SST-005",
            "Investigación Accidentes",
            "Accidentalidad"
        )

    ]

    creados = 0

    for codigo, nombre, tema in base:

        item = CapacitacionSST(
            empresa_id=empresa_id,
            usuario_id=1,
            codigo=codigo,
            nombre=nombre,
            tema=tema,
            estado="PROGRAMADA"
        )

        db.add(item)
        creados += 1

    db.commit()

    return {
        "mensaje": "Base de capacitaciones cargada correctamente",
        "creados": creados
    }


# ============================================================
# SUBIR EVIDENCIA
# ============================================================

from app.services.image_optimizer import guardar_upload_optimizado

@router.post("/{item_id}/evidencia")
async def subir_evidencia_capacitacion(
    item_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    item = (
        db.query(CapacitacionSST)
        .filter(CapacitacionSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Capacitación no encontrada"
        )

    resultado = guardar_evidencia_sst(
        file=archivo,
        modulo="capacitaciones",
        #destino_dir=UPLOAD_DIR,
        formato_imagen="webp",
    )

    item.evidencia = resultado["url"]

    db.commit()
    db.refresh(item)

    return {
        "mensaje": "Evidencia cargada y optimizada correctamente",
        "archivo": item.evidencia,
        "extension": resultado["extension"],
        "tamano_bytes": resultado["tamano_bytes"],
        "optimizado": resultado["optimizado"],
    }


# ============================================================
# ASISTENTES
# ============================================================

@router.post("/{item_id}/asistentes")
def agregar_asistente(
    item_id: int,
    datos: CapacitacionAsistenteCreate,
    db: Session = Depends(get_db)
):

    capacitacion = (
        db.query(CapacitacionSST)
        .filter(CapacitacionSST.id == item_id)
        .first()
    )

    if not capacitacion:
        raise HTTPException(
            status_code=404,
            detail="Capacitación no encontrada"
        )

    asistente = CapacitacionAsistenteSST(
        capacitacion_id=item_id,
        empleado_id=datos.empleado_id,
        nombres=datos.nombres,
        documento=datos.documento,
        cargo=datos.cargo,
        area=datos.area,
        asistio=datos.asistio,
        evaluacion=datos.evaluacion,
        firma_url=datos.firma_url,
        observaciones=datos.observaciones
    )

    db.add(asistente)

    capacitacion.total_asistentes += 1

    db.commit()

    return {
        "mensaje": "Asistente agregado correctamente"
    }