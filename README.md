# Integración IA Mundial 2026

Este paquete está preparado para copiarse directamente en la raíz del repositorio `mundial-2026`.

## Qué añade

- `backend/`: API FastAPI para clasificación, goleadores, partidos, equipos, estadios, rankings avanzados de jugadores y QA.
- `backend/data/`: JSON y CSV iniciales, incluida la caché `advanced_player_stats.json`.
- `backend/scripts/update_data.py`: sincronización con `worldcup26.ir` y, si está configurado, BALLDONTLIE.
- `assets/js/api-config.js`: configuración de URL del backend para GitHub Pages.
- `assets/js/ai-client.js`: cliente JS para consumir la API desde el frontend.
- `chatbot.html`: página de asistente IA conectado al backend.
- `predicciones.html`: página de predicciones y estadísticas.
- `model_local/`: estructura base para dataset y entrenamiento LoRA/RAG.
- `docs/INTEGRACION_GITHUB_PAGES.md`: guía de despliegue.

## BALLDONTLIE

El backend queda preparado para usar BALLDONTLIE FIFA World Cup API como segunda fuente de estadísticas avanzadas de jugadores.

Variables de entorno:

```bash
BALLDONTLIE_API_KEY=valor_de_tu_cuenta
BALLDONTLIE_SEASON=2026
BALLDONTLIE_PER_PAGE=100
BALLDONTLIE_MAX_PAGES=50
```

Importante: los endpoints avanzados pueden requerir trial o tier superior según tu cuenta. Si no hay clave o permisos, `/api/sync` no rompe el backend: mantiene los datos básicos de `worldcup26.ir` y deja el estado en `metadata.advanced_player_stats_status`.

Endpoint nuevo:

```bash
GET /api/jugadores/ranking?metric=youngest&limit=10
GET /api/jugadores/ranking?metric=yellow_cards&limit=10
GET /api/jugadores/ranking?metric=red_cards&limit=10
GET /api/jugadores/ranking?metric=minutes_played&limit=10
GET /api/jugadores/ranking?metric=fouls_committed&limit=10
GET /api/jugadores/ranking?metric=was_fouled&limit=10
GET /api/jugadores/ranking?metric=saves&limit=10
GET /api/jugadores/ranking?metric=substituted_out&limit=10
```

Preguntas soportadas por el chatbot cuando la caché avanzada esté sincronizada:

- jugador más joven
- más tarjetas amarillas
- más expulsiones o rojas
- más minutos jugados
- más faltas cometidas
- más faltas recibidas
- portero con más paradas
- jugador más sustituido

Limitaciones controladas:

- fuera de juego por jugador
- penaltis cometidos por jugador
- penaltis parados por portero
- portero con menos goles encajados

## Comandos de subida

```bash
git clone https://github.com/alejandroAI23/mundial-2026.git
cd mundial-2026
# copiar aquí el contenido de este paquete
git add .
git commit -m "Añade backend IA Mundial 2026, JSON CSV y modelo local"
git push origin main
```

## Ejecutar backend local

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/update_data.py
uvicorn app:app --reload
```

## Configurar GitHub Pages

Cuando despliegues el backend en Render/Replit, cambia en:

```text
assets/js/api-config.js
```

la URL local:

```js
http://127.0.0.1:8000
```

por la URL pública de tu backend.
