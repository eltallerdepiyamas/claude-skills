# library/ — shaders reutilizables

Shaders que funcionaron en proyectos pasados, guardados para reusar o adaptar.
El skill revisa esta carpeta ANTES de escribir un shader nuevo: si hay algo cercano
al mood pedido, parte de eso en vez de empezar de cero.

Organiza por categoría:
- visuals/   (generativos, snake_case, u_color1/2/3)
- effects/   (circuito cerrado, camelCase, sTD2DInputs[0..1])
- layouts/   (multi-cámara, sTD2DInputs[0..4])

Nombra describiendo el look, no el proyecto (ej. effects/ghost_trail.frag,
visuals/neon_grid.glsl). Cuando muevas uno aquí, anota en LEARNINGS.md de qué
proyecto salió y qué rangos quedaron buenos.
