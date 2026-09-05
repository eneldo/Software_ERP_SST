# Evidencia TDD — Criterios Res.0312 parametrizables (H-007, bloque 3)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-007; auditoría Estándares Mínimos (Sección 16).

## Recorrido
- Como AUDITOR, consulto el catálogo de criterios por tipo y recibo los vigentes desde BD; si la tabla está vacía, recibo la base normativa histórica.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Modelo acepta campos | `python -m unittest discover -s tests -p "test_estandares_criterios.py" -v` | Unitario | RED ModuleNotFoundError; GREEN 3/3 |
| Endpoint BD-primero + respaldo | mismo comando | Integración (mock) | GREEN |
| Migración local | `alembic upgrade head` → `b4c5d6e7f8a9 (head)` | Migración | PASS |
| Cadena limpia | `alembic upgrade head` en BD temporal | Integración | PASS 24 migraciones, BD eliminada |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 71 tests: 62 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/models/estandar_minimo_criterio.py`: nuevo (`estandares_minimos_criterios`, unique tipo/numeral/version).
- `backend/app/services/estandares_evaluacion_sst.py`: `obtener_criterios_parametrizados` (BD primero, constantes respaldo, orden numeral).
- `backend/app/routers/evaluacion_inicial.py`: `GET /criterios/{tipo}` (validado 3/7/21/60, declarado antes de `/{evaluacion_id}`).
- `backend/app/main.py`: registro del modelo.
- `backend/alembic/versions/20260904_0014_create_estandares_criterios.py`: nueva (`b4c5d6e7f8a9`).
- `backend/tests/test_estandares_criterios.py`: nuevo, 3/3 GREEN.

## Brechas
- Falta seed con los 60 numerales reales del anexo y CRUD admin de criterios.
