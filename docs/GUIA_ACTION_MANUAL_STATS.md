# Guia Action manual de estadisticas avanzadas

Este workflow evita editar CSV a mano. Se usa desde GitHub Actions y actualiza automaticamente los CSV que lee el chatbot.

Workflow:

```text
Actions -> Add manual advanced stats -> Run workflow
```

## Campos del formulario

| Campo | Ejemplo | Notas |
|---|---|---|
| partido_id | SWE-TUN-2026 | ID interno claro |
| match_id | 15186951 | ID SofaScore o ID interno |
| fecha | 2026-06-15 | Formato YYYY-MM-DD |
| local | Sweden | Nombre tecnico en ingles |
| visitante | Tunisia | Nombre tecnico en ingles |
| jugador | A. Isak | Nombre como quieras verlo |
| pais | Sweden | Seleccion del jugador |
| rival | Tunisia | Seleccion rival |
| stats_json | Ver ejemplos | Metricas del jugador |

## JSON minimo para jugador de campo

```json
{"posicion":"Forward","titular":true,"minutos":90,"goles":1,"asistencias":0,"amarillas":0,"rojas":0,"faltas_cometidas":1,"faltas_recibidas":2,"fueras_juego":1,"rating":8.6,"motm":true}
```

## JSON para portero

```json
{"posicion":"Goalkeeper","es_portero":true,"titular":true,"minutos":90,"saves":5,"goles_encajados":1,"porterias_cero":0,"penaltis_parados":0,"rating":7.4}
```

## JSON para jugador joven

Para que el chatbot pueda responder quien es el jugador mas joven, anade fecha de nacimiento:

```json
{"posicion":"Midfielder","titular":true,"minutos":76,"goles":0,"fecha_nacimiento":"2005-04-12","rating":7.1}
```

## Que CSV actualiza

El formulario actualiza siempre:

```text
backend/data/jugadores_stats.csv
backend/data/disciplina.csv
```

Si pones `"es_portero": true`, tambien actualiza:

```text
backend/data/porteros_stats.csv
```

Si pones `"motm": true`, tambien actualiza:

```text
backend/data/partidos_motm.csv
```

## Dedupe

Si ejecutas dos veces el workflow para el mismo `match_id` y `jugador`, el script actualiza la fila existente en vez de crear duplicados.

Para MOTM, solo puede haber uno por `match_id`. Si marcas otro jugador con `"motm": true`, reemplaza el anterior.

## Ejemplo completo Suecia vs Tunez

Formulario:

```text
partido_id: SWE-TUN-2026
match_id: 15186951
fecha: 2026-06-15
local: Sweden
visitante: Tunisia
jugador: A. Isak
pais: Sweden
rival: Tunisia
```

stats_json:

```json
{"posicion":"Forward","titular":true,"minutos":90,"goles":1,"asistencias":0,"amarillas":0,"rojas":0,"faltas_cometidas":1,"faltas_recibidas":2,"fueras_juego":1,"rating":8.6,"motm":true}
```

## Comprobacion

Despues de ejecutar el workflow, revisa el Summary. Debe indicar que hay filas reales en:

```text
jugadores_stats.csv
disciplina.csv
partidos_motm.csv
```

Tambien puedes abrir los CSV y buscar `es_ejemplo=false`.
