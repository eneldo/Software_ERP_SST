# Evidencia TDD — Exportación CSV corporativa (H-021e, bloque 4)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-021e; PROMPT §31 (PDF/Excel/CSV).

## Recorrido
- Como RESPONSABLE_SST, exporto objetivos, plan anual y matriz legal en CSV con encabezado corporativo; otro tenant recibe 403.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| CSV con encabezado + datos | `python -m unittest discover -s tests -p "test_export_csv.py" -v` | Unitario | RED ImportError; GREEN 3/3 |
| Export ajena → 403 | mismo comando | Seguridad | GREEN |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 74 tests: 65 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/services/export_csv_service.py`: nuevo `generar_csv_corporativo` (UTF-8 BOM, delimitador `;`, encabezado empresa/código/versión/fecha).
- `backend/app/routers/exportaciones_sst.py`: `/objetivos/csv`, `/plan-anual/csv`, `/matriz-legal/csv` con tenant heredado del gate central.
- `backend/tests/test_export_csv.py`: nuevo, 3/3 GREEN.

## Brechas
- Falta CSV en el resto de módulos y filtros de período en endpoints de lista.

## Ampliación — metadatos de generación
- `generar_csv_corporativo(..., metadatos)` incluye `Generado por` y `Filtros`; los 3 endpoints pasan `{usuario, filtros}`.
- `backend/tests/test_csv_metadatos.py`: RED 2 ERROR → GREEN 2/2 OK.
- Suite: 76 tests, 67 OK; mismos 6 FAIL + 3 ERROR preexistentes por mocks.
