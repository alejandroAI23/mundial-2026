# Guía: páginas SofaScore por partido

## Objetivo

En vez de usar un único conversor genérico, ahora existe una carpeta con una ficha HTML por partido:

```text
tools/sofascore-partidos/
```

Cada ficha abre el conversor SofaScore con estos datos ya precargados:

```text
partido_id
match_id
fecha
local
visitante
```

Así, cuando un partido finaliza, solo tienes que copiar las tablas visibles de SofaScore y pegarlas en la ficha del partido.

## URL principal

Cuando GitHub Pages actualice, abre:

```text
https://alejandroai23.github.io/mundial-2026/tools/sofascore-partidos/
```

Desde ahí eliges el partido.

## Flujo recomendado

### 1. Añadir partido finalizado

Edita:

```text
backend/data/sofascore_matches.csv
```

Añade una fila:

```csv
partido_id,match_id,fecha,local,visitante,estado,fuente,es_ejemplo
GER-CUW-2026,15186899,2026-06-14,Germany,Curacao,finalizado,manual,false
```

### 2. Generar página HTML

Tienes dos formas.

#### Automática

Al hacer commit de `sofascore_matches.csv`, el workflow se ejecuta solo:

```text
Generate SofaScore Match Pages
```

#### Manual

Desde GitHub:

```text
Actions -> Generate SofaScore Match Pages -> Run workflow
```

### 3. Completar estadísticas

Abre la ficha del partido, por ejemplo:

```text
https://alejandroai23.github.io/mundial-2026/tools/sofascore-partidos/SWE-TUN-2026.html
```

En SofaScore, entra en:

```text
Alineaciones -> Estadísticas del jugador
```

Copia y pega cada pestaña en su caja:

```text
General
Atacante
Defensa
Pases
Duelos
Portería
```

Pulsa:

```text
Convertir todo
```

### 4. Usar resultado

Puedes descargar o copiar líneas para:

```text
jugadores_stats.csv
disciplina.csv
porteros_stats.csv
partidos_motm.csv
```

Luego las pegas en los CSV correspondientes del repo o usas el workflow manual `Add manual advanced stats`.

## Ventaja

No dependes de la API interna de SofaScore, que devuelve `403 Forbidden` desde GitHub Actions. Solo conviertes los datos que ves en pantalla.
