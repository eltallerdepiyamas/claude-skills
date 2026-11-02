# Filtro 03 — Liquid Memory

**Categoría:** Feedback con Distorsión
**Firma visual:** La deformación.

## Esencia

El propio feedback se convierte en mapa de displacement: calculamos el
gradiente de luminancia del frame anterior y desplazamos las coordenadas
de muestreo en la dirección **perpendicular** al gradiente — es decir, a lo
largo de las isolíneas de brillo. Esto produce un flujo que sigue los
contornos de la imagen, como si la memoria visual fuera un fluido que
respeta las siluetas que ya existen. Se siente vivo, denso, orgánico.

---

## Código GLSL

```glsl
// =====================================================
// FILTRO 03 — LIQUID MEMORY
// Feedback con distorsión: el gradiente de luminancia
// del frame anterior define el campo vectorial que
// desplaza las coordenadas de muestreo. El flujo sigue
// las isolíneas de brillo.
// =====================================================

// --- UNIFORMS ---
uniform float uDisplace;    // Magnitud de displacement (0.0 - 0.05)
uniform float uDecay;       // Persistencia (0.90 - 0.99)
uniform float uFlow;        // Drift global (0.0 - 0.01)
uniform float uContrast;    // Contraste aplicado al feedback (0.8 - 1.5)
uniform float uMix;         // Mezcla del input nuevo (0.0 - 1.0)
uniform float uTime;        // Tiempo (absTime.seconds)

// --- CONSTANTES ---
const vec3 LUMA = vec3(0.299, 0.587, 0.114);

// --- HELPERS ---
// Gradiente de luminancia por diferencia central (cruz de 4 muestras).
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

    // Campo vectorial: perpendicular al gradiente = tangente a la isolínea.
    vec2 grad = lumaGradient(sTD2DInputs[1], uv, texel);
    vec2 perp = vec2(-grad.y, grad.x);

    // Drift global lento para evitar que el sistema se quede estancado.
    vec2 drift = vec2(sin(uTime * 0.3), cos(uTime * 0.21)) * uFlow;

    // Coordenadas finales de muestreo del feedback.
    vec2 fbUV = uv + perp * uDisplace + drift;

    // Sample feedback distorsionado + contraste no-lineal.
    vec4 fb = texture(sTD2DInputs[1], fbUV);
    fb.rgb  = (fb.rgb - 0.5) * uContrast + 0.5;
    fb.rgb *= uDecay;

    // Inyección de input nuevo.
    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec4 color    = mix(fb, newFrame, uMix);

    fragColor = TDOutputSwizzle(color);
}
```

---

## Estructura de red en TouchDesigner

```
[Source TOP]
     |
     v
   in0
[GLSL TOP: liquid_memory]
     |
     v
[Feedback TOP: fb_liquid]   <- Target = "liquid_memory"
     |
     +-----> in1 de liquid_memory
     |
     v
[Null TOP: out]
```

### Configuración paso a paso

1. **GLSL TOP** `liquid_memory`.
   - Pixel Format: `16-bit float (RGBA)`.
   - Resolution: `1920 x 1080`.
2. **Source TOP** → input 1.
3. **Feedback TOP** `fb_liquid`, Target = `../liquid_memory`. Salida → input 2.
4. **Importante**: en `Common` del GLSL TOP, asegúrate que `Extend U/V = Hold` o
   `Mirror`, para que las muestras desplazadas fuera del frame no se enrosquen
   con `Repeat` (a menos que quieras ese efecto wrap).

### Uniforms en el GLSL TOP (página `Vectors`)

| Vector | Nombre      | Tipo  | Valor por defecto / expresión |
| ------ | ----------- | ----- | ----------------------------- |
| 1      | `uDisplace` | float | `0.012`                       |
| 2      | `uDecay`    | float | `0.94`                        |
| 3      | `uFlow`     | float | `0.0015`                      |
| 4      | `uContrast` | float | `1.05`                        |
| 5      | `uMix`      | float | `0.3`                         |
| 6      | `uTime`     | float | `absTime.seconds`             |

---

## Tabla de uniforms

| Uniform     | Rango sugerido | Qué controla                                                                  |
| ----------- | -------------- | ----------------------------------------------------------------------------- |
| `uDisplace` | 0.0 – 0.05     | Cuánto se desplaza cada píxel siguiendo la isolínea. >0.03 ya es deformación brutal. |
| `uDecay`    | 0.90 – 0.99    | Persistencia. Bajar a 0.9 hace que el fluido "fluya" rápido y no se atasque.  |
| `uFlow`     | 0.0 – 0.01     | Drift global lento. Sin esto el sistema puede quedarse en equilibrio (tú quieres movimiento perpetuo). |
| `uContrast` | 0.8 – 1.5      | Contraste aplicado al feedback antes de devolverlo. >1 enfatiza siluetas, <1 desangra la imagen. |
| `uMix`      | 0.0 – 1.0      | Inyección del input nuevo. Bajo = imagen muy procesada; alto = casi pasthrough. |
| `uTime`     | n/a            | Reloj global. No tocar manualmente.                                            |

### Mapeos sugeridos para VJing

- **Knob principal**: `uDisplace` — es el control que define la "viscosidad" del filtro.
- **Fader**: `uMix`.
- **Knob lento**: `uContrast` — sube/baja el "peso" visual.
- **Trigger / pad**: `uFlow` (puede dispararse a 0.01 momentáneamente para "agitar" el sistema).
- **Reserva**: `uDecay` (cambios bruscos pueden romper el look).

---

## Tips de performance

- **5 texture fetches** (1 directo + 4 para el gradiente) — sigue siendo barato a 1080p en GPU dedicada moderna. En GPUs muy antiguas considera bajar a un sólo eje del gradiente.
- **Pixel Format `16-bit float` es prácticamente obligatorio**: el gradient de luminancia con 8-bit produce escalones visibles en regiones de bajo contraste.
- Si `uDisplace > 0.04` puedes ver pulsaciones inestables porque el feedback se realimenta sobre su propio displacement de forma caótica. Eso *puede* ser deseable; si no, mantén bajo 0.025.
- `Extend U/V = Mirror` da un look más continuo en los bordes que `Repeat`. `Hold` da bordes "estampados" — útil pero notable.
- Si quieres una versión más barata, reemplaza el gradiente por un `texture()` único más una rotación 90°: pierde fidelidad pero baja a 2 fetches.
- No uses `TDSimplexNoise` aquí: el ruido orgánico ya emerge del propio feedback, agregar simplex lo vuelve genérico.
