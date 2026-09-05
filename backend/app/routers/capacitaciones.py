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
from app.auth.dependencies import require_roles

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

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST", "AUDITOR"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"]
ROLES_ADMIN = ["SUPER_ADMIN", "ADMIN_EMPRESA"]

UPLOAD_DIR = Path("app/uploads/capacitaciones")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LISTAR
# ============================================================

@router.get("/", response_model=list[CapacitacionResponse])
def listar_capacitaciones(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
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
# LISTAR POR TIPO CAPACITACION (H-014)
# ============================================================

@router.get("/por-tipo/{tipo_capacitacion}", response_model=list[CapacitacionResponse])
def listar_por_tipo_capacitacion(
    empresa_id: int,
    tipo_capacitacion: str,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):

    tipos_validos = [
        "INDUCCION", "REINDUCCION", "RIESGO_ESPECIFICO",
        "CAPACITACION_GENERAL", "CONTINUA",
    ]
    if tipo_capacitacion.upper() not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Válidos: {', '.join(tipos_validos)}",
        )

    registros = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.tipo_capacitacion == tipo_capacitacion.upper(),
            CapacitacionSST.activo == True,
        )
        .order_by(CapacitacionSST.fecha_programada.desc())
        .all()
    )

    return registros


# ============================================================
# RESUMEN POR TIPO (H-014)
# ============================================================

@router.get("/resumen-por-tipo/{empresa_id}")
def resumen_por_tipo_capacitacion(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):

    from sqlalchemy import case

    resultados = (
        db.query(
            CapacitacionSST.tipo_capacitacion,
            func.count(CapacitacionSST.id).label("total"),
            func.sum(
                case(
                    (CapacitacionSST.estado == "EJECUTADA", 1),
                    else_=0,
                )
            ).label("ejecutadas"),
        )
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.activo == True,
        )
        .group_by(CapacitacionSST.tipo_capacitacion)
        .all()
    )

    return [
        {
            "tipo_capacitacion": r.tipo_capacitacion,
            "total": r.total,
            "ejecutadas": int(r.ejecutadas or 0),
            "cumplimiento": round(int(r.ejecutadas or 0) / r.total * 100) if r.total > 0 else 0,
        }
        for r in resultados
    ]


# ============================================================
# OBTENER
# ============================================================

@router.get("/{item_id}", response_model=CapacitacionResponse)
def obtener_capacitacion(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
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
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):

    item = CapacitacionSST(
        empresa_id=datos.empresa_id,
        usuario_id=usuario.id,
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
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
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
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ADMIN)),
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
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
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

    from app.models.capacitacion import CapacitacionAsistenteSST
    from app.models.capacitacion_certificado import CapacitacionCertificado

    asistentes = (
        db.query(CapacitacionAsistenteSST)
        .filter(
            CapacitacionAsistenteSST.capacitacion_id == item_id,
            CapacitacionAsistenteSST.asistio == True,
        )
        .all()
    )

    certificados_creados = 0
    for asistente in asistentes:
        existe = (
            db.query(CapacitacionCertificado)
            .filter(
                CapacitacionCertificado.capacitacion_id == item_id,
                CapacitacionCertificado.asistente_id == asistente.id,
                CapacitacionCertificado.activo == True,
            )
            .first()
        )
        if not existe:
            certificado = CapacitacionCertificado(
                capacitacion_id=item_id,
                asistente_id=asistente.id,
                activo=True,
            )
            db.add(certificado)
            certificados_creados += 1

    db.commit()

    return {
        "mensaje": "Capacitación finalizada correctamente",
        "certificados_generados": certificados_creados,
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
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
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
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
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
            "Inducción SG-SST",
            "INDUCCION",
        ),

        (
            "CAP-SST-002",
            "Reinducción SST",
            "Reinducción SG-SST",
            "REINDUCCION",
        ),

        (
            "CAP-SST-003",
            "Uso de EPP",
            "Elementos Protección Personal",
            "RIESGO_ESPECIFICO",
        ),

        (
            "CAP-SST-004",
            "Brigada Emergencias",
            "Emergencias",
            "CAPACITACION_GENERAL",
        ),

        (
            "CAP-SST-005",
            "Investigación Accidentes",
            "Accidentalidad",
            "CAPACITACION_GENERAL",
        ),

        (
            "CAP-SST-006",
            "Trabajo en Alturas",
            "Prevención caídas",
            "RIESGO_ESPECIFICO",
        ),

        (
            "CAP-SST-007",
            "Espacios Confinados",
            "Seguridad en espacios confinados",
            "RIESGO_ESPECIFICO",
        ),

        (
            "CAP-SST-008",
            "Primeros Auxilios",
            "Atención de emergencias",
            "CAPACITACION_GENERAL",
        ),

    ]

    creados = 0

    for codigo, nombre, tema, tipo_cap in base:

        item = CapacitacionSST(
            empresa_id=empresa_id,
            usuario_id=usuario.id,
            codigo=codigo,
            nombre=nombre,
            tema=tema,
            tipo_capacitacion=tipo_cap,
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

@router.post("/{item_id}/evidencia")
async def subir_evidencia_capacitacion(
    item_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
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
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
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
