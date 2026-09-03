# Análisis Plantilla Excel IPER 2026

## Archivo: `Modelo_Matriz IPER 2026.xlsx`

### Hojas
1. **ADMINISTRATIVA** — A1:AE1000, font 10pt
2. **OPERATIVO** — A1:AJ1043, font 12pt, columnas extra de seguimiento
3. **METODOLOGIA** — A1:Z749, referencia/methodology
4. **Hoja1** — B4:K64, lista de tareas administrativas

### Estructura de datos (rows 8-9)

#### Row 8 — Encabezados de grupo (celdas combinadas)
| Grupo | Columnas | Merge |
|-------|----------|-------|
| PROCESO | A | A8:A9 |
| ZONA/LUGAR | B | B8:B9 |
| ACTIVIDADES | C | C8:C9 |
| TAREAS | D | D8:D9 |
| RUTINARIA | E | E8:E9 |
| PELIGRO | F-G | F8:G8 |
| RIESGO | H | H8:H9 |
| EFECTOS POSIBLES | I | I8:I9 |
| CONTROLES EXISTENTES | J-L | J8:L8 |
| EVALUACION DE RIESGOS | M-T | M8:T8 |
| CRITERIOS CONTROLES | U-X | U8:X8 |
| MEDIDAS INTERVENCION | Y-AC | Y8:AC8 |
| SEGUIMIENTO *(solo OPERATIVO)* | AD-AH | AE8:AG8 |
| INDICADOR *(solo OPERATIVO)* | AI-AJ | AH8:AI8 |

#### Row 9 — Sub-encabezados
| Col | Header |
|-----|--------|
| F | CLASIFICACION |
| G | DESCRIPCION |
| J | FUENTE |
| K | MEDIO |
| L | INDIVIDUO |
| M | NIVEL DE DEFICIENCIA |
| N | NIVEL DE EXPOSICION |
| O | NIVEL DE PROBABILIDAD |
| P | INTERPRETACION DEL NIVEL DE PROBABILIDAD |
| Q | NIVEL DE CONSECUENCIA |
| R | NIVEL DEL RIESGO |
| S | INTERPRETACION DEL NIVEL DEL RIESGO |
| T | ACEPTABILIDAD DEL RIESGO |
| U | Nro. EXPUESTOS HOMBRES |
| V | Nro. EXPUESTOS MUJERES |
| W | Nro. EXPUESTOS Mujeres Gestantes/Lactantes |
| X | PEOR CONSECUENCIA |
| Y | ELIMINACION |
| Z | CONTROLODE INGENIERIA |
| AA | SUSTITUCION |
| AB | SEÑALIZACION. ADVERTENCIA, CONTROLES ADMINISTRACION |
| AC | EQUIPOS / ELEMENTOS DE PROTECCION PERSONAL |
| AD | Responsable *(OPERATIVO)* |
| AE | fecha proyectada *(OPERATIVO)* |
| AF | fecha ejecucion *(OPERATIVO)* |
| AG | Evidencias *(OPERATIVO)* |
| AH | Realizado *(OPERATIVO)* |
| AI | No Realizado *(OPERATIVO)* |

### Formato
- **Fondo headers:** #A8D08D (verde)
- **Font:** Times New Roman bold
- **Bordes:** Medios en headers, thin en datos
- **Alineación:** Center horizontal y vertical, wrap_text
- **Metadatos:** Rows 1-6 (título, versión, autor, fechas)

### Fórmulas (columnas calculadas)
- O = M × N (NP)
- P = IF sobre O → BAJO/MEDIO/ALTO/MUY ALTO
- R = O × Q (NR)
- S = IF sobre R → I/II/III/IV
- T = IF sobre S → ACEPTABLE/MEJORABLE/etc.

### Anchos de columna (ADMINISTRATIVA)
| Col | Width | Col | Width |
|-----|-------|-----|-------|
| A | 9.0 | N | 10.4 |
| B | 8.4 | O | 12.6 |
| C | 8.9 | P | 12.9 |
| D | 8.4 | Q | 7.0 |
| E | 7.9 | R | 11.1 |
| F | 15.6 | S | 17.4 |
| G | 30.6 | T | 10.6 |
| H | 17.6 | U | 15.1 |
| I | 14.1 | V | 15.1 |
| J | 12.4 | X | 22.0 |
| K | 12.9 | Y | 18.4 |
| L | 12.0 | Z | 21.9 |
| M | 14.1 | AA | 20.0 |
| | | AB | 37.0 |
| | | AC | 21.4 |
| | | AD | 11.4 |
| | | AE | 23.0 |
