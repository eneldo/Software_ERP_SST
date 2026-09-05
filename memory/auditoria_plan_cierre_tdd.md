# Evidencia TDD — Cierre de plan con evidencia (H-022, bloque 3)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-022; auditoría Planes de Mejoramiento (Sección 19).

## Recorrido
- Como RESPONSABLE_SST, no puedo cerrar un plan de mejoramiento sin evidencia de cierre registrada.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Cierre sin evidencia → 400 | `python -m unittest discover -s tests -p "test_plan_cierre.py" -v` | Unitario | RED sin excepción; GREEN 2/2 |
| Cierre con evidencia → FINALIZADO/100/fecha | mismo comando | Unitario | GREEN |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 61 tests: 52 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/services/plan_mejoramiento_service.py`: `cerrar_plan` cuenta evidencias activas y exige ≥1 (400 si no).
- `backend/tests/test_plan_cierre.py`: nuevo, 2/2 GREEN.

## Brechas
- Falta `origen_hallazgo` + FKs de origen, verificación explícita (verificado_por/fecha/resultado) y `responsable_id` como FK.
