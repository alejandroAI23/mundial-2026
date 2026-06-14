# Cambios de navegación y home

Este paquete mantiene `index.html` como la primera pantalla por defecto del proyecto.

## Resultado final

- `index.html`: página principal. Muestra resultados/calendario y chatbot integrado en la misma pantalla.
- `clasificacion.html`: página separada para clasificación por grupos.
- `inicio.html`: se mantiene como página de inicio/portada ya existente en la raíz. No se sobrescribe.
- `plantillas.html`: se mantiene como página de plantillas.
- `predicciones.html`: se mantiene como página de predicciones.
- `assets/js/api-config.js`: apunta al backend de Render.

## Navegación incluida

La navegación superior queda así en `index.html` y `clasificacion.html`:

```text
Inicio -> inicio.html
Resultados + Chatbot -> index.html
Clasificación -> clasificacion.html
Plantillas -> plantillas.html
Predicciones -> predicciones.html
```

## Archivos que debes subir

Copia estos archivos en la raíz del repositorio:

```text
index.html
clasificacion.html
assets/js/api-config.js
```

No he incluido `inicio.html` para no pisar la página que ya tienes creada.

## Comandos Git

```bash
git add index.html clasificacion.html assets/js/api-config.js
git commit -m "Ajusta navegación principal y separa clasificación"
git push origin main
```

## URLs para comprobar

```text
https://alejandroai23.github.io/mundial-2026/
https://alejandroai23.github.io/mundial-2026/inicio.html
https://alejandroai23.github.io/mundial-2026/clasificacion.html
https://alejandroai23.github.io/mundial-2026/plantillas.html
https://alejandroai23.github.io/mundial-2026/predicciones.html
```
