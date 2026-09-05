# Evidencia TDD — Exportación platinum con tenant (H-021d)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-021d; auditoría Reportes (Sección 31).

## Recorrido
- Como AUDITOR de la empresa 1, no puedo exportar el PDF platinum de una inspección de otra empresa (404 sin generar el PDF).

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Export ajena → 404 y no genera PDF | `python -m unittest discover -s tests -p "test_platinum_export_tenant.py" -v` | Seguridad | RED sin excepción; GREEN 1/1 + servicio no llamado + 2 condiciones en filtro |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 46 tests: 37 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/inspecciones_exportaciones_platinum.py`: `_empresa_id_autorizada` + verificación previa `(id, empresa_id)` antes de `generar_reporte_inspeccion_platinum_pdf`.
- `backend/tests/test_platinum_export_tenant.py`: nuevo, 1/1 GREEN.

## Brechas
- Resto de exportaciones de auditoría/revisión/capa con el mismo patrón pendientes de verificación.
