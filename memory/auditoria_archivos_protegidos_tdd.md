# Evidencia TDD — Descarga protegida con tenant (H-010 parcial)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-010; auditoría Documentos (DOC-041/DOC-062).

## Recorrido
- Como RESPONSABLE_SST de la empresa 1, no puedo descargar por path un archivo registrado de la empresa 2.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Descarga ajena → 403 | `python -m unittest discover -s tests -p "test_archivos_protegidos_tenant.py" -v` | Seguridad | RED 404 en vez de 403; GREEN 1/1 |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 47 tests: 38 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/archivos_protegidos.py`: en `servir_archivo_protegido`, verificación de `ArchivoSST.empresa_id` por `url`/`ruta` antes de servir (403 si ajeno; sin registro → comportamiento anterior; endpoints públicos de validación/logos intactos).
- `backend/tests/test_archivos_protegidos_tenant.py`: nuevo, 1/1 GREEN.

## Brechas
- Falta `hash_sha256`, endpoint de descarga con auditoría de accesos y permisos por tipo de archivo.
