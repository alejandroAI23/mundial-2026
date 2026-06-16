# Guía rápida: SofaScore visible a CSV

Esta guía sirve cuando SofaScore bloquea su API interna con `403 Forbidden`, pero tú sí puedes ver la tabla en la web.

## Objetivo

Evitar buscar jugador por jugador. La idea es copiar la tabla visible de SofaScore y convertirla a líneas CSV con una herramienta estática del propio repositorio.

## Herramienta

Abre esta página desde GitHub Pages:

```text
https://alejandroai23.github.io/mundial-2026/tools/sofascore-table-converter.html
```

También puedes abrir el archivo localmente:

```text
tools/sofascore-table-converter.html
```

## Pasos

1. Abre el partido en SofaScore.
2. Ve a `Alineaciones -> Estadísticas del jugador`.
3. Selecciona las filas visibles de la tabla.
4. Pulsa `Ctrl + C`.
5. Abre el conversor.
6. Rellena:
   - `partido_id`, por ejemplo `SWE-TUN-2026`.
   - `match_id`, por ejemplo `15186951`.
   - `fecha`, por ejemplo `2026-06-15`.
   - `local`, por ejemplo `Sweden`.
   - `visitante`, por ejemplo `Tunisia`.
   - `equipo de estas filas`, por ejemplo `Sweden`.
7. Pega la tabla copiada.
8. Pulsa `Convertir a CSV`.
9. Copia el bloque generado para `jugadores_stats.csv`, `disciplina.csv` o `partidos_motm.csv`.
10. Usa el formulario de GitHub Actions o edita los CSV si necesitas carga masiva.

## Importante

SofaScore cambia las columnas según la pestaña visible. Por eso el conversor genera una base rápida, pero debes revisar:

- goles
- asistencias
- minutos
- rating
- tarjetas
- faltas
- fueras de juego

Si quieres porteros, usa la pestaña `Portería` o introduce los datos con el workflow `Add manual advanced stats`.

## Ventaja

No se usa la API de SofaScore, así que no importa que devuelva `403 Forbidden`. Solo conviertes lo que ya ves en pantalla.
