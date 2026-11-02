# Filtro 06 — Spectral Mitosis

**Categoría:** Híbrido (espacial + cromático, content-driven)
**Firma visual:** División cromática en los bordes.

## Esencia

Cada canal RGB del feedback se sample del frame anterior en una posición
desplazada **a lo largo del gradiente de luminancia**, con un ángulo
ligeramente diferente para R / G / B. La clave: la magnitud del split es
proporcional a la **fuerza del gradiente**, así que el efecto **sólo ocurre
en zonas de contraste**. Las regiones planas quedan estables, los bordes
"se dividen" en hijos cromáticos que se desplazan en abanico. Visualmente:
células mitóticas dividiéndose a lo largo de las siluetas, dejando estela
en RGB. Una respiración global (zoom oscilante) hace que el sistema
"inhale y exhale" durante el set.

---

## Código GLSL

```glsl
// =====================================================
// FILTRO 06 — SPECTRAL MITOSIS
// Split cromatico content-driven: cada canal sample el
// feedback con offset a lo largo del gradiente,
// modulado por la magnitud del propio gradiente.
// La division solo ocurre donde hay contraste.
// =====================================================

// --- UNIFORMS ---
uniform float uSplit;        // Magnitud base del split          (0.0 - 0.05)
uniform float uAngleSpread;  // Spread angular RGB (radianes)    (0.0 - 1.2)
uniform float uDecay;        // Persistencia                     (0.92 - 0.99)
uniform float uBreathe;      // Amplitud de respiracion (zoom)   (0.0 - 1.0)
uniform float uMix;          // Inyeccion de input nuevo         (0.0 - 1.0)
uniform float uHueDrift;     // Drift de tono por frame          (-0.01 a 0.01)
uniform float uTime;         // Reloj

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

vec2 rotate2D(vec2 v, float a) {
    float s = sin(a);
    float co = cos(a);
    return mat2(co, -s, s, co) * v;
}

// --- OUTPUT ---
out vec4 fragColor;

void main() {
    vec2 uv    = vUV.st;
    vec2 texel = 1.0 / vec2(textureSize(sTD2DInputs[1], 0));

    // Gradiente y su magnitud (cuanto contraste hay aqui).
    vec2  grad = lumaGradient(sTD2DInputs[1], uv, texel);
    float gmag = length(grad);

    // Direccion unitaria; si el gradiente es casi cero usamos eje X
    // (en zonas planas el split sera 0 igual por la modulacion).
    vec2 dir = (gmag > 1e-4) ? grad / gmag : vec2(1.0, 0.0);

    // Offset por canal: rotaciones simetricas con respecto a "dir".
    // gmag modula la cantidad, asi que regiones planas no se dividen.
    float scale = uSplit * gmag;
    vec2 dR = rotate2D(dir,  uAngleSpread) * scale;
    vec2 dG = dir * scale;
    vec2 dB = rotate2D(dir, -uAngleSpread) * scale;

    // Respiracion: zoom oscilante sobre todo el frame.
    float breath = 1.0 + sin(uTime * 0.6) * uBreathe * 0.012;
    vec2 centered = uv - 0.5;
    vec2 uvBreath = centered * breath + 0.5;

    // Sample feedback por canal.
    float r = texture(sTD2DInputs[1], uvBreath + dR).r;
    float g = texture(sTD2DInputs[1], uvBreath + dG).g;
    float b = texture(sTD2DInputs[1], uvBreath + dB).b;

    vec3 fb = vec3(r, g, b) * uDecay;

    // Hue drift lento para que la paleta evolucione.
    vec3 hsv = TDRGBToHSV(fb);
    hsv.x = fract(hsv.x + uHueDrift);
    fb = TDHSVToRGB(hsv);

    // Composicion: input se "estampa" sobre las celulas.
    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = max(fb, newFrame.rgb * uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
```

---

## Estructura de red en TouchDesigner

Esqueleto estándar del set. Builder: `mod('builder').build('mitosis')`.

### Uniforms en el GLSL TOP (página `Vectors`)

| Vector | Nombre         | Tipo  | Valor por defecto |
| ------ | -------------- | ----- | ----------------- |
| 1      | `uSplit`       | float | `0.025`           |
| 2      | `uAngleSpread` | float | `0.6`             |
| 3      | `uDecay`       | float | `0.96`            |
| 4      | `uBreathe`     | float | `0.3`             |
| 5      | `uMix`         | float | `0.22`            |
| 6      | `uHueDrift`    | float | `0.0008`          |
| 7      | `uTime`        | float | `absTime.seconds` |

---

## Tabla de uniforms

| Uniform        | Rango sugerido | Qué controla                                                                  |
| -------------- | -------------- | ----------------------------------------------------------------------------- |
| `uSplit`       | 0.0 – 0.05     | Magnitud base del desplazamiento. Multiplicado por la magnitud del gradiente. >0.04 produce división muy agresiva. |
| `uAngleSpread` | 0.0 – 1.2 rad  | Cuán abiertos se separan los canales angularmente. 0 = sin separación; π/3 (~1.0) = ya muy abierto. |
| `uDecay`       | 0.92 – 0.99    | Persistencia. Subir = más reproducción mitótica antes de que se desvanezca cada hija. |
| `uBreathe`     | 0.0 – 1.0      | Amplitud del zoom oscilante. 0 = sin respiración; 0.5 = respiración perceptible; 1.0 = bombeo fuerte. |
| `uMix`         | 0.0 – 1.0      | Input nuevo. Mantener bajo (0.15–0.3) para preservar el carácter mitótico.    |
| `uHueDrift`    | −0.01 a 0.01   | Drift muy lento de la paleta. Esencial para sesiones largas.                  |
| `uTime`        | n/a            | Reloj. No tocar.                                                              |

### Mapeos sugeridos para VJing

- **Knob principal**: `uAngleSpread` — controla cuán "abierta" es la división cromática. Es la firma del filtro.
- **Knob secundario**: `uSplit` — controla la distancia de los hijos. Combinado con `uAngleSpread` define la geometría de la mitosis.
- **Knob suave / LFO**: `uBreathe` — bombeo. Subirlo en momentos de impulso da efecto orgánico.
- **Fader**: `uMix`.

---

## Tips de performance

- 4 fetches gradiente + 3 fetches canal = **7 fetches**. Mismo orden que Echo y Plasma. Holgado a 1080p en GPU moderna.
- **16-bit float obligatorio.**
- **Lo distintivo** comparado con Echo Fractal: la transformación NO es uniforme — `gmag` la modula por píxel. Por eso este filtro se "ve" más reactivo al contenido: si la imagen entrante tiene mucho contraste, explota; si es plana, queda estable.
- Cuando `uSplit * gmag` excede 0.05 localmente, aparecen "duplicaciones espectrales" muy visibles. Si las quieres como punctum, sube `uSplit`; si las quieres suaves, bájalo.
- Con `uMix = 0` el sistema sigue evolucionando por la respiración + la mitosis local. Útil para "freezes vivos" — congelar la entrada pero dejar el feedback respirando.
- Si quieres una versión más glitchy: sube `uAngleSpread > 1.0` y reduce `uSplit` para que los canales se separen mucho angularmente pero poco en distancia.
