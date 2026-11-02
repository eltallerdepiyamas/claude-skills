# Filtro 04 — Echo Fractal (Híbrido)

**Categoría:** Híbrido (Espacial + Cromático + Distorsión)
**Firma visual:** Una espiral cromática que respira y se pliega sobre sí misma.

## Esencia

Cada canal RGB del feedback se sample con su propia transformación geométrica
(zoom y rotación ligeramente distintas) **y** se desplaza siguiendo el gradiente
de luminancia del frame anterior. Resultado: una imagen que parece estar
fracturándose en ecos cromáticos — los ecos giran y zoomean a velocidades
sutilmente distintas, pero todos respetan los contornos del input. El input
nuevo aparece como un "destello" que se descompone en su trail.

Lo que la hace **más que la suma**: la transformación geométrica por canal
está modulada por el contenido visual (vía displacement), así que la separación
cromática no es uniforme — *responde* a lo que está pasando en pantalla. Las
zonas de alto contraste generan más fractura cromática que las zonas planas.

---

## Código GLSL

```glsl
// =====================================================
// FILTRO 04 — ECHO FRACTAL (HÍBRIDO)
// Combina:
//   - Feedback espacial (zoom + rotación por canal)
//   - Feedback cromático (decay independiente, hue drift)
//   - Distorsión por gradiente de luminancia
// La transformación por canal es modulada por el contenido,
// no es estática.
// =====================================================

// --- UNIFORMS ---
uniform float uDecay;          // Persistencia base       (0.90 - 0.99)
uniform float uZoom;           // Zoom radial base        (-0.04 a 0.04)
uniform float uRotation;       // Rotación base           (-0.04 a 0.04)
uniform float uChannelSpread;  // Variación entre canales (0.0 - 0.5)
uniform float uDisplace;       // Desplazamiento por contraste (0.0 - 0.03)
uniform float uHueDrift;       // Drift de tono por frame (-0.02 a 0.02)
uniform float uMix;            // Inyección de input nuevo (0.0 - 1.0)

// --- CONSTANTES ---
const vec3 LUMA = vec3(0.299, 0.587, 0.114);

// --- HELPERS ---
// Transformación combinada: rotación + zoom radial respecto al centro.
vec2 transform(vec2 uv, float zoom, float rotation) {
    vec2  c  = uv - 0.5;
    float s  = sin(rotation);
    float co = cos(rotation);
    c = mat2(co, -s, s, co) * c;
    c *= (1.0 - zoom);
    return c + 0.5;
}

// Gradiente de luminancia (cruz de 4 muestras).
vec2 lumaGradient(sampler2D tex, vec2 uv, vec2 texel) {
    float lx1 = dot(texture(tex, uv + vec2(texel.x, 0.0)).rgb, LUMA);
    float lx2 = dot(texture(tex, uv - vec2(texel.x, 0.0)).rgb, LUMA);
    float ly1 = dot(texture(tex, uv + vec2(0.0, texel.y)).rgb, LUMA);
    float ly2 = dot(texture(tex, uv - vec2(0.0, texel.y)).rgb, LUMA);
    return vec2(lx1 - lx2, ly1 - ly2);
}

// --- OUTPUT ---
out vec4 fragColor;

void main() {
    vec2 uv    = vUV.st;
    vec2 texel = 1.0 / vec2(textureSize(sTD2DInputs[1], 0));

    // 1) Distorsión: el contenido del feedback se distorsiona a sí mismo.
    vec2 grad   = lumaGradient(sTD2DInputs[1], uv, texel);
    vec2 perp   = vec2(-grad.y, grad.x);   // tangente isolínea
    vec2 dispUV = perp * uDisplace;

    // 2) Cada canal: transformación espacial con leve variación.
    //    R zoomea/rota un poco más rápido que G; B un poco más lento.
    vec2 uvR = transform(uv + dispUV,
                         uZoom     * (1.0 + uChannelSpread),
                         uRotation * (1.0 + uChannelSpread));
    vec2 uvG = transform(uv + dispUV, uZoom, uRotation);
    vec2 uvB = transform(uv + dispUV,
                         uZoom     * (1.0 - uChannelSpread),
                         uRotation * (1.0 - uChannelSpread));

    // 3) Sample por canal del feedback.
    float r = texture(sTD2DInputs[1], uvR).r;
    float g = texture(sTD2DInputs[1], uvG).g;
    float b = texture(sTD2DInputs[1], uvB).b;
    vec3  fb = vec3(r, g, b) * uDecay;

    // 4) Drift cromático: el feedback rota su tono lentamente.
    vec3 hsv = TDRGBToHSV(fb);
    hsv.x = fract(hsv.x + uHueDrift);
    fb    = TDHSVToRGB(hsv);

    // 5) Composición: el input nuevo entra "encima" del trail.
    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = max(fb, newFrame.rgb * uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
```

---

## Estructura de red en TouchDesigner

```
[Source TOP]
     |
     v
   in0
[GLSL TOP: echo_fractal]
     |
     v
[Feedback TOP: fb_echo]   <- Target = "echo_fractal"
     |
     +-----> in1 de echo_fractal
     |
     v
[Null TOP: out]
```

### Configuración paso a paso

1. **GLSL TOP** `echo_fractal`.
   - Pixel Format: `16-bit float (RGBA)` (necesario para los 7 fetches + acumulación).
2. **Source TOP** → input 1.
3. **Feedback TOP** `fb_echo`, Target = `../echo_fractal`. Salida → input 2.
4. `Common` → `Extend U/V = Mirror` (recomendado, los bordes se mantienen continuos).

### Uniforms en el GLSL TOP (página `Vectors`)

| Vector | Nombre            | Tipo  | Valor por defecto |
| ------ | ----------------- | ----- | ----------------- |
| 1      | `uDecay`          | float | `0.95`            |
| 2      | `uZoom`           | float | `0.008`           |
| 3      | `uRotation`       | float | `0.012`           |
| 4      | `uChannelSpread`  | float | `0.18`            |
| 5      | `uDisplace`       | float | `0.008`           |
| 6      | `uHueDrift`       | float | `0.001`           |
| 7      | `uMix`            | float | `0.25`            |

---

## Tabla de uniforms

| Uniform           | Rango sugerido | Qué controla                                                                  |
| ----------------- | -------------- | ----------------------------------------------------------------------------- |
| `uDecay`          | 0.90 – 0.99    | Persistencia base. Afecta a los tres canales por igual.                       |
| `uZoom`           | −0.04 a 0.04   | Zoom radial base. Positivo = vórtice; negativo = explosión.                   |
| `uRotation`       | −0.04 a 0.04   | Velocidad de rotación base.                                                   |
| `uChannelSpread`  | 0.0 – 0.5      | **Parámetro estrella**. 0 = los tres canales se transforman igual (no hay separación). 0.3+ = ecos cromáticos muy visibles. |
| `uDisplace`       | 0.0 – 0.03     | Cuánto el contenido se distorsiona a sí mismo. Es lo que hace el filtro "responsivo" al input. |
| `uHueDrift`       | −0.02 a 0.02   | Drift lento de paleta durante la persistencia.                                |
| `uMix`            | 0.0 – 1.0      | Inyección de input nuevo.                                                      |

### Mapeos sugeridos para VJing

- **Knob principal (centro de la consola)**: `uChannelSpread` — es la firma del filtro, vale tener acceso instantáneo.
- **XY pad**: X = `uRotation`, Y = `uZoom`. Da control intuitivo del vórtice.
- **Knob suave**: `uDisplace`. Subirlo en momentos de impacto musical multiplica la fractura.
- **Fader**: `uMix`.
- **Knob lentísimo**: `uHueDrift` — usar en sets largos para que la paleta evolucione sola.
- **Botón / pad de "reset"**: enviar `uDecay = 0` por un frame para limpiar el feedback.

---

## Tips de performance

- **7 texture fetches por píxel** (4 para gradiente + 3 RGB independientes) + 1 conversión HSV. A 1080p en GPU moderna corre cómodo a 60fps. En GPUs integradas o portátiles puede acercarse al límite a 1440p.
- **Pixel Format `16-bit float` obligatorio**. El acumulado de hue-drift + decay + displacement en 8-bit produce banding visible.
- `uChannelSpread` **multiplica** el efecto de `uZoom` y `uRotation`. Si uno crece y el otro también, la separación cromática crece exponencialmente y la imagen se desarma. Si esto pasa, baja primero `uChannelSpread` y luego ajusta los otros.
- Si necesitas más FPS: la mayor optimización es bajar el gradiente a 2 fetches en lugar de 4 (sólo eje X o sólo Y) y notar la diferencia de calidad.
- `Extend U/V = Mirror` mantiene los bordes "vivos" cuando el zoom es agresivo. Con `Hold` aparecen líneas de stamping en los bordes; con `Repeat` aparecen wraps caóticos (puede ser deseable).
- **Anti-saturación**: con `uDecay = 0.99` y `uMix = 0` el feedback satura a blanco rápidamente. Usa siempre `uMix > 0.05` o `uDecay < 0.97` durante shows largos.
