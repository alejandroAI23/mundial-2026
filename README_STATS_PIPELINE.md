# Sistema híbrido de estadísticas Mundial 2026

CSV + scraper SofaScore + edición manual.

## Uso

```bash
python backend/scripts/scrape_sofascore.py --match-id 12345678
python backend/scripts/scrape_sofascore.py --all-played
```

El chatbot puede leer estos CSVs mediante `backend/services/stats_query.py`.
