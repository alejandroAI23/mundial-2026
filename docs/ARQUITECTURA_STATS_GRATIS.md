# Arquitectura gratuita de estadisticas Mundial 2026

## Objetivo

Evitar APIs premium y mantener el chatbot funcionando con una combinacion estable:

```text
Datos basicos automaticos + estadisticas avanzadas por formulario GitHub Actions
```

## Capa 1: automatica gratis

Esta capa alimenta datos que no requieren API premium.

| Dato | Fuente actual/recomendada | Estado |
|---|---|---|
| partidos | backend / worldcup26.ir | Automatico |
| resultados | backend / worldcup26.ir | Automatico |
| clasificacion | backend / worldcup26.ir | Automatico |
| goleadores basicos | backend / worldcup26.ir | Automatico |
| equipos | backend / worldcup26.ir | Automatico |
| plantillas | frontend/backend actual + Wikipedia cuando aplique | Semiautomatico |
| entrenadores | plantillas/fuentes publicas | Semiautomatico |
| edad / jugador mas joven | CSV `jugadores_stats.csv` con `fecha_nacimiento` | Por formulario |

Workflow relacionado:

```text
Sync API Football Cache
```

Aunque el nombre diga API Football, este workflow llama al endpoint `/api/sync` de Render. El backend mantiene datos basicos desde la fuente gratuita disponible y deja las estadisticas avanzadas como opcionales.

## Capa 2: estadisticas avanzadas sin API premium

SofaScore bloquea el scraping automatico desde GitHub Actions con 403 Forbidden. Por eso, las metricas avanzadas se cargan por formulario en GitHub Actions.

Workflow nuevo:

```text
Add manual advanced stats
```

Actualiza automaticamente estos CSV:

```text
backend/data/jugadores_stats.csv
backend/data/disciplina.csv
backend/data/porteros_stats.csv
backend/data/partidos_motm.csv
```

## Preguntas cubiertas

### Automaticas basicas

```text
partidos
proximos partidos
resultados
clasificacion
goleadores basicos
equipos
plantillas
entrenadores
```

### Avanzadas por formulario

```text
mas tarjetas amarillas
mas tarjetas rojas
jugador mas joven
mas faltas cometidas
mas faltas recibidas
mas fueras de juego
portero con mas paradas
portero menos goleado
mejor jugador del partido
resumen de jugador
```

## Flujo recomendado despues de cada partido

1. El backend sincroniza resultados y clasificacion con `/api/sync`.
2. Revisas SofaScore/FIFA/AS/BeSoccer visualmente.
3. Abres `Actions -> Add manual advanced stats -> Run workflow`.
4. Rellenas un jugador importante o todas las estadisticas que quieras guardar.
5. El Action actualiza CSVs y hace commit automatico.
6. El chatbot consulta los CSVs con `backend/services/stats_query.py`.

## Ventajas

- Sin pagos.
- Sin depender de scraping bloqueado.
- Editable desde movil.
- CSVs versionados en GitHub.
- El chatbot no se cae si una fuente externa falla.

## Limitacion

Las metricas avanzadas requieren carga guiada. No hay una fuente gratuita estable que permita automatizar todas esas estadisticas sin bloqueo o sin plan premium.
