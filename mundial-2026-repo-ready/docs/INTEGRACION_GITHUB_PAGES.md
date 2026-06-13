# Integración en tu repositorio mundial-2026

## Estructura a subir

Copia estas carpetas y archivos al repositorio:

```text
backend/
frontend/assets/js/api-config.js
frontend/assets/js/ai-client.js
frontend/chatbot.html
frontend/predicciones.html
model_local/
docs/
```

## Importante sobre GitHub Pages

GitHub Pages solo sirve HTML, CSS y JavaScript estático. No ejecuta Python.

Por tanto:

- Tu HTML se queda en GitHub Pages.
- El backend FastAPI se despliega en Replit, Render, Railway o similar.
- Tu frontend llama a la URL pública del backend.

## Despliegue recomendado

### Opción más rápida: Render Free

1. Crea un servicio web en Render.
2. Conecta tu repo o sube la carpeta `backend`.
3. Build command:

```bash
pip install -r requirements.txt
```

4. Start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

5. Ejecuta manualmente `POST /api/sync` una vez desplegado para generar JSON/CSV reales.

### Opción rápida para pruebas: Replit

1. Crea un Repl de Python.
2. Sube la carpeta `backend`.
3. Instala `requirements.txt`.
4. Ejecuta:

```bash
python scripts/update_data.py
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Configurar la web

En `frontend/assets/js/api-config.js`, cambia:

```js
const DEFAULT_API_BASE = "http://127.0.0.1:8000";
```

por tu URL real:

```js
const DEFAULT_API_BASE = "https://tu-api.onrender.com";
```

También puedes abrir la página con:

```text
chatbot.html?api=https://tu-api.onrender.com
```

La URL queda guardada en `localStorage`.

## Archivos que sustituyen a los existentes

Si quieres activar la IA en tus páginas actuales:

- Sustituye `chatbot.html` por `frontend/chatbot.html`.
- Sustituye `predicciones.html` por `frontend/predicciones.html`.
- Añade `assets/js/api-config.js` y `assets/js/ai-client.js`.
- Conserva tu `index.html` y `plantillas.html` actuales.

## Modelo local

El modelo local no es obligatorio.

- Para tablas y respuestas sencillas: API + JSON/CSV + reglas.
- Para chatbot abierto: modelo local GGUF con `llama-cpp-python` o LoRA entrenado.
