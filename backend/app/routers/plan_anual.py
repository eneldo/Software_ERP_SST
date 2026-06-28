from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.empresa import Empresa
from app.models.archivo_sst import ArchivoSST
from app.models.plan_anual import PlanAnualSST
from app.services.upload_service import guardar_evidencia_sst
from app.schemas.plan_anual import (
    PlanAnualCreate,
    PlanAnualUpdate,
    PlanAnualResponse,
    PlanAnualResumenResponse,
)


router = APIRouter(
    prefix="/planear/plan-anual",
    tags=["PLANEAR - Plan Anual SST PRO"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


ACTIVIDADES_BASE = [
    {
        "codigo": "PA-SST-001",
        "actividad": "Capacitación anual en Seguridad y Salud en el Trabajo",
        "objetivo": "Fortalecer competencias SST en trabajadores y contratistas.",
        "responsable": "Responsable SST",
        "indicador": "Número de trabajadores capacitados / total trabajadores",
        "meta": "Capacitar al 100% del personal",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-002",
        "actividad": "Inspecciones planeadas de seguridad",
        "objetivo": "Identificar condiciones inseguras y generar acciones preventivas.",
        "responsable": "Responsable SST",
        "indicador": "Inspecciones ejecutadas / inspecciones programadas",
        "meta": "Ejecutar el 100% de inspecciones programadas",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-003",
        "actividad": "Actualización de Matriz Legal SST",
        "objetivo": "Mantener identificados y actualizados los requisitos legales aplicables.",
        "responsable": "Responsable SST",
        "indicador": "Requisitos revisados / requisitos registrados",
        "meta": "Revisar el 100% de requisitos legales",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-004",
        "actividad": "Actualización de Matriz de Peligros",
        "objetivo": "Actualizar la identificación de peligros, evaluación y valoración de riesgos.",
        "responsable": "Responsable SST",
        "indicador": "Procesos revisados / procesos existentes",
        "meta": "Actualizar el 100% de procesos",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-005",
        "actividad": "Simulacro de emergencia",
        "objetivo": "Evaluar la preparación y respuesta ante emergencias.",
        "responsable": "Brigada de emergencias",
        "indicador": "Simulacros ejecutados / simulacros programados",
        "meta": "Ejecutar al menos un simulacro anual",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-006",
        "actividad": "Auditoría interna SG-SST",
        "objetivo": "Verificar cumplimiento del SG-SST y generar acciones de mejora.",
        "responsable": "Auditor interno SST",
        "indicador": "Auditorías ejecutadas / auditorías programadas",
        "meta": "Ejecutar auditoría interna anual",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-007",
        "actividad": "Revisión por la Dirección",
        "objetivo": "Evaluar desempeño del SG-SST y tomar decisiones de mejora.",
        "responsable": "Alta Dirección",
        "indicador": "Revisión ejecutada / revisión programada",
        "meta": "Realizar revisión anual",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-008",
        "actividad": "Entrega y seguimiento de Elementos de Protección Personal",
        "objetivo": "Garantizar la entrega, uso y reposición de EPP según riesgos identificados.",
        "responsable": "Responsable SST",
        "indicador": "EPP entregados / EPP requeridos",
        "meta": "Garantizar cobertura del 100%",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-009",
        "actividad": "Investigación de incidentes y accidentes de trabajo",
        "objetivo": "Investigar eventos y definir acciones correctivas y preventivas.",
        "responsable": "Responsable SST",
        "indicador": "Eventos investigados / eventos reportados",
        "meta": "Investigar el 100% de eventos reportados",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
    {
        "codigo": "PA-SST-010",
        "actividad": "Exámenes médicos ocupacionales",
        "objetivo": "Realizar seguimiento a condiciones de salud de los trabajadores.",
        "responsable": "Responsable SST / IPS Ocupacional",
        "indicador": "Exámenes realizados / exámenes programados",
        "meta": "Cumplir el 100% del programa médico ocupacional",
        "estado": "PLANIFICADO",
        "porcentaje_avance": 0,
    },
]


def normalizar_estado_y_avance(item: PlanAnualSST):
    item.porcentaje_avance = max(0, min(100, int(item.porcentaje_avance or 0)))

    if item.estado == "EJECUTADO":
        item.porcentaje_avance = 100

    if (
        item.estado not in ["EJECUTADO", "CANCELADO"]
        and item.fecha_fin
        and item.fecha_fin < date.today()
        and item.porcentaje_avance < 100
    ):
        item.estado = "VENCIDO"

    return item


def serializar(item: PlanAnualSST):
    archivo = item.archivo

    return {
        "id": item.id,
        "empresa_id": item.empresa_id,
        "usuario_id": item.usuario_id,
        "archivo_id": item.archivo_id,
        "codigo": item.codigo,
        "actividad": item.actividad,
        "objetivo": item.objetivo,
        "responsable": item.responsable,
        "recurso_humano": item.recurso_humano,
        "recurso_fisico": item.recurso_fisico,
        "recurso_financiero": item.recurso_financiero,
        "presupuesto": item.presupuesto,
        "indicador": item.indicador,
        "meta": item.meta,
        "fecha_inicio": item.fecha_inicio,
        "fecha_fin": item.fecha_fin,
        "estado": item.estado,
        "porcentaje_avance": item.porcentaje_avance,
        "evidencia": item.evidencia,
        "observaciones": item.observaciones,
        "archivo_url": archivo.url if archivo else None,
        "archivo_nombre": archivo.nombre_original if archivo else None,
        "archivo_extension": archivo.extension if archivo else None,
        "activo": item.activo,
        "fecha_creacion": item.fecha_creacion,
        "fecha_actualizacion": item.fecha_actualizacion,
    }


@router.post("/", response_model=PlanAnualResponse)
def crear_actividad(
    data: PlanAnualCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    item = PlanAnualSST(**data.model_dump(), usuario_id=usuario.id)
    normalizar_estado_y_avance(item)

    db.add(item)
    db.commit()
    db.refresh(item)

    item = (
        db.query(PlanAnualSST)
        .options(joinedload(PlanAnualSST.archivo))
        .filter(PlanAnualSST.id == item.id)
        .first()
    )

    return serializar(item)


@router.post("/cargar-base/{empresa_id}")
def cargar_base_plan_anual(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    creados = 0

    for data in ACTIVIDADES_BASE:
        existe = (
            db.query(PlanAnualSST)
            .filter(
                PlanAnualSST.empresa_id == empresa_id,
                PlanAnualSST.codigo == data["codigo"],
            )
            .first()
        )

        if existe:
            continue

        item = PlanAnualSST(
            empresa_id=empresa_id,
            usuario_id=usuario.id,
            **data,
        )

        normalizar_estado_y_avance(item)

        db.add(item)
        creados += 1

    db.commit()

    return {
        "mensaje": "Base del Plan Anual SST cargada correctamente",
        "creados": creados,
    }


@router.get("/", response_model=list[PlanAnualResponse])
def listar_plan_anual(
    empresa_id: int | None = None,
    estado: str | None = None,
    responsable: str | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    query = (
        db.query(PlanAnualSST)
        .options(joinedload(PlanAnualSST.archivo))
        .filter(PlanAnualSST.activo == True)
    )

    if empresa_id:
        query = query.filter(PlanAnualSST.empresa_id == empresa_id)

    if estado:
        query = query.filter(PlanAnualSST.estado == estado)

    if responsable:
        query = query.filter(PlanAnualSST.responsable.ilike(f"%{responsable}%"))

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            PlanAnualSST.codigo.ilike(patron)
            | PlanAnualSST.actividad.ilike(patron)
            | PlanAnualSST.objetivo.ilike(patron)
        )

    items = query.order_by(PlanAnualSST.id.desc()).all()

    for item in items:
        normalizar_estado_y_avance(item)

    db.commit()

    return [serializar(item) for item in items]


@router.get("/resumen/{empresa_id}", response_model=PlanAnualResumenResponse)
def resumen_plan_anual(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    items = (
        db.query(PlanAnualSST)
        .filter(
            PlanAnualSST.empresa_id == empresa_id,
            PlanAnualSST.activo == True,
        )
        .all()
    )

    for item in items:
        normalizar_estado_y_avance(item)

    db.commit()

    total = len(items)
    ejecutados = len([i for i in items if i.estado == "EJECUTADO"])

    return {
        "total": total,
        "planificados": len([i for i in items if i.estado == "PLANIFICADO"]),
        "en_proceso": len([i for i in items if i.estado == "EN_PROCESO"]),
        "ejecutados": ejecutados,
        "cancelados": len([i for i in items if i.estado == "CANCELADO"]),
        "vencidos": len([i for i in items if i.estado == "VENCIDO"]),
        "cumplimiento": round((ejecutados / total) * 100) if total > 0 else 0,
        "presupuesto_total": sum(float(i.presupuesto or 0) for i in items),
    }


@router.get("/{item_id}", response_model=PlanAnualResponse)
def obtener_actividad(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    item = (
        db.query(PlanAnualSST)
        .options(joinedload(PlanAnualSST.archivo))
        .filter(PlanAnualSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    normalizar_estado_y_avance(item)
    db.commit()

    return serializar(item)


@router.put("/{item_id}", response_model=PlanAnualResponse)
def actualizar_actividad(
    item_id: int,
    data: PlanAnualUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = (
        db.query(PlanAnualSST)
        .options(joinedload(PlanAnualSST.archivo))
        .filter(PlanAnualSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    normalizar_estado_y_avance(item)

    db.commit()
    db.refresh(item)

    return serializar(item)


@router.patch("/{item_id}/finalizar", response_model=PlanAnualResponse)
def finalizar_actividad(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = (
        db.query(PlanAnualSST)
        .options(joinedload(PlanAnualSST.archivo))
        .filter(PlanAnualSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    item.estado = "EJECUTADO"
    item.porcentaje_avance = 100

    db.commit()
    db.refresh(item)

    return serializar(item)


@router.post("/{item_id}/evidencia", response_model=PlanAnualResponse)
def subir_evidencia_plan_anual(
    item_id: int,
    descripcion: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    item = (
        db.query(PlanAnualSST)
        .filter(PlanAnualSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    resultado = guardar_evidencia_sst(
        file=file,
        modulo="plan-anual",
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
        modulo="PLAN_ANUAL",
        referencia_id=item.id,
        descripcion=descripcion or f"Evidencia Plan Anual SST {item.codigo}",
        activo=True,
    )

    db.add(archivo)
    db.commit()
    db.refresh(archivo)

    item.archivo_id = archivo.id
    item.evidencia = resultado["url"]

    db.commit()

    item = (
        db.query(PlanAnualSST)
        .options(joinedload(PlanAnualSST.archivo))
        .filter(PlanAnualSST.id == item_id)
        .first()
    )

    return serializar(item)


@router.delete("/{item_id}")
def eliminar_actividad(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    item = (
        db.query(PlanAnualSST)
        .filter(PlanAnualSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    item.activo = False
    db.commit()

    return {"mensaje": "Actividad del Plan Anual desactivada correctamente"}