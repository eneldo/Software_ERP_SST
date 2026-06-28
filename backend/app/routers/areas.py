# ============================================================
# ROUTER ÁREAS - ERP SST PRO
# FASE 1.1.3 — ÁREAS SST ENTERPRISE 360°
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import get_db
from app.models.area import Area
from app.models.area_historial import AreaHistorialSST
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.schemas.area_schema import (
    AreaCreate,
    AreaUpdate,
    AreaResponse,
    AreaEnterpriseResponse,
)
from app.schemas.area_historial_schema import (
    AreaHistorialCreate,
    AreaHistorialUpdate,
    AreaHistorialResponse,
    AreaHistorialResumenResponse,
)
from app.auth.dependencies import require_roles


router = APIRouter(
    prefix="/areas",
    tags=["Áreas SST Enterprise"],
)


# ============================================================
# HELPERS
# ============================================================

def normalizar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None

    valor = valor.strip()
    return valor if valor else None


def validar_empresa(db: Session, empresa_id: int) -> Empresa:
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return empresa


def validar_sede(db: Session, sede_id: int | None, empresa_id: int | None = None) -> Sede | None:
    if sede_id is None:
        return None

    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    if empresa_id and sede.empresa_id != empresa_id:
        raise HTTPException(
            status_code=400,
            detail="La sede seleccionada no pertenece a la empresa indicada",
        )

    return sede


def area_to_enterprise_response(area: Area) -> AreaEnterpriseResponse:
    return AreaEnterpriseResponse(
        id=area.id,
        empresa_id=area.empresa_id,
        sede_id=area.sede_id,
        empresa_nombre=area.empresa.nombre if area.empresa else None,
        empresa_nit=area.empresa.nit if area.empresa else None,
        sede_nombre=area.sede.nombre if area.sede else None,
        sede_codigo=area.sede.codigo_sede if area.sede else None,
        sede_ciudad=area.sede.ciudad if area.sede else None,
        nombre=area.nombre,
        codigo_area=area.codigo_area,
        descripcion=area.descripcion,
        tipo_area=area.tipo_area,
        nivel_riesgo=area.nivel_riesgo,
        proceso_asociado=area.proceso_asociado,
        responsable_area=area.responsable_area,
        cargo_responsable=area.cargo_responsable,
        correo_responsable=area.correo_responsable,
        telefono_responsable=area.telefono_responsable,
        numero_empleados=area.numero_empleados or 0,
        activo=area.activo,
        fecha_creacion=area.fecha_creacion,
        fecha_actualizacion=area.fecha_actualizacion,
    )


def historial_to_response(evento: AreaHistorialSST) -> AreaHistorialResponse:
    return AreaHistorialResponse(
        id=evento.id,
        area_id=evento.area_id,
        tipo_evento=evento.tipo_evento,
        titulo=evento.titulo,
        descripcion=evento.descripcion,
        impacto_sst=evento.impacto_sst,
        estado_resultante=evento.estado_resultante,
        responsable=evento.responsable,
        evidencia_url=evento.evidencia_url,
        fecha_evento=evento.fecha_evento,
        fecha_creacion=evento.fecha_creacion,
        fecha_actualizacion=evento.fecha_actualizacion,
    )


def normalizar_upper(valor: str | None, defecto: str | None = None) -> str | None:
    limpio = normalizar_texto(valor)
    if not limpio:
        return defecto
    return limpio.upper()


# ============================================================
# CREAR ÁREA
# ============================================================

@router.post("/", response_model=AreaResponse)
def crear_area(
    data: AreaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    validar_empresa(db, data.empresa_id)
    validar_sede(db, data.sede_id, data.empresa_id)

    if data.codigo_area:
        existe_codigo = (
            db.query(Area)
            .filter(
                Area.empresa_id == data.empresa_id,
                Area.sede_id == data.sede_id,
                func.lower(Area.codigo_area) == data.codigo_area.lower(),
            )
            .first()
        )

        if existe_codigo:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un área con este código para la empresa/sede seleccionada",
            )

    area = Area(
        empresa_id=data.empresa_id,
        sede_id=data.sede_id,
        nombre=normalizar_texto(data.nombre),
        codigo_area=normalizar_texto(data.codigo_area),
        descripcion=normalizar_texto(data.descripcion),
        tipo_area=normalizar_texto(data.tipo_area) or "OPERATIVA",
        nivel_riesgo=normalizar_texto(data.nivel_riesgo) or "MEDIO",
        proceso_asociado=normalizar_texto(data.proceso_asociado),
        responsable_area=normalizar_texto(data.responsable_area),
        cargo_responsable=normalizar_texto(data.cargo_responsable),
        correo_responsable=str(data.correo_responsable) if data.correo_responsable else None,
        telefono_responsable=normalizar_texto(data.telefono_responsable),
        numero_empleados=data.numero_empleados or 0,
        activo=True,
    )

    db.add(area)
    db.commit()
    db.refresh(area)

    return area


# ============================================================
# LISTAR ÁREAS
# ============================================================

@router.get("/", response_model=list[AreaEnterpriseResponse])
def listar_areas(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    activo: bool | None = Query(default=None),
    tipo_area: str | None = Query(default=None),
    nivel_riesgo: str | None = Query(default=None),
    buscar: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    query = (
        db.query(Area)
        .join(Empresa, Empresa.id == Area.empresa_id)
        .outerjoin(Sede, Sede.id == Area.sede_id)
    )

    if empresa_id:
        query = query.filter(Area.empresa_id == empresa_id)

    if sede_id:
        query = query.filter(Area.sede_id == sede_id)

    if activo is not None:
        query = query.filter(Area.activo == activo)

    if tipo_area:
        query = query.filter(func.lower(Area.tipo_area) == tipo_area.lower())

    if nivel_riesgo:
        query = query.filter(func.lower(Area.nivel_riesgo) == nivel_riesgo.lower())

    if buscar:
        q = f"%{buscar.lower()}%"
        query = query.filter(
            or_(
                func.lower(Area.nombre).like(q),
                func.lower(Area.codigo_area).like(q),
                func.lower(Area.descripcion).like(q),
                func.lower(Area.proceso_asociado).like(q),
                func.lower(Area.responsable_area).like(q),
                func.lower(Empresa.nombre).like(q),
                func.lower(Empresa.nit).like(q),
                func.lower(Sede.nombre).like(q),
                func.lower(Sede.ciudad).like(q),
            )
        )

    areas = query.order_by(Area.id.desc()).all()

    return [area_to_enterprise_response(area) for area in areas]


# ============================================================
# DASHBOARD ÁREAS
# ============================================================

@router.get("/dashboard/resumen")
def dashboard_areas(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    query = db.query(Area)

    if empresa_id:
        query = query.filter(Area.empresa_id == empresa_id)

    if sede_id:
        query = query.filter(Area.sede_id == sede_id)

    areas = query.all()

    total_areas = len(areas)
    areas_activas = len([a for a in areas if a.activo])
    areas_inactivas = len([a for a in areas if not a.activo])
    total_empleados = sum(int(a.numero_empleados or 0) for a in areas)

    tipos_area = {}
    niveles_riesgo = {}
    procesos = {}

    for area in areas:
        tipo = area.tipo_area or "SIN CLASIFICAR"
        riesgo = area.nivel_riesgo or "SIN CLASIFICAR"
        proceso = area.proceso_asociado or "SIN PROCESO"

        tipos_area[tipo] = tipos_area.get(tipo, 0) + 1
        niveles_riesgo[riesgo] = niveles_riesgo.get(riesgo, 0) + 1
        procesos[proceso] = procesos.get(proceso, 0) + 1

    return {
        "total_areas": total_areas,
        "areas_activas": areas_activas,
        "areas_inactivas": areas_inactivas,
        "total_empleados": total_empleados,
        "tipos_area": tipos_area,
        "niveles_riesgo": niveles_riesgo,
        "procesos": procesos,
    }


# ============================================================
# FASE 1.1.3.4 — HISTÓRICO SST POR ÁREA
# ============================================================

@router.get("/{area_id}/historial", response_model=list[AreaHistorialResponse])
def listar_historial_area(
    area_id: int,
    tipo_evento: str | None = Query(default=None),
    impacto_sst: str | None = Query(default=None),
    estado_resultante: str | None = Query(default=None),
    buscar: str | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    query = db.query(AreaHistorialSST).filter(AreaHistorialSST.area_id == area_id)

    if tipo_evento:
        query = query.filter(func.lower(AreaHistorialSST.tipo_evento) == tipo_evento.lower())

    if impacto_sst:
        query = query.filter(func.lower(AreaHistorialSST.impacto_sst) == impacto_sst.lower())

    if estado_resultante:
        query = query.filter(func.lower(AreaHistorialSST.estado_resultante) == estado_resultante.lower())

    if buscar:
        q = f"%{buscar.lower()}%"
        query = query.filter(
            or_(
                func.lower(AreaHistorialSST.titulo).like(q),
                func.lower(AreaHistorialSST.descripcion).like(q),
                func.lower(AreaHistorialSST.responsable).like(q),
                func.lower(AreaHistorialSST.tipo_evento).like(q),
            )
        )

    eventos = (
        query.order_by(AreaHistorialSST.fecha_evento.desc(), AreaHistorialSST.id.desc())
        .limit(limite)
        .all()
    )

    return [historial_to_response(evento) for evento in eventos]


@router.post("/{area_id}/historial", response_model=AreaHistorialResponse)
def crear_historial_area(
    area_id: int,
    data: AreaHistorialCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    evento = AreaHistorialSST(
        area_id=area_id,
        tipo_evento=normalizar_upper(data.tipo_evento, "EVENTO SST"),
        titulo=normalizar_texto(data.titulo),
        descripcion=normalizar_texto(data.descripcion),
        impacto_sst=normalizar_upper(data.impacto_sst, "MEDIO"),
        estado_resultante=normalizar_upper(data.estado_resultante, "REGISTRADO"),
        responsable=normalizar_texto(data.responsable),
        evidencia_url=normalizar_texto(data.evidencia_url),
        fecha_evento=data.fecha_evento,
    )

    db.add(evento)
    db.commit()
    db.refresh(evento)

    return historial_to_response(evento)


@router.put("/historial/{evento_id}", response_model=AreaHistorialResponse)
def actualizar_historial_area(
    evento_id: int,
    data: AreaHistorialUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    evento = db.query(AreaHistorialSST).filter(AreaHistorialSST.id == evento_id).first()

    if not evento:
        raise HTTPException(status_code=404, detail="Evento histórico no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if isinstance(value, str):
            value = normalizar_texto(value)
            if key in {"tipo_evento", "impacto_sst", "estado_resultante"} and value:
                value = value.upper()
        setattr(evento, key, value)

    db.commit()
    db.refresh(evento)

    return historial_to_response(evento)


@router.delete("/historial/{evento_id}")
def eliminar_historial_area(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    evento = db.query(AreaHistorialSST).filter(AreaHistorialSST.id == evento_id).first()

    if not evento:
        raise HTTPException(status_code=404, detail="Evento histórico no encontrado")

    db.delete(evento)
    db.commit()

    return {"mensaje": "Evento histórico eliminado correctamente", "evento_id": evento_id}


@router.get("/{area_id}/historial/resumen", response_model=AreaHistorialResumenResponse)
def resumen_historial_area(
    area_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    eventos = (
        db.query(AreaHistorialSST)
        .filter(AreaHistorialSST.area_id == area_id)
        .order_by(AreaHistorialSST.fecha_evento.desc(), AreaHistorialSST.id.desc())
        .all()
    )

    eventos_por_tipo = {}
    eventos_por_impacto = {}
    eventos_abiertos = 0
    eventos_alto_impacto = 0

    for evento in eventos:
        tipo = evento.tipo_evento or "SIN TIPO"
        impacto = evento.impacto_sst or "SIN IMPACTO"
        estado = (evento.estado_resultante or "").upper()

        eventos_por_tipo[tipo] = eventos_por_tipo.get(tipo, 0) + 1
        eventos_por_impacto[impacto] = eventos_por_impacto.get(impacto, 0) + 1

        if impacto in {"ALTO", "CRÍTICO", "CRITICO"}:
            eventos_alto_impacto += 1

        if estado not in {"CERRADO", "FINALIZADO", "RESUELTO"}:
            eventos_abiertos += 1

    return AreaHistorialResumenResponse(
        total_eventos=len(eventos),
        eventos_alto_impacto=eventos_alto_impacto,
        eventos_abiertos=eventos_abiertos,
        ultimo_evento=historial_to_response(eventos[0]) if eventos else None,
        eventos_por_tipo=eventos_por_tipo,
        eventos_por_impacto=eventos_por_impacto,
    )


# ============================================================
# OBTENER ÁREA
# ============================================================

@router.get("/{area_id}", response_model=AreaEnterpriseResponse)
def obtener_area(
    area_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    return area_to_enterprise_response(area)


# ============================================================
# ACTUALIZAR ÁREA
# ============================================================

@router.put("/{area_id}", response_model=AreaResponse)
def actualizar_area(
    area_id: int,
    data: AreaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    update_data = data.model_dump(exclude_unset=True)

    nuevo_empresa_id = update_data.get("empresa_id", area.empresa_id)
    nuevo_sede_id = update_data.get("sede_id", area.sede_id)

    if "empresa_id" in update_data and update_data["empresa_id"]:
        validar_empresa(db, update_data["empresa_id"])

    if "sede_id" in update_data:
        validar_sede(db, nuevo_sede_id, nuevo_empresa_id)

    nuevo_codigo = update_data.get("codigo_area", area.codigo_area)

    if nuevo_codigo:
        existe_codigo = (
            db.query(Area)
            .filter(
                Area.id != area_id,
                Area.empresa_id == nuevo_empresa_id,
                Area.sede_id == nuevo_sede_id,
                func.lower(Area.codigo_area) == nuevo_codigo.lower(),
            )
            .first()
        )

        if existe_codigo:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otra área con este código para la empresa/sede seleccionada",
            )

    for key, value in update_data.items():
        if isinstance(value, str):
            value = normalizar_texto(value)

        if key == "correo_responsable" and value:
            value = str(value)

        setattr(area, key, value)

    db.commit()
    db.refresh(area)

    return area


# ============================================================
# ACTIVAR / DESACTIVAR ÁREA
# ============================================================

@router.patch("/{area_id}/estado", response_model=AreaResponse)
def cambiar_estado_area(
    area_id: int,
    activo: bool = Query(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    area.activo = activo
    db.commit()
    db.refresh(area)

    return area


# ============================================================
# ELIMINAR ÁREA LÓGICAMENTE
# ============================================================

@router.delete("/{area_id}")
def eliminar_area(
    area_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")

    area.activo = False
    db.commit()

    return {
        "mensaje": "Área desactivada correctamente",
        "area_id": area_id,
    }
