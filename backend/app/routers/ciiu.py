# ============================================================
# ROUTER CIIU — Búsqueda de actividades económicas
# CIIU Rev. 4 A.C. (Colombia)
# ============================================================

import json
from pathlib import Path

from fastapi import APIRouter, Query


router = APIRouter(
    prefix="/ciiu",
    tags=["CIIU"],
)

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_CIIU_FILE = _DATA_DIR / "ciiu_rev4.json"

_CIIU_DATA: list[dict] = []


def _cargar_datos() -> list[dict]:
    global _CIIU_DATA
    if not _CIIU_DATA:
        with open(_CIIU_FILE, "r", encoding="utf-8") as f:
            _CIIU_DATA = json.load(f)
    return _CIIU_DATA


@router.get("/buscar")
def buscar_ciiu(q: str = Query(..., min_length=1, description="Código o palabra clave")):
    """
    Busca actividades económicas CIIU Rev. 4 A.C. por código o descripción.
    Retorna máximo 20 resultados.
    """
    datos = _cargar_datos()
    termino = q.lower().strip()

    resultados = []
    for item in datos:
        codigo = item["codigo"]
        descripcion = item["descripcion"]
        if termino in codigo or termino in descripcion.lower():
            resultados.append(item)
        if len(resultados) >= 20:
            break

    return resultados
