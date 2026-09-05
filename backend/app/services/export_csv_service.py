# ============================================================
# SERVICIO CSV CORPORATIVO SST
# Motor de Exportación Corporativo SST (complemento PDF/Excel)
# ============================================================

import csv
from datetime import datetime
from io import BytesIO, StringIO


def _nombre_generador(metadatos: dict) -> str:
    generador = metadatos.get("usuario_generador")
    if isinstance(generador, str) and generador.strip():
        return generador.strip()
    usuario = metadatos.get("usuario")
    if usuario is None:
        return "Sistema"
    nombre = f"{getattr(usuario, 'nombres', '') or ''} {getattr(usuario, 'apellidos', '') or ''}".strip()
    return nombre or f"Usuario {getattr(usuario, 'id', '')}" or "Sistema"


def generar_csv_corporativo(
    titulo: str,
    codigo: str,
    empresa,
    configuracion=None,
    columnas=None,
    filas=None,
    metadatos: dict | None = None,
):
    """
    Genera CSV corporativo reutilizable para SG-SST (UTF-8 con BOM).
    """
    columnas = columnas or []
    filas = filas or []
    metadatos = metadatos or {}

    prefijo = configuracion.prefijo_documental if configuracion else "SGSST"
    version = configuracion.version_documental if configuracion else "1.0"

    salida = StringIO()
    escritor = csv.writer(salida, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    escritor.writerow([getattr(empresa, "nombre", "")])
    escritor.writerow(
        [
            f"{titulo} | Código: {prefijo}-{codigo} | Versión: {version} | "
            f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]
    )
    escritor.writerow([f"Generado por: {_nombre_generador(metadatos)}"])
    if metadatos.get("filtros"):
        escritor.writerow([f"Filtros: {metadatos['filtros']}"])
    if metadatos.get("periodo"):
        escritor.writerow([f"Periodo: {metadatos['periodo']}"])
    escritor.writerow([])
    escritor.writerow(list(columnas))
    for fila in filas:
        escritor.writerow(["" if valor is None else valor for valor in fila])

    buffer = BytesIO(salida.getvalue().encode("utf-8-sig"))
    buffer.seek(0)
    return buffer
