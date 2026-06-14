# Integración IA Mundial 2026

Este paquete está preparado para copiarse directamente en la raíz del repositorio `mundial-2026`.

## Qué añade

- `backend/`: API FastAPI para clasificación, goleadores, partidos, equipos, estadios y QA.
- `backend/data/`: JSON y CSV iniciales.
- `backend/scripts/update_data.py`: sincronización con la API gratuita `worldcup26.ir`.
- `assets/js/api-config.js`: configuración de URL del backend para GitHub Pages.
- `assets/js/ai-client.js`: cliente JS para consumir la API desde el frontend.
- `chatbot.html`: página de asistente IA conectado al backend.
- `predicciones.html`: página de predicciones y estadísticas.
- `model_local/`: estructura base para dataset y entrenamiento LoRA/RAG.
- `docs/INTEGRACION_GITHUB_PAGES.md`: guía de despliegue.

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
