from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.permiso import Permiso

logger = logging.getLogger("app.permissions")

PERM_REPORTES_EXPORTAR = "REPORTES_EXPORTAR"
PERM_REGISTROS_ELIMINAR = "REGISTROS_ELIMINAR"
PERM_USUARIOS_GESTIONAR = "USUARIOS_GESTIONAR"
PERM_DOCUMENTOS_APROBAR = "DOCUMENTOS_APROBAR"
PERM_EXAMENES_DESCARGAR = "EXAMENES_DESCARGAR"
PERM_PERMISOS_GESTIONAR = "PERMISOS_GESTIONAR"
PERM_HISTORIA_CLINICA = "HISTORIA_CLINICA_ACCEDER"
PERM_CONCEPTO_MEDICO = "CONCEPTO_MEDICO_VER"


DEFAULT_PERMISSIONS = (
    {
        "codigo": PERM_REPORTES_EXPORTAR,
        "nombre": "Exportar reportes",
        "modulo": "REPORTES",
        "descripcion": "Permite exportar reportes PDF, Excel y descargas ejecutivas.",
    },
    {
        "codigo": PERM_REGISTROS_ELIMINAR,
        "nombre": "Eliminar registros",
        "modulo": "SEGURIDAD",
        "descripcion": "Permite eliminar o desactivar registros críticos del sistema.",
    },
    {
        "codigo": PERM_USUARIOS_GESTIONAR,
        "nombre": "Gestionar usuarios",
        "modulo": "USUARIOS",
        "descripcion": "Permite crear, modificar, activar, desactivar y consultar usuarios del sistema.",
    },
    {
        "codigo": PERM_DOCUMENTOS_APROBAR,
        "nombre": "Aprobar documentos",
        "modulo": "DOCUMENTAL",
        "descripcion": "Permite aprobar o rechazar documentos en flujos documentales.",
    },
    {
        "codigo": PERM_EXAMENES_DESCARGAR,
        "nombre": "Descargar exámenes médicos",
        "modulo": "EXAMENES",
        "descripcion": "Permite descargar o exportar información y evidencias de exámenes médicos.",
    },
    {
        "codigo": PERM_PERMISOS_GESTIONAR,
        "nombre": "Gestionar permisos",
        "modulo": "SEGURIDAD",
        "descripcion": "Permite crear permisos y asignarlos a usuarios.",
    },
    {
        "codigo": PERM_HISTORIA_CLINICA,
        "nombre": "Acceder historia clínica",
        "modulo": "MEDICINA_LABORAL",
        "descripcion": "Permite acceder a información clínica detallada (restricciones, observaciones, diagnósticos). Solo personal médico autorizado.",
    },
    {
        "codigo": PERM_CONCEPTO_MEDICO,
        "nombre": "Ver concepto médico",
        "modulo": "MEDICINA_LABORAL",
        "descripcion": "Permite ver el concepto de aptitud (APTO/NO_APTO) sin acceso a detalle clínico.",
    },
)


def ensure_default_permissions(db: Session) -> None:
    existing = {
        codigo
        for (codigo,) in db.query(Permiso.codigo)
        .filter(Permiso.codigo.in_([item["codigo"] for item in DEFAULT_PERMISSIONS]))
        .all()
    }

    for item in DEFAULT_PERMISSIONS:
        if item["codigo"] not in existing:
            db.add(Permiso(**item, activo=True))

    db.commit()


def ensure_default_permissions_on_startup() -> None:
    db = SessionLocal()
    try:
        ensure_default_permissions(db)
    except Exception:
        db.rollback()
        logger.exception("No fue posible inicializar permisos base")
    finally:
        db.close()
