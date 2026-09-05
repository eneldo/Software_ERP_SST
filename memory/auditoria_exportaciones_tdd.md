# Evidencia TDD — Exportaciones SST con tenant (H-021b)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-021b; auditoría Reportes (Sección 31).

## Recorridos
- Como ADMIN_EMPRESA de la empresa 1, no puedo exportar reportes de la empresa 2.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Helper rechaza otra empresa → 403 | `python -m unittest discover -s tests -p "test_exportaciones_tenant.py" -v` | Seguridad | RED ImportError (helper inexistente); GREEN 2/2 |
| Export objetivos ajena → 403 sin generar PDF | mismo comando | Seguridad | RED sin excepción; GREEN + PDF no generado |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 43 tests: 34 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/exportaciones_sst.py`: `_empresa_id_autorizada` + `obtener_empresa_y_configuracion(db, empresa_id, usuario)` con gate central; 10 call sites actualizados.
- `backend/tests/test_exportaciones_tenant.py`: nuevo, 2/2 GREEN.

## Brechas
- Falta CSV, metadatos de generación (usuario/filtros/período) y filtros de período en endpoints de lista.
