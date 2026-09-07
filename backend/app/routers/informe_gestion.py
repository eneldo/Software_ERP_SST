# ============================================================
# ROUTER FASTAPI - INFORME DE GESTIÓN SG-SST
#
# Endpoints REST para el módulo de Informe de Gestión.
#
# Ubicación: backend/app/routers/informe_gestion.py
# ============================================================

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.informe_gestion import (
    InformeGestionSGSST,
    InformeGestionSeccion,
    InformeGestionEvidencia,
    InformeGestionRecomendacion,
    InformeGestionAprobacion,
    RendicionCuentas,
    RendicionCuentasResponsabilidad,
)
from app.schemas.informe_gestion_schema import (
    InformeGestionCreate,
    InformeGestionUpdate,
    InformeGestionResponse,
    InformeGestionList,
    InformeGestionSeccionCreate,
    InformeGestionSeccionUpdate,
    InformeGestionSeccionResponse,
    InformeGestionEvidenciaCreate,
    InformeGestionEvidenciaResponse,
    InformeGestionRecomendacionCreate,
    InformeGestionRecomendacionUpdate,
    InformeGestionRecomendacionResponse,
    InformeGestionAprobacionCreate,
    InformeGestionAprobacionResponse,
    InformeGestionVersionResponse,
    ConsolidarInformeRequest,
    ConsolidarInformeResponse,
    PresentarInformeRequest,
    AprobarInformeRequest,
    RendicionCuentasCreate,
    RendicionCuentasUpdate,
    RendicionCuentasResponse,
    RendicionCuentasResponsabilidadCreate,
    RendicionCuentasResponsabilidadResponse,
)
from app.services.informe_gestion_service import InformeGestionService

router = APIRouter(
    prefix="/api/sgsst/informes-gestion",
    tags=["Informe de Gestión SG-SST"],
)


def _empresa_id_autorizada(
    usuario: Usuario, empresa_id: Optional[int] = None
) -> int:
    """Retorna el empresa_id autorizado para el usuario."""
    if usuario.rol == "SUPER_ADMIN":
        if empresa_id:
            return empresa_id
        return usuario.empresa_id
    return usuario.empresa_id


# ============================================================
# ENDPOINTS PRINCIPALES - INFORMES
# ============================================================


@router.get("", response_model=list[InformeGestionList])
def listar_informes(
    anio: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista informes de gestión de la empresa."""
    empresa_id = _empresa_id_autorizada(usuario)
    query = db.query(InformeGestionSGSST).filter(
        InformeGestionSGSST.empresa_id == empresa_id,
        InformeGestionSGSST.activo == True,
    )
    if anio:
        query = query.filter(InformeGestionSGSST.anio == anio)
    if estado:
        query = query.filter(InformeGestionSGSST.estado == estado)
    return (
        query.order_by(InformeGestionSGSST.fecha_creacion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("", response_model=InformeGestionResponse)
def crear_informe(
    payload: InformeGestionCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Crea un nuevo informe de gestión SG-SST."""
    empresa_id = _empresa_id_autorizada(usuario)
    servicio = InformeGestionService(db)
    informe = servicio.crear_informe(
        empresa_id=empresa_id,
        usuario_id=usuario.id,
        anio=payload.anio,
        sede_id=payload.sede_id,
    )
    if payload.responsable_sst_nombre:
        informe.responsable_sst_nombre = payload.responsable_sst_nombre
    if payload.representante_legal_nombre:
        informe.representante_legal_nombre = payload.representante_legal_nombre
    if payload.titulo:
        informe.titulo = payload.titulo
    db.commit()
    db.refresh(informe)
    return informe


@router.get("/{informe_id}", response_model=InformeGestionResponse)
def obtener_informe(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Obtiene un informe de gestión por ID."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return informe


@router.put("/{informe_id}", response_model=InformeGestionResponse)
def actualizar_informe(
    informe_id: int,
    payload: InformeGestionUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Actualiza datos de un informe (solo en BORRADOR o DEVUELTO)."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    if informe.estado not in ("BORRADOR", "DEVUELTO"):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede editar un informe en estado: {informe.estado}",
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(informe, field, value)
    db.commit()
    db.refresh(informe)
    return informe


@router.delete("/{informe_id}")
def eliminar_informe(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Elimina lógicamente un informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    if informe.estado not in ("BORRADOR",):
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden eliminar informes en BORRADOR",
        )
    informe.activo = False
    db.commit()
    return {"mensaje": "Informe eliminado exitosamente"}


# ============================================================
# CONSOLIDACIÓN DE DATOS
# ============================================================


@router.post("/{informe_id}/generar", response_model=ConsolidarInformeResponse)
def consolidar_informe(
    informe_id: int,
    payload: ConsolidarInformeRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Consolida todos los datos del SG-SST en el informe (snapshot histórico)."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    servicio = InformeGestionService(db)
    try:
        resultado = servicio.consolidar_datos(
            informe_id=informe_id, forzar=payload.forzar
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# FLUJO DE APROBACIÓN
# ============================================================


@router.post("/{informe_id}/presentar", response_model=InformeGestionResponse)
def presentar_informe(
    informe_id: int,
    payload: PresentarInformeRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Presenta el informe para revisión."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    servicio = InformeGestionService(db)
    try:
        return servicio.presentar_informe(informe_id, usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{informe_id}/aprobar", response_model=InformeGestionResponse)
def aprobar_informe(
    informe_id: int,
    payload: AprobarInformeRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Aprueba, aprueba con observaciones o devuelve el informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    servicio = InformeGestionService(db)
    try:
        return servicio.aprobar_informe(
            informe_id=informe_id,
            usuario_id=usuario.id,
            resultado=payload.resultado,
            observaciones=payload.observaciones,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{informe_id}/devolver", response_model=InformeGestionResponse)
def devolver_informe(
    informe_id: int,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Devuelve el informe para corrección."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    servicio = InformeGestionService(db)
    try:
        return servicio.aprobar_informe(
            informe_id=informe_id,
            usuario_id=usuario.id,
            resultado="DEVUELTO",
            observaciones=observaciones,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{informe_id}/cerrar", response_model=InformeGestionResponse)
def cerrar_informe(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Cierra el informe (solo si está aprobado)."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    servicio = InformeGestionService(db)
    try:
        return servicio.cerrar_informe(informe_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# DASHBOARD
# ============================================================


@router.get("/{informe_id}/dashboard")
def dashboard_informe(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna datos consolidados del informe para dashboard ejecutivo."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    datos = informe.datos_consolidados or {}
    secciones = (
        db.query(InformeGestionSeccion)
        .filter(
            InformeGestionSeccion.informe_id == informe_id,
            InformeGestionSeccion.activo == True,
        )
        .order_by(InformeGestionSeccion.orden)
        .all()
    )
    return {
        "informe": {
            "id": informe.id,
            "codigo": informe.codigo,
            "titulo": informe.titulo,
            "anio": informe.anio,
            "estado": informe.estado,
            "version": informe.version,
            "cumplimiento_global": float(informe.cumplimiento_global or 0),
            "cumplimiento_plan_anual": float(informe.cumplimiento_plan_anual or 0),
            "cumplimiento_estandares": float(informe.cumplimiento_estandares or 0),
            "fecha_generacion": str(informe.fecha_generacion)
            if informe.fecha_generacion
            else None,
        },
        "secciones": [
            {
                "codigo": s.codigo_seccion,
                "nombre": s.nombre_seccion,
                "estado": s.estado_seccion,
            }
            for s in secciones
        ],
        "resumen_ejecutivo": informe.resumen_ejecutivo,
        "indicadores_calculados": datos.get("indicadores_calculados", {}),
    }


# ============================================================
# SECCIONES DEL INFORME
# ============================================================


@router.get("/{informe_id}/secciones", response_model=list[InformeGestionSeccionResponse])
def listar_secciones(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista las secciones del informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return (
        db.query(InformeGestionSeccion)
        .filter(
            InformeGestionSeccion.informe_id == informe_id,
            InformeGestionSeccion.activo == True,
        )
        .order_by(InformeGestionSeccion.orden)
        .all()
    )


@router.put(
    "/{informe_id}/secciones/{seccion_id}",
    response_model=InformeGestionSeccionResponse,
)
def actualizar_seccion(
    informe_id: int,
    seccion_id: int,
    payload: InformeGestionSeccionUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Actualiza una sección del informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    seccion = (
        db.query(InformeGestionSeccion)
        .filter(
            InformeGestionSeccion.id == seccion_id,
            InformeGestionSeccion.informe_id == informe_id,
            InformeGestionSeccion.empresa_id == empresa_id,
        )
        .first()
    )
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(seccion, field, value)
    db.commit()
    db.refresh(seccion)
    return seccion


# ============================================================
# EVIDENCIAS
# ============================================================


@router.get(
    "/{informe_id}/evidencias",
    response_model=list[InformeGestionEvidenciaResponse],
)
def listar_evidencias(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista las evidencias del informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    return (
        db.query(InformeGestionEvidencia)
        .filter(
            InformeGestionEvidencia.informe_id == informe_id,
            InformeGestionEvidencia.empresa_id == empresa_id,
            InformeGestionEvidencia.activo == True,
        )
        .all()
    )


@router.post(
    "/{informe_id}/evidencias",
    response_model=InformeGestionEvidenciaResponse,
)
def crear_evidencia(
    informe_id: int,
    payload: InformeGestionEvidenciaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Agrega una evidencia al informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    evidencia = InformeGestionEvidencia(
        informe_id=informe_id,
        empresa_id=empresa_id,
        usuario_id=usuario.id,
        **payload.model_dump(),
    )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)
    return evidencia


@router.delete("/{informe_id}/evidencias/{evidencia_id}")
def eliminar_evidencia(
    informe_id: int,
    evidencia_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Elimina lógicamente una evidencia."""
    empresa_id = _empresa_id_autorizada(usuario)
    evidencia = (
        db.query(InformeGestionEvidencia)
        .filter(
            InformeGestionEvidencia.id == evidencia_id,
            InformeGestionEvidencia.informe_id == informe_id,
            InformeGestionEvidencia.empresa_id == empresa_id,
        )
        .first()
    )
    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    evidencia.activo = False
    db.commit()
    return {"mensaje": "Evidencia eliminada exitosamente"}


# ============================================================
# RECOMENDACIONES
# ============================================================


@router.get(
    "/{informe_id}/recomendaciones",
    response_model=list[InformeGestionRecomendacionResponse],
)
def listar_recomendaciones(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista las recomendaciones del informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    return (
        db.query(InformeGestionRecomendacion)
        .filter(
            InformeGestionRecomendacion.informe_id == informe_id,
            InformeGestionRecomendacion.empresa_id == empresa_id,
            InformeGestionRecomendacion.activo == True,
        )
        .all()
    )


@router.post(
    "/{informe_id}/recomendaciones",
    response_model=InformeGestionRecomendacionResponse,
)
def crear_recomendacion(
    informe_id: int,
    payload: InformeGestionRecomendacionCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Agrega una recomendación al informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    recomendacion = InformeGestionRecomendacion(
        informe_id=informe_id,
        empresa_id=empresa_id,
        usuario_id=usuario.id,
        **payload.model_dump(),
    )
    db.add(recomendacion)
    db.commit()
    db.refresh(recomendacion)
    return recomendacion


@router.put(
    "/{informe_id}/recomendaciones/{recomendacion_id}",
    response_model=InformeGestionRecomendacionResponse,
)
def actualizar_recomendacion(
    informe_id: int,
    recomendacion_id: int,
    payload: InformeGestionRecomendacionUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Actualiza una recomendación."""
    empresa_id = _empresa_id_autorizada(usuario)
    rec = (
        db.query(InformeGestionRecomendacion)
        .filter(
            InformeGestionRecomendacion.id == recomendacion_id,
            InformeGestionRecomendacion.informe_id == informe_id,
            InformeGestionRecomendacion.empresa_id == empresa_id,
        )
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recomendación no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rec, field, value)
    db.commit()
    db.refresh(rec)
    return rec


# ============================================================
# VERSIONES HISTÓRICAS
# ============================================================


@router.get(
    "/{informe_id}/versiones",
    response_model=list[InformeGestionVersionResponse],
)
def listar_versiones(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista el historial de versiones del informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    from app.models.informe_gestion import InformeGestionVersion

    return (
        db.query(InformeGestionVersion)
        .filter(InformeGestionVersion.informe_id == informe_id)
        .order_by(InformeGestionVersion.version_numero.desc())
        .all()
    )


# ============================================================
# RENDICIÓN DE CUENTAS
# ============================================================


@router.get(
    "/{informe_id}/rendiciones",
    response_model=list[RendicionCuentasResponse],
)
def listar_rendiciones(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista las rendiciones de cuentas del informe."""
    empresa_id = _empresa_id_autorizada(usuario)
    return (
        db.query(RendicionCuentas)
        .filter(
            RendicionCuentas.informe_id == informe_id,
            RendicionCuentas.empresa_id == empresa_id,
            RendicionCuentas.activo == True,
        )
        .all()
    )


@router.post(
    "/{informe_id}/rendiciones",
    response_model=RendicionCuentasResponse,
)
def crear_rendicion(
    informe_id: int,
    payload: RendicionCuentasCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Crea una rendición de cuentas."""
    empresa_id = _empresa_id_autorizada(usuario)
    rendicion = RendicionCuentas(
        informe_id=informe_id,
        empresa_id=empresa_id,
        usuario_id=usuario.id,
        **payload.model_dump(exclude={"informe_id"}),
    )
    db.add(rendicion)
    db.commit()
    db.refresh(rendicion)
    return rendicion


@router.put(
    "/{informe_id}/rendiciones/{rendicion_id}",
    response_model=RendicionCuentasResponse,
)
def actualizar_rendicion(
    informe_id: int,
    rendicion_id: int,
    payload: RendicionCuentasUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Actualiza una rendición de cuentas."""
    empresa_id = _empresa_id_autorizada(usuario)
    rendicion = (
        db.query(RendicionCuentas)
        .filter(
            RendicionCuentas.id == rendicion_id,
            RendicionCuentas.informe_id == informe_id,
            RendicionCuentas.empresa_id == empresa_id,
        )
        .first()
    )
    if not rendicion:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rendicion, field, value)
    db.commit()
    db.refresh(rendicion)
    return rendicion


@router.post(
    "/{informe_id}/rendiciones/{rendicion_id}/responsabilidades",
    response_model=RendicionCuentasResponsabilidadResponse,
)
def crear_responsabilidad_rendicion(
    informe_id: int,
    rendicion_id: int,
    payload: RendicionCuentasResponsabilidadCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Agrega una responsabilidad a una rendición de cuentas."""
    empresa_id = _empresa_id_autorizada(usuario)
    rendicion = (
        db.query(RendicionCuentas)
        .filter(
            RendicionCuentas.id == rendicion_id,
            RendicionCuentas.informe_id == informe_id,
            RendicionCuentas.empresa_id == empresa_id,
        )
        .first()
    )
    if not rendicion:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")
    resp = RendicionCuentasResponsabilidad(
        rendicion_id=rendicion_id,
        empresa_id=empresa_id,
        **payload.model_dump(),
    )
    db.add(resp)
    db.commit()
    db.refresh(resp)
    return resp


# ============================================================
# AUDITORÍA DEL INFORME
# ============================================================


@router.get("/{informe_id}/auditoria")
def auditoria_informe(
    informe_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna el historial de auditoría del informe (versiones y aprobaciones)."""
    empresa_id = _empresa_id_autorizada(usuario)
    informe = (
        db.query(InformeGestionSGSST)
        .filter(
            InformeGestionSGSST.id == informe_id,
            InformeGestionSGSST.empresa_id == empresa_id,
        )
        .first()
    )
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")

    from app.models.informe_gestion import InformeGestionVersion

    versiones = (
        db.query(InformeGestionVersion)
        .filter(InformeGestionVersion.informe_id == informe_id)
        .order_by(InformeGestionVersion.fecha_creacion.desc())
        .all()
    )
    aprobaciones = (
        db.query(InformeGestionAprobacion)
        .filter(InformeGestionAprobacion.informe_id == informe_id)
        .order_by(InformeGestionAprobacion.fecha_creacion.desc())
        .all()
    )
    return {
        "informe_id": informe_id,
        "codigo": informe.codigo,
        "version_actual": informe.version,
        "versiones": [
            {
                "version": v.version_numero,
                "estado": v.estado_nuevo,
                "motivo": v.motivo_cambio,
                "fecha": str(v.fecha_creacion) if v.fecha_creacion else None,
            }
            for v in versiones
        ],
        "aprobaciones": [
            {
                "tipo": a.tipo_accion,
                "resultado": a.resultado,
                "observaciones": a.observaciones,
                "fecha": str(a.fecha_creacion) if a.fecha_creacion else None,
            }
            for a in aprobaciones
        ],
    }
