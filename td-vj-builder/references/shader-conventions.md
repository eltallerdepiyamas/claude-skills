# Convenciones de shaders — TD VJ Builder

Destilado del corpus real del usuario (Along, Magamundi, Alan Navarro, CCTV, set
generativo 01–16, feedback filters). Lee esto antes de escribir un shader nuevo.

## Reglas TouchDesigner (todas las categorías)

- Salida: `out vec4 fragColor;` y `fragColor = TDOutputSwizzle(vec4(color, 1.0));`
- UV: `vUV.st`. Resolución vía uniform, nunca por `textureSize` salvo para gradientes.
- **NUNCA** declarar `uniform sampler2D` para entradas de TD. Usar `texture(sTD2DInputs[i], uv)`.
  - Visuales: `#define u_input sTD2DInputs[0]`.
  - Efectos: input 0 = cámara, input 1 = feedback.
  - Layouts: cámaras = `sTD2DInputs[0..4]`.
- Pixel format 16-bit float cuando haya feedback o `pow()`/gradientes (8-bit hace banding).
- Tiempo real 1080p/60fps: pocos texture fetches, sin loops largos, sin raymarching pesado.

## Convención de uniforms por categoría

### Visuales (base1–16) — snake_case
```glsl
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;          // energía de audio sumada (low/mid/high segun toggles)
uniform vec3  u_color1, u_color2, u_color3;
// + los u_* propios del visual (u_speed, u_grid_scale, etc.)
#define u_input sTD2DInputs[0]  // solo si mezcla video
```
Generativo puro: ignora `u_input`. Si mezcla, `mix(generado, texture(u_input,uv), k)`.

### Efectos / filtros (base18–24, 38–45) — camelCase
```glsl
uniform float uTime;
uniform vec2  uResolution;
// + los uniforms propios (uDisplaceAmount, uFeedbackDecay, ...)
// feedback opcional: texture(sTD2DInputs[1], uv)
```

### Layouts (escena_modular)
```glsl
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;     // 0=Fill 1=Fit 2=Stretch
// + uniforms propios del layout
```
Incluir la función `applyCamFit(cellUV, camAspect, cellAspect, fitMode)` (ver CLAUDE.md
del proyecto del usuario) en todos los layouts.

## Reactividad de audio — el patrón

El shader recibe la energía de audio **ya sumada** en un uniform (en visuales es
`u_bass`; en efectos suele ser un `uAudioLevel`/banda específica). El builder arma la
expresión en TD; el shader solo la usa como driver. Mantén la respuesta **suave**:
pásala por `smoothstep`/`clamp`/`mix`, nunca 1:1 con el beat. Para cámara en vivo,
"audio como respiración o presión", no como trigger de rave.

## Helpers GLSL comunes (reusa, no reinventes)

`saturate`, `luma = dot(rgb, vec3(0.299,0.587,0.114))`, `rotate2D`, `hash/noise`,
`fbm`, `rgb2hsv/hsv2rgb` (o `TDRGBToHSV`/`TDHSVToRGB`), chroma split, edge-lite/Sobel,
grain analógico, soft vignette, split-tone, highlight extraction, feedback blend seguro.
Para gradiente de luminancia: cruz de 4 muestras.

## Seguridad de cámara (efectos)

La cara/cuerpo deben seguir legibles. Mantén el wet/dry (`Bypass`/cross) y rangos sanos;
no conviertas el feed en abstracción irreconocible. Para retrato, máscara central suave
(menos intensidad al centro, más en bordes). Limita el strobe: breve y opcional.

## Do / Don't (del propio corpus)

- DO: nombres descriptivos de uniforms; comentarios cortos de intención visual en español.
- DO: feedback con `feedbackTOP` + `levelTOP` (decay) + `compositeTOP`/cross para wet-dry.
- DON'T: agregar `TDSimplexNoise` cuando la complejidad ya emerge del feedback.
- DON'T: `uDecay >= 1.0` por defecto (se satura a blanco). Mantener < 1.0.
- DON'T: leer y escribir la misma textura en un pass de feedback (usar el loop de TD).
