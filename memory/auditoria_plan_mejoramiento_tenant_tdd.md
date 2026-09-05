# Evidencia TDD — Planes de mejora con tenant (H-025, bloque 3)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-025; auditoría Planes de Mejoramiento (H-003).

## Recorrido
- Como RESPONSABLE_SST de la empresa 1, no puedo listar, ver el dashboard ni leer planes de la empresa 2.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Lectura ajena → 403/404 | `python -m unittest discover -s tests -p "test_plan_mejoramiento_tenant.py" -v` | Seguridad | RED 2 FAIL + 1 ERROR; GREEN 3/3 |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 81 tests: 72 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/plan_mejoramiento.py`: `_empresa_id_autorizada` + 403 en listar/dashboard + 404 en detalle ajeno (cerrar/verificar ya la usaban).
- `backend/tests/test_plan_mejoramiento_tenant.py`: nuevo, 3/3 GREEN.

## Brechas
- Falta tenant en generar y `responsable_id` como FK.

## Ampliación — escritura con tenant
- `crear_accion_mejoramiento` rechaza 403 otra empresa; `actualizar_accion_mejoramiento` verifica (id+empresa) con 404.
- `backend/tests/test_plan_mejoramiento_write_tenant.py`: RED (1 FAIL + 1 ERROR) → GREEN 2/2 OK.

## Cierre — suite 100% verde
- Mocks legacy de `test_auditoria_p0_epp_insp_med.py` reescritos (miss filtrado + asserts de condiciones): 13/13 OK.
- Suite completa: 83 tests OK, 0 fallos.
