# Guía rápida: SofaScore visible a CSV

Esta guía sirve cuando SofaScore bloquea su API interna con `403 Forbidden`, pero tú sí puedes ver las tablas en la web.

## Herramienta

Abre esta página desde GitHub Pages:

```text
https://alejandroai23.github.io/mundial-2026/tools/sofascore-table-converter.html
```

También puedes abrir el archivo localmente:

```text
tools/sofascore-table-converter.html
```

## Objetivo

No buscar dato por dato. La idea es copiar cada pestaña visible de SofaScore y pegarla en una caja distinta:

```text
General
Atacante
Defensa
Pases
Duelos
Portería
```

El conversor fusiona los datos por jugador y genera automáticamente:

```text
jugadores_stats.csv
disciplina.csv
porteros_stats.csv
partidos_motm.csv
stats_json para el workflow Add manual advanced stats
```

## Pasos recomendados por partido

1. Abre el partido en SofaScore.
2. Ve a `Alineaciones -> Estadísticas del jugador`.
3. Entra en la pestaña `General`.
4. Selecciona las filas visibles de la tabla y pulsa `Ctrl + C`.
5. Pega el contenido en la caja `General` del conversor.
6. Repite lo mismo con:
   - `Atacante`
   - `Defensa`
   - `Pases`
   - `Duelos`
   - `Portería`
7. Rellena los datos del partido:
   - `partido_id`, por ejemplo `SWE-TUN-2026`.
   - `match_id`, por ejemplo `15186951`.
   - `fecha`, por ejemplo `2026-06-15`.
   - `local`, por ejemplo `Sweden`.
   - `visitante`, por ejemplo `Tunisia`.
8. Pulsa `Convertir todo`.
9. Revisa la vista previa fusionada.
10. Copia los bloques generados para cada CSV.

## Si no detecta bien el equipo

Cuando copias desde SofaScore, a veces el navegador no copia las banderas. En ese caso:

1. Pon `equipo por defecto si no detecta bandera = Local`.
2. Pega solo filas del equipo local y convierte.
3. Después cambia a `Visitante`.
4. Pega filas del visitante y convierte.

Si el copiado conserva la bandera, el conversor intentará detectar automáticamente el equipo.

## Qué datos saca cada pestaña

| Pestaña | Datos útiles |
|---|---|
| General | goles, asistencias, minutos y rating si aparece |
| Atacante | tiros a puerta, tiros fuera, tiros bloqueados, regates |
| Defensa | intercepciones, entradas, despejes, tiros bloqueados |
| Pases | pases clave, centros, pases largos, pases precisos |
| Duelos | faltas cometidas, faltas recibidas, fueras de juego, posición, rating |
| Portería | paradas, goles evitados, puños, salidas por alto, rating |

## Importante

SofaScore cambia columnas según el tamaño de pantalla, idioma o pestaña. Revisa siempre en la vista previa:

- goles
- asistencias
- minutos
- rating
- faltas
- fueras de juego
- paradas de portero

## Ventaja

No se usa la API de SofaScore, así que no importa que devuelva `403 Forbidden`. Solo conviertes lo que ya ves en pantalla.
