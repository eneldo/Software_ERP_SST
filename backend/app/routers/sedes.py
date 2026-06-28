# ============================================================
# ROUTER SEDES - ERP SST PRO
# FASE 1.1.2.1 — SEDES SST ENTERPRISE 360°
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import get_db
from app.models.sede import Sede
from app.models.empresa import Empresa
from app.schemas.sede_schema import (
    SedeCreate,
    SedeUpdate,
    SedeResponse,
    SedeEnterpriseResponse,
)
from app.auth.dependencies import require_roles


router = APIRouter(
    prefix="/sedes",
    tags=["Sedes SST Enterprise"],
)


# ============================================================
# HELPERS
# ============================================================

def validar_empresa(db: Session, empresa_id: int) -> Empresa:
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    return empresa


def normalizar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None

    valor = valor.strip()

    return valor if valor else None


def sede_to_enterprise_response(sede: Sede) -> SedeEnterpriseResponse:
    return SedeEnterpriseResponse(
        id=sede.id,
        empresa_id=sede.empresa_id,
        empresa_nombre=sede.empresa.nombre if sede.empresa else None,
        empresa_nit=sede.empresa.nit if sede.empresa else None,
        nombre=sede.nombre,
        codigo_sede=sede.codigo_sede,
        tipo_sede=sede.tipo_sede,
        direccion=sede.direccion,
        ciudad=sede.ciudad,
        departamento=sede.departamento,
        telefono=sede.telefono,
        correo=sede.correo,
        responsable_sede=sede.responsable_sede,
        cargo_responsable=sede.cargo_responsable,
        numero_empleados=sede.numero_empleados or 0,
        activo=sede.activo,
        fecha_creacion=sede.fecha_creacion,
        fecha_actualizacion=sede.fecha_actualizacion,
    )


# ============================================================
# CREAR SEDE
# ============================================================

@router.post("/", response_model=SedeResponse)
def crear_sede(
    data: SedeCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    validar_empresa(db, data.empresa_id)

    if data.codigo_sede:
        existe_codigo = (
            db.query(Sede)
            .filter(
                Sede.empresa_id == data.empresa_id,
                func.lower(Sede.codigo_sede) == data.codigo_sede.lower(),
            )
            .first()
        )

        if existe_codigo:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una sede con este código para la empresa seleccionada",
            )

    sede = Sede(
        empresa_id=data.empresa_id,
        nombre=normalizar_texto(data.nombre),
        codigo_sede=normalizar_texto(data.codigo_sede),
        tipo_sede=normalizar_texto(data.tipo_sede) or "PRINCIPAL",
        direccion=normalizar_texto(data.direccion),
        ciudad=normalizar_texto(data.ciudad),
        departamento=normalizar_texto(data.departamento),
        telefono=normalizar_texto(data.telefono),
        correo=str(data.correo) if data.correo else None,
        responsable_sede=normalizar_texto(data.responsable_sede),
        cargo_responsable=normalizar_texto(data.cargo_responsable),
        numero_empleados=data.numero_empleados or 0,
        activo=True,
    )

    db.add(sede)
    db.commit()
    db.refresh(sede)

    return sede


# ============================================================
# LISTAR SEDES
# ============================================================

@router.get("/", response_model=list[SedeEnterpriseResponse])
def listar_sedes(
    empresa_id: int | None = Query(default=None),
    activo: bool | None = Query(default=None),
    ciudad: str | None = Query(default=None),
    departamento: str | None = Query(default=None),
    tipo_sede: str | None = Query(default=None),
    buscar: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    query = db.query(Sede).join(Empresa, Empresa.id == Sede.empresa_id)

    if empresa_id:
        query = query.filter(Sede.empresa_id == empresa_id)

    if activo is not None:
        query = query.filter(Sede.activo == activo)

    if ciudad:
        query = query.filter(func.lower(Sede.ciudad).like(f"%{ciudad.lower()}%"))

    if departamento:
        query = query.filter(func.lower(Sede.departamento).like(f"%{departamento.lower()}%"))

    if tipo_sede:
        query = query.filter(func.lower(Sede.tipo_sede) == tipo_sede.lower())

    if buscar:
        q = f"%{buscar.lower()}%"
        query = query.filter(
            or_(
                func.lower(Sede.nombre).like(q),
                func.lower(Sede.codigo_sede).like(q),
                func.lower(Sede.ciudad).like(q),
                func.lower(Sede.departamento).like(q),
                func.lower(Sede.responsable_sede).like(q),
                func.lower(Empresa.nombre).like(q),
                func.lower(Empresa.nit).like(q),
            )
        )

    sedes = query.order_by(Sede.id.desc()).all()

    return [sede_to_enterprise_response(sede) for sede in sedes]


# ============================================================
# DASHBOARD SEDES
# ============================================================

@router.get("/dashboard/resumen")
def dashboard_sedes(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    query = db.query(Sede)

    if empresa_id:
        query = query.filter(Sede.empresa_id == empresa_id)

    sedes = query.all()

    total_sedes = len(sedes)
    sedes_activas = len([s for s in sedes if s.activo])
    sedes_inactivas = len([s for s in sedes if not s.activo])
    total_empleados = sum(int(s.numero_empleados or 0) for s in sedes)

    ciudades = sorted(
        list({s.ciudad for s in sedes if s.ciudad})
    )

    tipos = {}
    for sede in sedes:
        tipo = sede.tipo_sede or "SIN CLASIFICAR"
        tipos[tipo] = tipos.get(tipo, 0) + 1

    return {
        "total_sedes": total_sedes,
        "sedes_activas": sedes_activas,
        "sedes_inactivas": sedes_inactivas,
        "total_empleados": total_empleados,
        "total_ciudades": len(ciudades),
        "ciudades": ciudades,
        "tipos_sede": tipos,
    }


# ============================================================
# OBTENER SEDE
# ============================================================

@router.get("/{sede_id}", response_model=SedeEnterpriseResponse)
def obtener_sede(
    sede_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=404,
            detail="Sede no encontrada",
        )

    return sede_to_enterprise_response(sede)


# ============================================================
# ACTUALIZAR SEDE
# ============================================================

@router.put("/{sede_id}", response_model=SedeResponse)
def actualizar_sede(
    sede_id: int,
    data: SedeUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=404,
            detail="Sede no encontrada",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "empresa_id" in update_data and update_data["empresa_id"]:
        validar_empresa(db, update_data["empresa_id"])

    nuevo_empresa_id = update_data.get("empresa_id", sede.empresa_id)
    nuevo_codigo = update_data.get("codigo_sede", sede.codigo_sede)

    if nuevo_codigo:
        existe_codigo = (
            db.query(Sede)
            .filter(
                Sede.id != sede_id,
                Sede.empresa_id == nuevo_empresa_id,
                func.lower(Sede.codigo_sede) == nuevo_codigo.lower(),
            )
            .first()
        )

        if existe_codigo:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otra sede con este código para la empresa seleccionada",
            )

    for key, value in update_data.items():
        if isinstance(value, str):
            value = normalizar_texto(value)

        if key == "correo" and value:
            value = str(value)

        setattr(sede, key, value)

    db.commit()
    db.refresh(sede)

    return sede


# ============================================================
# ACTIVAR / DESACTIVAR SEDE
# ============================================================

@router.patch("/{sede_id}/estado", response_model=SedeResponse)
def cambiar_estado_sede(
    sede_id: int,
    activo: bool = Query(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=404,
            detail="Sede no encontrada",
        )

    sede.activo = activo

    db.commit()
    db.refresh(sede)

    return sede


# ============================================================
# ELIMINAR SEDE LÓGICAMENTE
# ============================================================

@router.delete("/{sede_id}")
def eliminar_sede(
    sede_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=404,
            detail="Sede no encontrada",
        )

    sede.activo = False
    db.commit()

    return {
        "mensaje": "Sede desactivada correctamente",
        "sede_id": sede_id,
    }