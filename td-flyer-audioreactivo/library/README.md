# library/ — shaders y recetas reutilizables

Lo que funcionó en flyers pasados, para reusar o adaptar. Revisa esta carpeta ANTES
de escribir un shader nuevo: si hay algo cercano, parte de eso.

## shaders/
GLSL para GLSL TOPs. Convención: entradas vía `sTD2DInputs[i]` (NUNCA `uniform sampler2D`),
salida con `TDOutputSwizzle(...)`, uniforms en camelCase (`uTime`, `uResolution`, `uOffset`...).
El builder los puede embeber como texto en un Text DAT (sin archivo externo) o apuntar a archivo.

- `chroma_split.glsl` — aberración cromática / RGB split. Separa R y B a lo largo de un
  ángulo que bambolea (loop-safe). Uniforms: uResolution, uOffset (px), uTime, uWobble.
  Salió del flyer Tarabeva (2026-06-02). Rango bueno de uOffset: 1–4 base, hasta ~40 con audio.

Nombra describiendo el look, no el proyecto (ej. `halftone_dots.glsl`, no `tarabeva.glsl`).
Cuando muevas uno aquí, anota en LEARNINGS.md de qué flyer salió y qué rangos quedaron buenos.
