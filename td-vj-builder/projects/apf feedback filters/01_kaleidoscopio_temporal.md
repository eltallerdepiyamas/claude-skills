# Filtro 01 — Kaleidoscopio Temporal Cinético

**Categoría:** Feedback Espacial
**Firma visual:** El movimiento.

## Esencia

Cada frame del feedback es plegado radialmente (kaleidoscopio) y, a la vez,
zoomeado y rotado un poco antes de mezclarse con el frame anterior. Como el
plegado se acumula, los patrones nacen, giran hacia el centro (o hacia afuera)
y se multiplican en simetría temporal. El input nuevo se inyecta en pequeñas
dosis para que la imagen "respire" sin perder la estructura cinética.

---

## Código GLSL

```glsl
// =====================================================
// FILTRO 01 — KALEIDOSCOPIO TEMPORAL CINÉTICO
// Feedback espacial: pliegue radial + zoom + rotación
// acumulativos sobre el frame anterior.
// =====================================================

// --- UNIFORMS ---
uniform float uDecay;       // Persistencia del feedback (0.85 - 0.99)
uniform float uZoom;        // Zoom radial por frame (-0.05 a 0.05)
uniform float uRotation;    // Rotación por frame en radianes (-0.05 a 0.05)
uniform float uSegments;    // Número de espejos del kaleidoscopio (1 - 32)
uniform float uMix;         // Cantidad de input nuevo por frame (0.0 - 1.0)
uniform vec2  uCenter;      // Centro de la transformación (0.5, 0.5 = centro)

// --- CONSTANTES ---
const float TAU = 6.28318530718;

// --- HELPERS ---
// Pliegue radial tipo kaleidoscopio sobre coordenadas centradas.
vec2 kaleidoFold(vec2 c, float segments) {
    float angle  = atan(c.y, c.x);
    float radius = length(c);
    float seg    = TAU / max(segments, 1.0);
    angle = mod(angle, seg);
    angle = abs(angle - seg * 0.5);   // espejo dentro del segmento
    return vec2(cos(angle), sin(angle)) * radius;
}

// Rota un punto 2D en torno al origen.
vec2 rotate2D(vec2 c, float a) {
    float s = sin(a);
    float co = cos(a);
    return mat2(co, -s, s, co) * c;
}

// --- OUTPUT ---
out vec4 fragColor;

void main() {
    // Coordenadas centradas en uCenter.
    vec2 centered = vUV.st - uCenter;

    // Aplicamos pliegue, rotación y zoom al sample del feedback.
    vec2 fold     = kaleidoFold(centered, uSegments);
    vec2 rotated  = rotate2D(fold, uRotation);
    vec2 zoomed   = rotated * (1.0 - uZoom);
    vec2 fbUV     = zoomed + uCenter;

    // Sample feedback (input 1) y nuevo frame (input 0).
    vec4 feedback = texture(sTD2DInputs[1], fbUV);
    vec4 newFrame = texture(sTD2DInputs[0], vUV.st);

    // Decay sobre el feedback + inyección dosificada del input nuevo.
    vec4 color = mix(feedback * uDecay, newFrame, uMix);

    fragColor = TDOutputSwizzle(color);
}
```

---

## Estructura de red en TouchDesigner

```
[Source TOP]                              <- video / cámara / generador
     |
     v
   in0
[GLSL TOP: kaleido_temporal]
     |
     v
[Feedback TOP: fb_kaleido]   <- Target = "kaleido_temporal"
     |
     +-----> in1 de kaleido_temporal      (loop de feedback)
     |
     v
[Null TOP: out]                           <- salida final
```

### Configuración paso a paso

1. **GLSL TOP** llamado `kaleido_temporal`.
   - Pixel Format: `16-bit float (RGBA)` (recomendado para feedback limpio).
   - Resolution: `1920 x 1080` (o lo que use tu pipeline).
2. **Source TOP** (video/cámara/Noise) → conectar al **input 1** del GLSL TOP.
3. **Feedback TOP** llamado `fb_kaleido`.
   - Target: `../kaleido_temporal` (o el path correspondiente).
   - Connect: salida del Feedback TOP → **input 2** del GLSL TOP.
4. En el GLSL TOP, página `Vectors`, declarar los uniforms (ver abajo).
5. Página `Common` del GLSL TOP: `Input Smoothness = Nearest` para evitar suavizado extra
   en el muestreo del feedback (opcional, dependiendo del look).

### Uniforms en el GLSL TOP (página `Vectors`)

| Vector | Nombre       | Tipo  | Valor por defecto / expresión |
| ------ | ------------ | ----- | ----------------------------- |
| 1      | `uDecay`     | float | `0.96`                        |
| 2      | `uZoom`      | float | `0.005`                       |
| 3      | `uRotation`  | float | `0.01`                        |
| 4      | `uSegments`  | float | `8`                           |
| 5      | `uMix`       | float | `0.15`                        |
| 6      | `uCenter`    | vec2  | `0.5, 0.5`                    |

---

## Tabla de uniforms

| Uniform     | Rango sugerido    | Qué controla                                                                  |
| ----------- | ----------------- | ----------------------------------------------------------------------------- |
| `uDecay`    | 0.85 – 0.99       | Cuánto persiste cada frame. >0.97 = trails muy largos; <0.9 = movimiento corto. |
| `uZoom`     | −0.05 a 0.05      | Zoom radial por frame. Positivo = vórtice hacia el centro; negativo = explosión. |
| `uRotation` | −0.05 a 0.05      | Velocidad de rotación acumulativa en radianes/frame.                           |
| `uSegments` | 1 – 32            | Cantidad de espejos. 1 = sin kaleido. Valores fraccionarios producen ruptura asimétrica. |
| `uMix`      | 0.0 – 1.0         | Cuánto se "vacía" la imagen al input nuevo. 0 = pure feedback (peligro de saturación), 0.5 = balance. |
| `uCenter`   | (0,0) – (1,1)     | Centro del pliegue/zoom. Mover lejos de (0.5,0.5) descentra todo el sistema.   |

### Mapeos sugeridos para VJing

- **Knob slow / horizontal**: `uRotation`.
- **Knob slow / vertical**: `uZoom`.
- **Fader principal**: `uMix` (cuánta señal nueva entra).
- **Encoder libre**: `uSegments` (cambios escalonados son más vistosos).
- **XY pad**: `uCenter` (mueve el vórtice por la pantalla).
- **Decay knob (idealmente continuo)**: `uDecay`.

---

## Tips de performance

- A 1080p el shader es trivial: 2 texture fetches + trig. Corre con holgura a 60fps en cualquier GPU dedicada moderna.
- **Pixel Format del Feedback TOP debe matchear el del GLSL TOP** — si no, TD inserta una conversión y tira FPS.
- Mantén `uDecay < 1.0`. Con `uDecay = 1.0` y `uMix = 0` la imagen no decae nunca y se satura a blanco.
- Si quieres textura más limpia en zoom-in agresivo, sube el `Input Smoothness` a `Mipmap Linear` en la página `Common`.
- Resoluciones >1080p escalan linealmente; el cuello de botella sería bandwidth de feedback, no compute.
- Evita `uSegments > 32` — el cálculo es barato pero los aliasing artefactos se vuelven feos.
- No hace falta `uTime`: la animación viene del feedback, no del reloj.
