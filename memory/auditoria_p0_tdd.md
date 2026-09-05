# Evidencia TDD — Auditoría P0 CAPA, Incidentes e IPER

Fecha: 2026-09-04

## Recorridos

- Como responsable SST, puedo crear y seguir una medida correctiva sin errores por campos desalineados.
- Como usuario de una empresa, no puedo consultar recursos de incidentes ni filas IPER de otro tenant.
- Como responsable SST, puedo editar parcialmente una fila IPER sin alterar su valoración de riesgo vigente.
- Como operador, puedo instalar el esquema desde una base vacía sin colisiones del baseline dinámico.

## Evidencia

| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Los modelos CAPA aceptan todos los campos publicados por sus schemas | `python -m unittest discover -s tests -p "test_auditoria_p0.py" -v` | Unitario | RED por `invalid keyword argument`; GREEN 6/6 |
| Los listados hijos de incidentes rechazan otro tenant | `backend/tests/test_auditoria_p0.py` | Seguridad | RED sin excepción; GREEN HTTP 403 |
| IPER rechaza crear para otra empresa | `backend/tests/test_auditoria_p0.py` | Seguridad | RED sin excepción; GREEN HTTP 403 |
| El recálculo parcial conserva los valores almacenados | `backend/tests/test_auditoria_p0.py` | Unitario | RED por API ausente; GREEN `np=20`, `nr=500` |
| No hay regresiones en la suite backend | `python -m unittest discover -s tests -v` | Regresión | PASS 13/13 |
| Toda la cadena de migraciones funciona sobre una base vacía | `alembic upgrade head` con base PostgreSQL temporal | Integración | PASS hasta `e1f2a3b4c5d6` |
| Código Python compilable | `python -m compileall app tests alembic\\versions` | Estático | PASS |
| Diff sin errores de whitespace | `git diff --check` | Estático | PASS |

## Cobertura Y Brechas

- No existe configuración de cobertura Python en el proyecto; no se obtuvo porcentaje global.
- Las pruebas agregadas cubren los defectos reproducidos, pero no sustituyen una suite HTTP con base multiempresa real.
- No se realizaron commits de checkpoint porque el usuario no solicitó commits y el árbol ya contenía trabajo no relacionado.
