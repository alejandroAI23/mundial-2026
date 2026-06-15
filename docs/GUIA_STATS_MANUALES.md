# Guía manual de estadísticas

Sistema híbrido: CSVs editables, scraper SofaScore y consultas pandas.

## Fuentes

- SofaScore: ratings, alineaciones, incidentes y estadísticas.
- BeSoccer: respaldo manual para goles y tarjetas.
- AS.com: respaldo manual en español.

## Checklist post-partido

1. Añadir el `match_id` a `backend/data/sofascore_matches.csv`.
2. Ejecutar el scraper.
3. Revisar los CSVs.
4. Probar el chatbot.

## Campos mínimos

- Jugadores: `partido_id`, `match_id`, `fecha`, `jugador`, `pais`, `minutos`, `goles`, `fecha_nacimiento`.
- Porteros: `partido_id`, `match_id`, `fecha`, `portero`, `pais`, `saves`, `goles_encajados`.
- Disciplina: `partido_id`, `match_id`, `fecha`, `jugador`, `pais`, `amarillas`, `rojas`, `faltas_cometidas`, `faltas_recibidas`.
