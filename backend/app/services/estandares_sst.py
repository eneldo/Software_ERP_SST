# ============================================================
# ERP SST COLOMBIA
# SERVICIO GLOBAL: CLASIFICACIÓN ESTÁNDARES MÍNIMOS SG-SST
# Resolución 0312 de 2019
# ============================================================


def calcular_estandares_sst(
    numero_trabajadores: int,
    clase_riesgo: str,
    tipo_empresa: str = "EMPRESA",
) -> dict:
    trabajadores = int(numero_trabajadores or 1)
    riesgo = str(clase_riesgo or "I").upper().strip()
    tipo = str(tipo_empresa or "EMPRESA").upper().strip()

    if tipo == "AGROPECUARIA" and trabajadores <= 10 and riesgo in ["I", "II", "III"]:
        return {
            "tipo_estandares_sst": "3",
            "total_estandares_sst": 3,
            "descripcion_estandares_sst": "Unidad agropecuaria con 10 o menos trabajadores permanentes, riesgo I, II o III.",
        }

    if riesgo in ["IV", "V"]:
        return {
            "tipo_estandares_sst": "60",
            "total_estandares_sst": 60,
            "descripcion_estandares_sst": "Empresa de cualquier tamaño clasificada en riesgo IV o V.",
        }

    if trabajadores <= 10 and riesgo in ["I", "II", "III"]:
        return {
            "tipo_estandares_sst": "7",
            "total_estandares_sst": 7,
            "descripcion_estandares_sst": "Empresa con 10 o menos trabajadores, riesgo I, II o III.",
        }

    if 11 <= trabajadores <= 50 and riesgo in ["I", "II", "III"]:
        return {
            "tipo_estandares_sst": "21",
            "total_estandares_sst": 21,
            "descripcion_estandares_sst": "Empresa entre 11 y 50 trabajadores, riesgo I, II o III.",
        }

    return {
        "tipo_estandares_sst": "60",
        "total_estandares_sst": 60,
        "descripcion_estandares_sst": "Empresa con más de 50 trabajadores o condición que exige estándar completo.",
    }