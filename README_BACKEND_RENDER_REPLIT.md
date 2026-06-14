# Backend Mundial 2026 para Render/Replit

Este paquete añade un backend FastAPI para tu repositorio `mundial-2026`.

## Qué añade

```text
backend/
assets/js/api-config.js
assets/js/ai-client.js
docs/RENDER_REPLIT_DEPLOY.md
```

## Comandos locales

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Prueba:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/clasificacion
```

Para sincronizar datos:

```bash
curl -X POST http://127.0.0.1:8000/api/sync
```

## Uso desde GitHub Pages

Cuando el backend esté desplegado, cambia en `assets/js/api-config.js`:

```js
window.MUNDIAL_2026_API_BASE = "https://tu-api.onrender.com";
```

## IA

El endpoint `POST /api/qa` ya responde consultas básicas sin modelo local:

- máximo goleador
- líder de grupo
- puntos de una selección
- ayuda

Esto es lo correcto para empezar porque evita alucinaciones y no cuesta dinero por token.
