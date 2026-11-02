# Filtro 05 — Plasma Currents

**Categoría:** Distorsión avanzada (extiende Liquid Memory)
**Firma visual:** Corrientes y filamentos.

## Esencia

El feedback se trata como un campo de plasma 2D. El gradiente de luminancia
genera **dos fuerzas simultáneas**: una corriente que fluye tangente a las
isolíneas (como Liquid) y una presión que empuja a lo largo del gradiente
(las zonas brillantes se atraen o se repelen entre sí). Las dos fuerzas
combinadas producen remolinos y filamentos tipo plasma solar / humo
eléctrico. Cada canal RGB fluye a velocidad ligeramente distinta, generando
estelas cromáticas en la dirección del flujo.

---

## Código GLSL

```glsl
// =====================================================
// FILTRO 05 — PLASMA CURRENTS
// El gradiente de luminancia produce corriente (tangente)
// + presion (radial). El campo combinado genera remolinos
// y filamentos. Cromatica diferenciada por canal.
// =====================================================

// --- UNIFORMS ---
uniform float uCurrent;      // Flujo tangente (perp. al gradiente)   (0.0 - 0.03)
uniform float uPressure;     // Flujo radial (alineado al gradiente)  (-0.01 a 0.01)
uniform float uDecay;        // Persistencia                          (0.92 - 0.99)
uniform float uChromaFlow;   // Variacion de velocidad por canal      (0.0 - 0.6)
uniform float uContrast;     // Contraste sobre feedback              (0.9 - 1.3)
uniform float uMix;          // Inyeccion de input nuevo              (0.0 - 1.0)
uniform float uTime;         // Reloj (absTime.seconds)

// --- CONSTANTES ---
const vec3 LUMA = vec3(0.299, 0.587, 0.114);

// --- HELPERS ---
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

    // Campo escalar -> dos campos vectoriales.
    vec2 grad = lumaGradient(sTD2DInputs[1], uv, texel);
    vec2 perp = vec2(-grad.y, grad.x);             // tangente isolinea (corriente)
    // grad mismo = presion (positivo = brillante atrae; negativo = repele)

    // Drift global lento para que el sistema no se quede en equilibrio.
    float t = uTime * 0.17;
    vec2 baseDrift = vec2(sin(t), cos(t * 1.31)) * 0.0007;

    // Flujo combinado, por canal con escala diferenciada.
    vec2 flowBase = perp * uCurrent + grad * uPressure + baseDrift;
    vec2 flowR = flowBase * (1.0 + uChromaFlow);
    vec2 flowG = flowBase;
    vec2 flowB = flowBase * (1.0 - uChromaFlow);

    float r = texture(sTD2DInputs[1], uv + flowR).r;
    float g = texture(sTD2DInputs[1], uv + flowG).g;
    float b = texture(sTD2DInputs[1], uv + flowB).b;

    vec3 fb = vec3(r, g, b);

    // Contraste no-lineal (refuerza filamentos).
    fb = (fb - 0.5) * uContrast + 0.5;
    fb *= uDecay;

    // El input nuevo se "estampa" sobre las corrientes.
    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = max(fb, newFrame.rgb * uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
```

---

## Estructura de red en TouchDesigner

Idéntica al esqueleto del set: `Source → in0 [GLSL TOP] in1 ← [Feedback TOP]`.
Construir manualmente o llamar `mod('builder').build('plasma')`.

### Uniforms en el GLSL TOP (página `Vectors`)

| Vector | Nombre        | Tipo  | Valor por defecto |
| ------ | ------------- | ----- | ----------------- |
| 1      | `uCurrent`    | float | `0.014`           |
| 2      | `uPressure`   | float | `0.002`           |
| 3      | `uDecay`      | float | `0.96`            |
| 4      | `uChromaFlow` | float | `0.25`            |
| 5      | `uContrast`   | float | `1.08`            |
| 6      | `uMix`        | float | `0.18`            |
| 7      | `uTime`       | float | `absTime.seconds` |

---

## Tabla de uniforms

| Uniform       | Rango sugerido | Qué controla                                                                  |
| ------------- | -------------- | ----------------------------------------------------------------------------- |
| `uCurrent`    | 0.0 – 0.03     | Magnitud del flujo tangente. Es el "viento" del plasma. Mayor = filamentos más largos. |
| `uPressure`   | −0.01 a 0.01   | Empuje radial. Positivo → las zonas brillantes se ATRAEN (plasma se condensa en blobs). Negativo → las brillantes se REPELEN (plasma se dispersa). |
| `uDecay`      | 0.92 – 0.99    | Persistencia. Subir = filamentos largos y densos. Bajar = plasma volátil.     |
| `uChromaFlow` | 0.0 – 0.6      | Diferencia de velocidad entre canales. >0.3 ya muestra trails RGB pronunciados sobre los filamentos. |
| `uContrast`   | 0.9 – 1.3      | Realce de contraste sobre el feedback. >1 marca los filamentos; <1 los disuelve. |
| `uMix`        | 0.0 – 1.0      | Inyección del input nuevo. Manténlo bajo (0.1-0.3) para que dominen las corrientes. |
| `uTime`       | n/a            | Reloj. No tocar manualmente.                                                  |

### Mapeos sugeridos para VJing

- **Knob principal**: `uPressure` — pasar de negativo a positivo cambia drásticamente el carácter (dispersión ↔ condensación).
- **Knob secundario**: `uCurrent` — controla la "fuerza del viento".
- **Knob lento**: `uChromaFlow` — sube en momentos climáticos para spread cromático.
- **Fader**: `uMix`.
- **Reserva**: `uContrast`, `uDecay`.

---

## Tips de performance

- 4 fetches para gradiente + 3 por canal = **7 texture fetches**. Mismo costo que Echo Fractal. Holgado a 1080p en GPU dedicada moderna.
- **16-bit float obligatorio** (gradient + contraste acumulado).
- **Cuidado con `uPressure` y `uDecay` altos juntos**: la presión positiva alta + decay alto puede colapsar todo el feedback en un blob brillante. Si pasa, baja `uPressure` o sube `uMix`.
- Con `uPressure < 0` y feedback muy oscuro, el plasma se "despega" del fondo y se mueve libremente — efecto muy bonito pero puede saturar a negro si no entra señal nueva (sube `uMix`).
- `uChromaFlow > 0.7` genera disociación tan fuerte que el ojo ya no integra los canales — si quieres ese look glitchy, perfecto; si no, mantén abajo de 0.5.
- No agregues `TDSimplexNoise` ni nada parecido: la complejidad del flujo emerge del feedback mismo, agregar ruido externo lo vuelve genérico.
