# Despliegue backend Mundial 2026 IA

## Opción recomendada: Render

Render encaja muy bien porque tu repositorio ya está en GitHub. El backend está dentro de la carpeta `backend/` y tiene `render.yaml`.

### Pasos

1. Sube esta carpeta al repositorio `alejandroAI23/mundial-2026`.
2. Entra en Render y crea un **New Web Service** desde GitHub.
3. Selecciona el repositorio `mundial-2026`.
4. Configura:
   - Root Directory: `backend`
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Variables de entorno:
   - `AUTO_SYNC_ON_STARTUP=false`
   - `CORS_ORIGINS=https://alejandroai23.github.io`
6. Deploy.
7. Abre `/docs` para probar Swagger.
8. Ejecuta `POST /api/sync` desde Swagger para poblar datos desde `worldcup26.ir`.
9. Copia la URL pública de Render y pégala en `assets/js/api-config.js`.

## Opción Replit

1. Crea una App Python en Replit.
2. Importa tu repo desde GitHub o sube la carpeta `backend/`.
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```
5. Usa Publish/Deployment para hacerlo público.

## Endpoints

- `GET /health`
- `GET /api/clasificacion`
- `GET /api/goleadores`
- `GET /api/partidos`
- `GET /api/equipos`
- `GET /api/estadios`
- `POST /api/qa`
- `POST /api/prediccion`
- `POST /api/sync`

## Modelo local

No lo actives en Render Free ni Replit básico. Para el caso actual, la IA basada en reglas + datos estructurados es más barata, rápida y fiable. El modelo local queda preparado en `backend/llm/local_llm.py` para una segunda fase en una máquina con más RAM/GPU.
