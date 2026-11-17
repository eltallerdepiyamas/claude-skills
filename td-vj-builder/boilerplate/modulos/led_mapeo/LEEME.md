# led_mapeo

Toma el visual (`/project1/color_final`) y lo reparte en los tableros de una pantalla LED, apilados como los pide el procesador (fila de arriba primero). Crea `/project1/led`.

- **master_banner**: (Columnas × Tablero) × (Filas × Tablero). Lo que va al procesador.
- **preview_banner**: todos los tableros en una línea, como cuelgan, con guías.

Página **Banner**: Columnas · Filas · Tablero (px por lado) · Modo (cuadros / franja / bloque del centro) · Zoom.
La primera vez toma la cuadrícula de `proyecto.json` → `"led"`. Default 4 × 3 de 256 px (banner de Casa Bacardi / Pal Norte).
