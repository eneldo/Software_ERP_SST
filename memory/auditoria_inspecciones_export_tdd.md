# Evidencia TDD — Exportaciones inspecciones con tenant (H-021c)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-021c; auditoría Reportes (Sección 31).

## Recorridos
- Como RESPONSABLE_SST de la empresa 1, no puedo exportar inspecciones ni hallazgos de la empresa 2.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Export otra empresa → 403 | `python -m unittest discover -s tests -p "test_inspecciones_export_tenant.py" -v` | Seguridad | RED 2 FAIL; GREEN 2/2 |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 45 tests: 36 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/inspecciones_exportaciones.py`: `_empresa_id_autorizada` en excel-general, hallazgos-excel/pdf, pdf-general, pdf-individual, acta-pdf, seguimientos-pdf, dashboard-ejecutivo-pdf; `_get_inspeccion(db, id, empresa)`; hallazgos y seguimientos filtrados por empresa de la inspección.
- `backend/tests/test_inspecciones_export_tenant.py`: nuevo, 2/2 GREEN.

## Brechas
- Falta CSV, metadatos de generación y límites/paginación real en exportaciones.
