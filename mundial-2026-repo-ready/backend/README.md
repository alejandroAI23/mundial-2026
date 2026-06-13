# Mundial 2026 AI API

Backend en Python/FastAPI para tu portal Mundial 2026.

## Qué hace

- Consume la API gratuita `https://worldcup26.ir/get`.
- Genera `data/worldcup_data.json`.
- Genera `data/worldcup_classification.csv`.
- Genera `data/worldcup_top_scorers.csv`.
- Expone endpoints para tu GitHub Pages:
  - `GET /api/clasificacion`
  - `GET /api/goleadores`
  - `GET /api/partidos`
  - `GET /api/equipos`
  - `GET /api/estadios`
  - `POST /api/qa`
  - `POST /api/sync`

## Uso local

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate
pip install -r requirements.txt
python scripts/update_data.py
uvicorn app:app --reload
```

Prueba:

```bash
curl http://127.0.0.1:8000/api/clasificacion
curl -X POST http://127.0.0.1:8000/api/qa -H "Content-Type: application/json" -d "{\"question\":\"¿quién es el máximo goleador?\"}"
```

## Modelo local: ¿necesario?

No es necesario para mostrar clasificación, goleadores o partidos. La API + JSON/CSV bastan.

Sí tiene sentido si quieres preguntas abiertas tipo chatbot. Aun así, la primera versión usa reglas sobre datos estructurados, porque es gratis, rápida y evita alucinaciones.

## Despliegue gratis o bajo coste

Opción rápida:

- Render Free Web Service o Replit.
- Subes esta carpeta `backend`.
- Comando de arranque: `uvicorn app:app --host 0.0.0.0 --port $PORT`.
- Luego configuras la URL en `frontend/assets/js/api-config.js`.
