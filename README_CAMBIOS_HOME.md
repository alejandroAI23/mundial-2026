# Cambios solicitados

Estructura propuesta:

- `index.html`: primera pantalla por defecto. Muestra resultados/calendario y chatbot integrado en la misma página.
- `clasificacion.html`: nueva página separada para la clasificación por grupos.
- `assets/js/api-config.js`: URL pública del backend Render.

## Subida a GitHub

Copia estos archivos en la raíz del repositorio:

```text
index.html
clasificacion.html
assets/js/api-config.js
```

Luego:

```bash
git add index.html clasificacion.html assets/js/api-config.js
git commit -m "Integra resultados y chatbot en pantalla principal"
git push origin main
```

## URLs esperadas

- Home: https://alejandroai23.github.io/mundial-2026/
- Clasificación: https://alejandroai23.github.io/mundial-2026/clasificacion.html
