# ============================================================
# SERVICE
# PLAN DE MEJORAMIENTO SST
# EVIDENCIAS
# FASE 1.5.7
# ============================================================

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.archivo_sst import ArchivoSST
from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.plan_mejoramiento_evidencia import (
    PlanMejoramientoEvidenciaSST,
)

from app.services.upload_service import guardar_evidencia_sst


# ============================================================
# VALIDACIONES
# ============================================================

def obtener_plan_o_404(
    db: Session,
    plan_id: int,
) -> PlanMejoramientoSST:

    plan = (
        db.query(PlanMejoramientoSST)
        .filter(
            PlanMejoramientoSST.id == plan_id,
            PlanMejoramientoSST.activo == True,
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan de mejoramiento no encontrado",
        )

    return plan


def obtener_evidencia_o_404(
    db: Session,
    evidencia_id: int,
) -> PlanMejoramientoEvidenciaSST:

    evidencia = (
        db.query(PlanMejoramientoEvidenciaSST)
        .filter(
            PlanMejoramientoEvidenciaSST.id == evidencia_id,
            PlanMejoramientoEvidenciaSST.activo == True,
        )
        .first()
    )

    if not evidencia:
        raise HTTPException(
            status_code=404,
            detail="Evidencia no encontrada",
        )

    return evidencia


# ============================================================
# SUBIR EVIDENCIA
# ============================================================

def subir_evidencia_plan(
    db: Session,
    plan_id: int,
    usuario_id: int,
    file: UploadFile,
    descripcion: str | None = None,
    tipo_evidencia: str = "CIERRE",
):

    plan = obtener_plan_o_404(
        db=db,
        plan_id=plan_id,
    )

    resultado = guardar_evidencia_sst(
        file=file,
        modulo="plan-mejoramiento",
        formato_imagen="webp",
    )

    archivo = ArchivoSST(
        
        empresa_id=plan.empresa_id,
        usuario_id=usuario_id,
        tipo="EVIDENCIA",
        nombre_original=file.filename,
        nombre_archivo=resultado["nombre_archivo"],
        ruta=resultado["ruta_fisica"],
        url=resultado["url"],
        extension=resultado["extension"],
        mime_type=resultado["mime_type"],
        tamano_bytes=resultado["tamano_bytes"],
        modulo="PLAN_MEJORAMIENTO",
        referencia_id=plan.id,
        descripcion=descripcion or f"Evidencia plan de mejoramiento {plan.codigo}",
        activo=True,
        
        
    )

    db.add(archivo)
    db.commit()
    db.refresh(archivo)

    evidencia = PlanMejoramientoEvidenciaSST(
        plan_id=plan.id,
        empresa_id=plan.empresa_id,
        usuario_id=usuario_id,
        archivo_id=archivo.id,
        tipo_evidencia=tipo_evidencia,
        descripcion=descripcion,
        url=resultado["url"],
        nombre_original=file.filename,
        extension=resultado["extension"],
        mime_type=resultado["mime_type"],
        tamano_bytes=resultado["tamano_bytes"],
        activo=True,
    )

    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)

    return evidencia


# ============================================================
# LISTAR EVIDENCIAS
# ============================================================

def listar_evidencias_plan(
    db: Session,
    plan_id: int,
):

    obtener_plan_o_404(
        db=db,
        plan_id=plan_id,
    )

    return (
        db.query(PlanMejoramientoEvidenciaSST)
        .filter(
            PlanMejoramientoEvidenciaSST.plan_id == plan_id,
            PlanMejoramientoEvidenciaSST.activo == True,
        )
        .order_by(
            PlanMejoramientoEvidenciaSST.id.desc()
        )
        .all()
    )


# ============================================================
# DETALLE
# ============================================================

def obtener_evidencia(
    db: Session,
    evidencia_id: int,
):
    return obtener_evidencia_o_404(
        db=db,
        evidencia_id=evidencia_id,
    )


# ============================================================
# ELIMINAR
# ============================================================

def eliminar_evidencia(
    db: Session,
    evidencia_id: int,
):

    evidencia = obtener_evidencia_o_404(
        db=db,
        evidencia_id=evidencia_id,
    )

    evidencia.activo = False

    if evidencia.archivo_id:

        archivo = (
            db.query(ArchivoSST)
            .filter(
                ArchivoSST.id == evidencia.archivo_id
            )
            .first()
        )

        if archivo:
            archivo.activo = False

    db.commit()

    return {
        "mensaje": "Evidencia eliminada correctamente"
    }


# ============================================================
# KPI
# ============================================================

def total_evidencias_plan(
    db: Session,
    plan_id: int,
):

    return (
        db.query(
            PlanMejoramientoEvidenciaSST
        )
        .filter(
            PlanMejoramientoEvidenciaSST.plan_id == plan_id,
            PlanMejoramientoEvidenciaSST.activo == True,
        )
        .count()
    )