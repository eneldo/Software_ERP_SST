# ============================================================
# ROUTER MATRIZ LEGAL SST
# FASE 1.8.5.2 - MATRIZ LEGAL SST BI EXECUTIVE
# Mantiene CRUD, evidencias, exportaciones y agrega dashboard BI
# Archivo: backend/app/routers/matriz_legal.py
# ============================================================

from datetime import date, timedelta
from collections import Counter, defaultdict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles

from app.models.empresa import Empresa
from app.models.archivo_sst import ArchivoSST
from app.models.matriz_legal import MatrizLegalSST
from app.models.matriz_legal_historial import MatrizLegalHistorial

from app.services.upload_service import guardar_evidencia_sst

from app.schemas.matriz_legal_schema import (
    MatrizLegalCreate,
    MatrizLegalUpdate,
    MatrizLegalResponse,
    MatrizLegalResumenResponse,
    MatrizLegalDashboardResponse,
    MatrizLegalBIResponse,
)


router = APIRouter(
    prefix="/planear/matriz-legal",
    tags=["PLANEAR - Matriz Legal SST PRO"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


NORMAS_BASE_SST = [
    {
        "codigo": "ML-SST-001",
        "norma": "Decreto 1072 de 2015",
        "tipo_norma": "Decreto",
        "numero_norma": "1072",
        "anio": "2015",
        "articulo": "Libro 2, Parte 2, Título 4, Capítulo 6",
        "requisito_legal": "Implementar el Sistema de Gestión de Seguridad y Salud en el Trabajo SG-SST.",
        "tema": "Sistema de Gestión SST",
        "entidad_emisora": "Ministerio del Trabajo",
    },
    {
        "codigo": "ML-SST-002",
        "norma": "Resolución 0312 de 2019",
        "tipo_norma": "Resolución",
        "numero_norma": "0312",
        "anio": "2019",
        "articulo": "Estándares mínimos",
        "requisito_legal": "Cumplir con los estándares mínimos del Sistema de Gestión de Seguridad y Salud en el Trabajo.",
        "tema": "Estándares mínimos",
        "entidad_emisora": "Ministerio del Trabajo",
    },
    {
        "codigo": "ML-SST-003",
        "norma": "Ley 1562 de 2012",
        "tipo_norma": "Ley",
        "numero_norma": "1562",
        "anio": "2012",
        "articulo": "Sistema General de Riesgos Laborales",
        "requisito_legal": "Actualizar el Sistema General de Riesgos Laborales y promover la prevención de riesgos laborales.",
        "tema": "Riesgos laborales",
        "entidad_emisora": "Congreso de Colombia",
    },
    {
        "codigo": "ML-SST-004",
        "norma": "Resolución 2013 de 1986",
        "tipo_norma": "Resolución",
        "numero_norma": "2013",
        "anio": "1986",
        "articulo": "COPASST",
        "requisito_legal": "Conformar y mantener activo el Comité Paritario de Seguridad y Salud en el Trabajo.",
        "tema": "COPASST",
        "entidad_emisora": "Ministerio de Trabajo y Seguridad Social",
    },
    {
        "codigo": "ML-SST-005",
        "norma": "Resolución 1409 de 2012",
        "tipo_norma": "Resolución",
        "numero_norma": "1409",
        "anio": "2012",
        "articulo": "Trabajo en alturas",
        "requisito_legal": "Implementar el reglamento de seguridad para protección contra caídas en trabajo en alturas.",
        "tema": "Trabajo en alturas",
        "entidad_emisora": "Ministerio del Trabajo",
    },
]


def serializar(item: MatrizLegalSST):
    archivo = item.archivo

    return {
        "id": item.id,
        "empresa_id": item.empresa_id,
        "usuario_id": item.usuario_id,
        "archivo_id": item.archivo_id,
        "codigo": item.codigo,
        "norma": item.norma,
        "tipo_norma": item.tipo_norma,
        "numero_norma": item.numero_norma,
        "anio": item.anio,
        "articulo": item.articulo,
        "requisito_legal": item.requisito_legal,
        "tema": item.tema,
        "entidad_emisora": item.entidad_emisora,
        "aplicabilidad": item.aplicabilidad,
        "estado_cumplimiento": item.estado_cumplimiento,
        "estado_norma": item.estado_norma,
        "responsable": item.responsable,
        "fecha_revision": item.fecha_revision,
        "fecha_vencimiento": item.fecha_vencimiento,
        "evidencia": item.evidencia,
        "observaciones": item.observaciones,
        "archivo_url": archivo.url if archivo else None,
        "archivo_nombre": archivo.nombre_original if archivo else None,
        "archivo_extension": archivo.extension if archivo else None,
        "activo": item.activo,
        "fecha_creacion": item.fecha_creacion,
        "fecha_actualizacion": item.fecha_actualizacion,
    }


def _items_empresa(db: Session, empresa_id: int):
    return (
        db.query(MatrizLegalSST)
        .options(joinedload(MatrizLegalSST.archivo))
        .filter(
            MatrizLegalSST.empresa_id == empresa_id,
            MatrizLegalSST.activo == True,
        )
        .all()
    )


def _riesgo_legal(porcentaje: int, no_cumplen: int, vencidas_revision: int, sin_evidencia: int) -> str:
    """
    Calcula un nivel simple para el panel ejecutivo:
    ALTO: bajo cumplimiento o no conformidades.
    MEDIO: cumplimiento intermedio o faltantes documentales.
    BAJO: control estable.
    """
    if porcentaje < 70 or no_cumplen > 0 or vencidas_revision > 0:
        return "ALTO"
    if porcentaje < 90 or sin_evidencia > 0:
        return "MEDIO"
    return "BAJO"


def _dashboard_payload(items: list[MatrizLegalSST]):
    hoy = date.today()
    limite_revision = hoy + timedelta(days=30)

    total = len(items)
    cumplen = len([i for i in items if i.estado_cumplimiento == "CUMPLE"])
    pendientes = len([i for i in items if i.estado_cumplimiento == "PENDIENTE"])
    no_cumplen = len([i for i in items if i.estado_cumplimiento == "NO_CUMPLE"])

    vigentes = len([i for i in items if i.estado_norma == "VIGENTE"])
    derogadas = len([i for i in items if i.estado_norma == "DEROGADA"])
    modificadas = len([i for i in items if i.estado_norma == "MODIFICADA"])

    sin_evidencia = len([i for i in items if not i.archivo_id and not i.evidencia])
    con_evidencia = total - sin_evidencia

    sin_responsable = len([i for i in items if not (i.responsable or "").strip()])
    responsables_unicos = {
        (i.responsable or "").strip()
        for i in items
        if (i.responsable or "").strip()
    }

    revisiones = []
    vencidas_revision = 0

    for item in items:
        fechas = []
        if item.fecha_revision:
            fechas.append(("Revisión", item.fecha_revision))
        if item.fecha_vencimiento:
            fechas.append(("Vencimiento", item.fecha_vencimiento))

        for tipo, fecha_item in fechas:
            dias = (fecha_item - hoy).days

            if dias < 0:
                vencidas_revision += 1

            if 0 <= dias <= 30:
                revisiones.append(
                    {
                        "id": item.id,
                        "codigo": item.codigo,
                        "norma": item.norma,
                        "fecha": fecha_item,
                        "dias": dias,
                        "tipo": tipo,
                    }
                )

    proximas_revision_items = sorted(revisiones, key=lambda x: x["dias"])[:8]
    proximas_revision = len(proximas_revision_items)

    porcentaje_cumplimiento = round((cumplen / total) * 100) if total > 0 else 0
    porcentaje_evidencias = round((con_evidencia / total) * 100) if total > 0 else 0

    tipo_counter = Counter([(i.tipo_norma or "Sin tipo").strip() or "Sin tipo" for i in items])
    cumplimiento_counter = Counter([(i.estado_cumplimiento or "SIN_EVALUAR").strip() for i in items])
    estado_counter = Counter([(i.estado_norma or "SIN_ESTADO").strip() for i in items])

    # Temas críticos: requisitos pendientes o no conformes agrupados por tema.
    temas_counter = Counter()
    for item in items:
        if item.estado_cumplimiento in ["PENDIENTE", "NO_CUMPLE"]:
            temas_counter[(item.tema or "Sin tema").strip() or "Sin tema"] += 1

    responsables_counter = Counter()
    for item in items:
        nombre = (item.responsable or "").strip()
        if nombre:
            responsables_counter[nombre] += 1

    # Tendencia basada en el mes de creación de los registros disponibles.
    por_mes = defaultdict(lambda: {"total": 0, "cumplen": 0})
    for item in items:
        fecha_base = item.fecha_creacion.date() if item.fecha_creacion else hoy
        mes = fecha_base.strftime("%Y-%m")
        por_mes[mes]["total"] += 1
        if item.estado_cumplimiento == "CUMPLE":
            por_mes[mes]["cumplen"] += 1

    tendencia = []
    for mes in sorted(por_mes.keys())[-6:]:
        data = por_mes[mes]
        tendencia.append(
            {
                "mes": mes,
                "cumplimiento": round((data["cumplen"] / data["total"]) * 100)
                if data["total"]
                else 0,
            }
        )

    if not tendencia:
        tendencia = [{"mes": hoy.strftime("%Y-%m"), "cumplimiento": porcentaje_cumplimiento}]

    riesgo = _riesgo_legal(
        porcentaje=porcentaje_cumplimiento,
        no_cumplen=no_cumplen,
        vencidas_revision=vencidas_revision,
        sin_evidencia=sin_evidencia,
    )

    return {
        "total": total,
        "cumplen": cumplen,
        "pendientes": pendientes,
        "no_cumplen": no_cumplen,
        "vigentes": vigentes,
        "derogadas": derogadas,
        "modificadas": modificadas,
        "sin_evidencia": sin_evidencia,
        "con_evidencia": con_evidencia,
        "sin_responsable": sin_responsable,
        "responsables": len(responsables_unicos),
        "proximas_revision": proximas_revision,
        "vencidas_revision": vencidas_revision,
        "porcentaje_cumplimiento": porcentaje_cumplimiento,
        "porcentaje_evidencias": porcentaje_evidencias,
        "riesgo_legal": riesgo,
        "por_tipo_norma": [
            {"nombre": nombre, "total": total_item}
            for nombre, total_item in tipo_counter.most_common()
        ],
        "por_cumplimiento": [
            {"nombre": nombre, "total": total_item}
            for nombre, total_item in cumplimiento_counter.most_common()
        ],
        "por_estado_norma": [
            {"nombre": nombre, "total": total_item}
            for nombre, total_item in estado_counter.most_common()
        ],
        "temas_criticos": [
            {"nombre": nombre, "total": total_item}
            for nombre, total_item in temas_counter.most_common(8)
        ],
        "responsables_top": [
            {"nombre": nombre, "total": total_item}
            for nombre, total_item in responsables_counter.most_common(8)
        ],
        "proximas_revision_items": proximas_revision_items,
        "tendencia_cumplimiento": tendencia,
    }


@router.post("/", response_model=MatrizLegalResponse)
def crear_requisito_legal(
    data: MatrizLegalCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    item = MatrizLegalSST(**data.model_dump(), usuario_id=usuario.id)

    db.add(item)
    db.commit()
    db.refresh(item)

    item = (
        db.query(MatrizLegalSST)
        .options(joinedload(MatrizLegalSST.archivo))
        .filter(MatrizLegalSST.id == item.id)
        .first()
    )

    return serializar(item)


@router.post("/cargar-base/{empresa_id}")
def cargar_base_normativa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    creados = 0

    for norma in NORMAS_BASE_SST:
        existe = (
            db.query(MatrizLegalSST)
            .filter(
                MatrizLegalSST.empresa_id == empresa_id,
                MatrizLegalSST.codigo == norma["codigo"],
            )
            .first()
        )

        if existe:
            continue

        item = MatrizLegalSST(
            empresa_id=empresa_id,
            usuario_id=usuario.id,
            aplicabilidad="APLICA",
            estado_cumplimiento="PENDIENTE",
            estado_norma="VIGENTE",
            **norma,
        )

        db.add(item)
        creados += 1

    db.commit()

    return {
        "mensaje": "Base normativa cargada correctamente",
        "creados": creados,
    }


@router.get("/", response_model=list[MatrizLegalResponse])
def listar_matriz_legal(
    empresa_id: int | None = None,
    tema: str | None = None,
    estado_cumplimiento: str | None = None,
    estado_norma: str | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    query = (
        db.query(MatrizLegalSST)
        .options(joinedload(MatrizLegalSST.archivo))
        .filter(MatrizLegalSST.activo == True)
    )

    if empresa_id:
        query = query.filter(MatrizLegalSST.empresa_id == empresa_id)

    if tema:
        query = query.filter(MatrizLegalSST.tema.ilike(f"%{tema}%"))

    if estado_cumplimiento:
        query = query.filter(MatrizLegalSST.estado_cumplimiento == estado_cumplimiento)

    if estado_norma:
        query = query.filter(MatrizLegalSST.estado_norma == estado_norma)

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            MatrizLegalSST.norma.ilike(patron)
            | MatrizLegalSST.requisito_legal.ilike(patron)
            | MatrizLegalSST.tema.ilike(patron)
            | MatrizLegalSST.codigo.ilike(patron)
        )

    items = query.order_by(MatrizLegalSST.id.desc()).all()

    return [serializar(item) for item in items]


@router.get("/resumen/{empresa_id}", response_model=MatrizLegalResumenResponse)
def resumen_matriz_legal(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    items = _items_empresa(db, empresa_id)

    total = len(items)
    cumplen = len([i for i in items if i.estado_cumplimiento == "CUMPLE"])
    pendientes = len([i for i in items if i.estado_cumplimiento == "PENDIENTE"])
    no_cumplen = len([i for i in items if i.estado_cumplimiento == "NO_CUMPLE"])
    vigentes = len([i for i in items if i.estado_norma == "VIGENTE"])
    derogadas = len([i for i in items if i.estado_norma == "DEROGADA"])

    porcentaje = round((cumplen / total) * 100) if total > 0 else 0

    return {
        "total": total,
        "cumplen": cumplen,
        "pendientes": pendientes,
        "no_cumplen": no_cumplen,
        "vigentes": vigentes,
        "derogadas": derogadas,
        "porcentaje_cumplimiento": porcentaje,
    }


@router.get("/dashboard/{empresa_id}", response_model=MatrizLegalDashboardResponse)
def dashboard_matriz_legal(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    items = _items_empresa(db, empresa_id)
    return _dashboard_payload(items)


@router.get("/bi/{empresa_id}", response_model=MatrizLegalBIResponse)
def bi_matriz_legal(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    items = _items_empresa(db, empresa_id)
    return _dashboard_payload(items)


@router.get("/{item_id}", response_model=MatrizLegalResponse)
def obtener_requisito_legal(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    item = (
        db.query(MatrizLegalSST)
        .options(joinedload(MatrizLegalSST.archivo))
        .filter(MatrizLegalSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Requisito legal no encontrado")

    return serializar(item)


@router.put("/{item_id}", response_model=MatrizLegalResponse)
def actualizar_requisito_legal(
    item_id: int,
    data: MatrizLegalUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = (
        db.query(MatrizLegalSST)
        .options(joinedload(MatrizLegalSST.archivo))
        .filter(MatrizLegalSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Requisito legal no encontrado")

    valores_anteriores = {
        "norma": item.norma,
        "estado_norma": item.estado_norma,
        "aplicabilidad": item.aplicabilidad,
        "estado_cumplimiento": item.estado_cumplimiento,
        "requisito_legal": item.requisito_legal,
    }

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.flush()

    cambios_detectados = []
    for campo, valor_anterior in valores_anteriores.items():
        valor_nuevo = getattr(item, campo, None)
        if str(valor_anterior or "") != str(valor_nuevo or ""):
            cambios_detectados.append(f"{campo}: '{valor_anterior}' → '{valor_nuevo}'")

    if cambios_detectados:
        tipo_cambio = "MODIFICACION"
        if data.estado_norma and data.estado_norma.upper() == "DEROGADA":
            tipo_cambio = "DEROGACION"
        elif data.estado_norma and data.estado_norma.upper() == "SUSPENDIDA":
            tipo_cambio = "SUSPENSION"

        historial = MatrizLegalHistorial(
            matriz_legal_id=item.id,
            empresa_id=item.empresa_id,
            usuario_id=usuario.id,
            tipo_cambio=tipo_cambio,
            descripcion_cambio="; ".join(cambios_detectados),
            valor_anterior=str(valores_anteriores),
            valor_nuevo=str(data.model_dump(exclude_unset=True)),
            norma_anterior=valores_anteriores.get("norma"),
            estado_norma_anterior=valores_anteriores.get("estado_norma"),
            estado_norma_nuevo=item.estado_norma,
            motivo=data.observaciones if hasattr(data, 'observaciones') else None,
            fecha_efectiva=data.fecha_revision if hasattr(data, 'fecha_revision') else None,
        )
        db.add(historial)

    db.commit()
    db.refresh(item)

    return serializar(item)


@router.post("/{item_id}/evidencia", response_model=MatrizLegalResponse)
def subir_evidencia_matriz_legal(
    item_id: int,
    descripcion: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    item = (
        db.query(MatrizLegalSST)
        .filter(MatrizLegalSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Requisito legal no encontrado")

    resultado = guardar_evidencia_sst(
        file=file,
        modulo="matriz-legal",
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
        modulo="MATRIZ_LEGAL",
        referencia_id=item.id,
        descripcion=descripcion or f"Evidencia matriz legal {item.codigo}",
        activo=True,
    )

    db.add(archivo)
    db.commit()
    db.refresh(archivo)

    item.archivo_id = archivo.id
    item.evidencia = resultado["url"]

    db.commit()

    item = (
        db.query(MatrizLegalSST)
        .options(joinedload(MatrizLegalSST.archivo))
        .filter(MatrizLegalSST.id == item_id)
        .first()
    )

    return serializar(item)


@router.delete("/{item_id}")
def eliminar_requisito_legal(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    item = (
        db.query(MatrizLegalSST)
        .filter(MatrizLegalSST.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Requisito legal no encontrado")

    item.activo = False
    db.commit()

    return {"mensaje": "Requisito legal desactivado correctamente"}


@router.get("/{item_id}/historial")
def listar_historial_norma(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    item = db.query(MatrizLegalSST).filter(MatrizLegalSST.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Requisito legal no encontrado")

    historiales = (
        db.query(MatrizLegalHistorial)
        .filter(
            MatrizLegalHistorial.matriz_legal_id == item_id,
            MatrizLegalHistorial.activo == True,
        )
        .order_by(MatrizLegalHistorial.fecha_creacion.desc())
        .all()
    )

    return [
        {
            "id": h.id,
            "tipo_cambio": h.tipo_cambio,
            "descripcion_cambio": h.descripcion_cambio,
            "valor_anterior": h.valor_anterior,
            "valor_nuevo": h.valor_nuevo,
            "norma_anterior": h.norma_anterior,
            "estado_norma_anterior": h.estado_norma_anterior,
            "estado_norma_nuevo": h.estado_norma_nuevo,
            "motivo": h.motivo,
            "fecha_efectiva": h.fecha_efectiva,
            "fecha_creacion": h.fecha_creacion,
        }
        for h in historiales
    ]


# ============================================================
# H-018: ALERTAS DE VENCIMIENTO
# ============================================================

@router.post("/alertas-vencimiento/{empresa_id}")
def generar_alertas_vencimiento(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    from app.services.alertas_matriz_legal_service import generar_alertas_vencimiento_legal

    alertas = generar_alertas_vencimiento_legal(db, empresa_id)
    return {
        "mensaje": f"Se generaron {len(alertas)} alertas",
        "alertas": alertas,
    }


@router.get("/alertas-resumen/{empresa_id}")
def resumen_alertas(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    from app.services.alertas_matriz_legal_service import contar_alertas_activas

    return contar_alertas_activas(db, empresa_id)
