# ============================================================
# H-007: SCRIPT DE CARGA DE CRITERIOS RESOLUCIÓN 0312
# Ejecutar: python -m app.data.seed_criterios_res_0312
# ============================================================

"""
Carga los 60 numerales reales de la Resolución 0312 de 2019
en la tabla estandares_minimos_criterios.
Idempotente: no duplica si ya existen registros para el tipo '60'.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import inspect
from app.database import SessionLocal
from app.models.estandar_minimo_criterio import EstandarMinimoCriterio
from app.data.criterios_res_0312_60 import CRITERIOS_RES_0312_60_COMPLETOS


def seed_criterios():
    db = SessionLocal()
    try:
        insp = inspect(db.bind)
        if "estandares_minimos_criterios" not in insp.get_table_names():
            print("Tabla estandares_minimos_criterios no existe. Saltando seed.")
            return

        existentes = (
            db.query(EstandarMinimoCriterio)
            .filter(EstandarMinimoCriterio.tipo_estandares == "60")
            .count()
        )

        if existentes >= 60:
            print(f"Ya existen {existentes} criterios tipo 60. Seed no necesario.")
            return

        print(f"Cargando {len(CRITERIOS_RES_0312_60_COMPLETOS)} criterios Resolución 0312...")

        for criterio in CRITERIOS_RES_0312_60_COMPLETOS:
            existe = (
                db.query(EstandarMinimoCriterio)
                .filter(
                    EstandarMinimoCriterio.tipo_estandares == criterio["tipo_estandares"],
                    EstandarMinimoCriterio.numeral == criterio["numeral"],
                    EstandarMinimoCriterio.version_norma == "0312-2019",
                )
                .first()
            )
            if not existe:
                db.add(EstandarMinimoCriterio(**criterio))

        db.commit()
        total = (
            db.query(EstandarMinimoCriterio)
            .filter(EstandarMinimoCriterio.tipo_estandares == "60")
            .count()
        )
        print(f"Seed completado. Total criterios tipo 60: {total}")

    except Exception as e:
        db.rollback()
        print(f"Error en seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_criterios()
