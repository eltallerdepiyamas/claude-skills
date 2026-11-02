# Filtro 02 — RGB Trail Decay

**Categoría:** Feedback Cromático
**Firma visual:** El color.

## Esencia

Cada canal RGB lee el feedback con su propio offset espacial y su propia
curva de decay no-lineal (potencia exponencial), por lo que los rojos, verdes
y azules dejan estelas de duración y dirección distintas. Movimiento en la
imagen → tres fantasmas de color desfasados que se separan y reabsorben.
Una pizca de hue-drift por frame hace que la paleta evolucione lentamente
durante la persistencia.

---

## Código GLSL

```glsl
// =====================================================
// FILTRO 02 — RGB TRAIL DECAY
// Feedback cromático: decay no-lineal y desfase
// espacial independientes por canal RGB.
// =====================================================

// --- UNIFORMS ---
uniform float uDecayR;     // Persistencia rojo  (0.90 - 0.999)
uniform float uDecayG;     // Persistencia verde
uniform float uDecayB;     // Persistencia azul
uniform vec2  uOffsetR;    // Offset del trail rojo  (-0.02 a 0.02)
uniform vec2  uOffsetG;    // Offset del trail verde
uniform vec2  uOffsetB;    // Offset del trail azul
uniform float uMix;        // Inyección de input nuevo (0.0 - 1.0)
uniform float uHueDrift;   // Desplazamiento de tono por frame (-0.02 a 0.02)
uniform float uGain;       // Realce de saturación del trail (0.5 - 2.0)

// --- HELPERS ---
// Decay no-lineal: pow(x, 1/d) con d en (0,1].
// d cercano a 1 -> casi identidad; d bajo -> los grises caen rápido,
// las luces altas persisten más, generando "lumas vivas, sombras muertas".
float nonLinearDecay(float x, float d) {
    return pow(clamp(x, 0.0, 1.0), 1.0 / max(d, 0.001));
}

// --- OUTPUT ---
out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;

    // Sample feedback por canal con offset propio.
    float fbR = texture(sTD2DInputs[1], uv - uOffsetR).r;
    float fbG = texture(sTD2DInputs[1], uv - uOffsetG).g;
    float fbB = texture(sTD2DInputs[1], uv - uOffsetB).b;

    // Decay no-lineal independiente.
    fbR = nonLinearDecay(fbR, uDecayR);
    fbG = nonLinearDecay(fbG, uDecayG);
    fbB = nonLinearDecay(fbB, uDecayB);

    vec3 fb = vec3(fbR, fbG, fbB);

    // Drift de tono lento sobre el feedback.
    vec3 hsv = TDRGBToHSV(fb);
    hsv.x = fract(hsv.x + uHueDrift);
    hsv.y = clamp(hsv.y * uGain, 0.0, 1.0);
    fb = TDHSVToRGB(hsv);

    // Componer: el input nuevo "pinta encima" usando max,
    // así los trails brillantes nunca son tapados por píxeles oscuros.
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
[GLSL TOP: rgb_trail]
     |
     v
[Feedback TOP: fb_trail]   <- Target = "rgb_trail"
     |
     +-----> in1 de rgb_trail
     |
     v
[Null TOP: out]
```

### Configuración paso a paso

1. **GLSL TOP** llamado `rgb_trail`.
   - Pixel Format: `16-bit float (RGBA)` (los pow() acumulan error con 8-bit).
2. **Source TOP** → input 1 del GLSL TOP.
3. **Feedback TOP** `fb_trail`, Target = `../rgb_trail`. Salida del Feedback TOP
   → input 2 del GLSL TOP.
4. Crea un `Constant CHOP` o `Slider COMP` y enrutea por DAT/Bind para mapear
   a los uniforms (especialmente los `uOffset*` que son vec2).

### Uniforms en el GLSL TOP (página `Vectors`)

| Vector | Nombre      | Tipo  | Valor por defecto |
| ------ | ----------- | ----- | ----------------- |
| 1      | `uDecayR`   | float | `0.97`            |
| 2      | `uDecayG`   | float | `0.95`            |
| 3      | `uDecayB`   | float | `0.93`            |
| 4      | `uOffsetR`  | vec2  | `0.002, 0.0`      |
| 5      | `uOffsetG`  | vec2  | `0.0, 0.0`        |
| 6      | `uOffsetB`  | vec2  | `-0.002, 0.0`     |
| 7      | `uMix`      | float | `0.4`             |
| 8      | `uHueDrift` | float | `0.0`             |
| 9      | `uGain`     | float | `1.1`             |

---

## Tabla de uniforms

| Uniform     | Rango sugerido     | Qué controla                                                              |
| ----------- | ------------------ | ------------------------------------------------------------------------- |
| `uDecayR/G/B` | 0.90 – 0.999     | Curva de decay por canal. Valores muy cercanos a 1 → trails muy largos. Diferenciar canales = separación cromática temporal. |
| `uOffsetR/G/B` | −0.02 a 0.02   | Desfase espacial del trail por canal. Si los tres son distintos, el movimiento "abre" en RGB. |
| `uMix`      | 0.0 – 1.0          | Cuánto del frame nuevo entra. Bajo `uMix` = trails dominan; alto = imagen casi limpia. |
| `uHueDrift` | −0.02 a 0.02       | El feedback rota su tono cada frame. Sutil. Crea evoluciones lentas de paleta durante el decay. |
| `uGain`     | 0.5 – 2.0          | Saturación aplicada al feedback. >1 hace los trails más vivos; <1 los desatura hasta plata. |

### Mapeos sugeridos para VJing

- **3 faders en columna**: `uDecayR`, `uDecayG`, `uDecayB`. Tocarlos por separado da control inmediato de balance temporal de color.
- **XY pad**: `uOffsetR` (xy). Deja `uOffsetB = -uOffsetR` como expresión para split simétrico.
- **Knob lento**: `uHueDrift` (su efecto es acumulativo, basta un toque pequeño).
- **Fader principal**: `uMix`.

---

## Tips de performance

- 4 texture fetches + 1 conversión HSV/RGB. Trivial a 1080p.
- **Pixel Format `16-bit float`** es importante: `pow()` con curvas extremas acumula banding en 8-bit muy rápido.
- `uDecayR/G/B = 1.0` congela la imagen. Mantén siempre <1.0 a menos que quieras congelar deliberadamente.
- Cuidado con `uOffset` muy grandes (>0.05): el feedback "patina" tanto que la imagen se resbala fuera del frame. Usa wrap mode `Repeat` en el Feedback TOP si quieres que reentre por el otro lado.
- Si `uHueDrift > 0.05` por frame el cambio se vuelve epiléptico. Mantenerlo <0.01 para que se sienta como un drift orgánico.
- `max()` para componer es barato y mantiene los trails brillantes; si lo cambias por `mix()` el carácter del filtro se pierde.
