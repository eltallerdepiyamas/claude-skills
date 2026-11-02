# Filtro 07 — Memory Marbling

**Categoría:** Distorsión + cromático (domain warping)
**Firma visual:** Espirales tipo mármol / tinta en agua.

## Esencia

Domain warping recursivo: el feedback se sample dos veces, y la **primera
muestra se usa como vector de desplazamiento para la segunda**. Entre las
dos lecturas se aplica una rotación de cizalla (shear) que invierte signo,
así las dos capas giran en sentidos opuestos. El resultado es una textura
marmoreada que se repliega sobre sí misma — como tinta cayendo en agua,
pero acumulándose en el tiempo. Una separación cromática **perpendicular
a la dirección del warp** decora cada espiral con bordes RGB que siguen
el flujo.

---

## Código GLSL

```glsl
// =====================================================
// FILTRO 07 — MEMORY MARBLING
// Domain warping recursivo del feedback. Dos lecturas
// encadenadas con shear opuesto entre capas. Chroma
// perpendicular al warp para bordes RGB que siguen
// la espiral.
// =====================================================

// --- UNIFORMS ---
uniform float uWarp1;        // Magnitud del warp primario          (0.0 - 0.06)
uniform float uWarp2;        // Magnitud del warp secundario        (0.0 - 0.06)
uniform float uShear;        // Angulo de cizalla entre capas (rad) (-1.5 a 1.5)
uniform float uChromaWarp;   // Spread cromatico perpendicular      (0.0 - 0.015)
uniform float uDecay;        // Persistencia                        (0.92 - 0.99)
uniform float uMix;          // Inyeccion de input nuevo            (0.0 - 1.0)
uniform float uContrast;     // Contraste sobre feedback            (0.85 - 1.4)

// --- HELPERS ---
vec2 rotate2D(vec2 v, float a) {
    float s = sin(a);
    float co = cos(a);
    return mat2(co, -s, s, co) * v;
}

// --- OUTPUT ---
out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;

    // ---- Domain warping en 2 pasos ----
    // Paso 1: sondear el feedback en uv. Convertimos
    // los componentes RB (centrados en 0) en un vector
    // de desplazamiento.
    vec3 probe1 = texture(sTD2DInputs[1], uv).rgb;
    vec2 disp1  = (probe1.rb - 0.5);

    // Aplicamos shear positivo y warp primario.
    vec2 uv2 = uv + rotate2D(disp1, uShear) * uWarp1;

    // Paso 2: sondear en la posicion ya desplazada.
    vec3 probe2 = texture(sTD2DInputs[1], uv2).rgb;
    vec2 disp2  = (probe2.rb - 0.5);

    // Posicion final con shear opuesto + warp secundario.
    vec2 finalUV = uv2 + rotate2D(disp2, -uShear) * uWarp2;

    // ---- Chroma perpendicular al warp ----
    // perp al ultimo desplazamiento -> los bordes RGB
    // siguen la direccion de la espiral, no la cruzan.
    vec2 warpDir = rotate2D(disp2, -uShear);
    vec2 perp    = vec2(-warpDir.y, warpDir.x);

    float r = texture(sTD2DInputs[1], finalUV + perp * uChromaWarp).r;
    float g = texture(sTD2DInputs[1], finalUV).g;
    float b = texture(sTD2DInputs[1], finalUV - perp * uChromaWarp).b;

    vec3 fb = vec3(r, g, b);

    // Contraste y decay.
    fb = (fb - 0.5) * uContrast + 0.5;
    fb *= uDecay;

    // Composicion.
    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = mix(fb, newFrame.rgb, uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
```

---

## Estructura de red en TouchDesigner

Esqueleto estándar del set. Builder: `mod('builder').build('marbling')`.

### Uniforms en el GLSL TOP (página `Vectors`)

| Vector | Nombre        | Tipo  | Valor por defecto |
| ------ | ------------- | ----- | ----------------- |
| 1      | `uWarp1`      | float | `0.025`           |
| 2      | `uWarp2`      | float | `0.020`           |
| 3      | `uShear`      | float | `0.4`             |
| 4      | `uChromaWarp` | float | `0.004`           |
| 5      | `uDecay`      | float | `0.97`            |
| 6      | `uMix`        | float | `0.20`            |
| 7      | `uContrast`   | float | `1.05`            |

---

## Tabla de uniforms

| Uniform       | Rango sugerido | Qué controla                                                                  |
| ------------- | -------------- | ----------------------------------------------------------------------------- |
| `uWarp1`      | 0.0 – 0.06     | Magnitud del primer warp. Define la "fuerza" de la primera vuelta de la espiral. |
| `uWarp2`      | 0.0 – 0.06     | Magnitud del warp recursivo. Si `uWarp1` define el patrón base, `uWarp2` lo retuerce sobre sí mismo. |
| `uShear`      | −1.5 a 1.5 rad | Ángulo de cizalla entre las dos capas. **Parámetro estrella**. 0 = no hay swirl; >0.5 rad = espirales marcadas; ±π/2 = perpendicular (textura tipo "rejilla líquida"). El signo invierte el sentido del giro. |
| `uChromaWarp` | 0.0 – 0.015    | Separación cromática perpendicular al warp. Sutil pero hace toda la diferencia: pinta bordes RGB sobre las espirales. |
| `uDecay`      | 0.92 – 0.99    | Persistencia. Subir = mármol más estratificado.                               |
| `uMix`        | 0.0 – 1.0      | Inyección de input. **Importante**: este filtro funciona mejor con `uMix` un poco más alto (0.2–0.4) — el input nuevo es el "tinte" que el mármol va integrando. |
| `uContrast`   | 0.85 – 1.4     | Contraste sobre feedback. >1 marca las estriaciones; <1 las funde.            |

### Mapeos sugeridos para VJing

- **Knob principal**: `uShear` — es lo más expresivo del filtro. Cruzar el cero invierte el sentido del swirl en vivo, efecto espectacular.
- **Knob secundario**: `uWarp1` (o un fader que controle `uWarp1` y `uWarp2` juntos por una expresión).
- **Knob suave**: `uChromaWarp` — sube en momentos de cambio para "encender" los bordes cromáticos.
- **Fader**: `uMix` — sube/baja la inyección de la fuente.
- **Reserva**: `uDecay`, `uContrast`.

---

## Tips de performance

- **5 texture fetches**: 2 para domain warping + 3 para los canales finales. Más barato que Echo / Plasma / Mitosis (que tienen 7).
- **16-bit float obligatorio**: el warp recursivo amplifica banding de 8-bit muy rápido.
- A diferencia de los otros filtros, este **no usa gradiente de luminancia** — el warp viene directamente de los valores RGB del feedback. Por eso es más barato pero también más "abstracto": no respeta siluetas, las disuelve.
- **`uWarp1 * uWarp2 > 0.0036`** (≈ 0.06 × 0.06) y `uDecay > 0.97` puede entrar en runaway feedback (la imagen explota a un patrón de alta frecuencia). Si pasa, baja warp o decay.
- `uShear` cerca de ±π/2 produce texturas casi cuadriculadas (las dos capas son perpendiculares). `uShear` cerca de 0 produce flujos más rectos. El sweet spot expresivo está en ±0.3–0.7 rad.
- Cuando `uMix = 0` el sistema sigue evolucionando porque la recursión es no-trivial. Útil para "modo abstracto puro" sin input.
- Si quieres bajar el costo aún más: elimina los `disp2` del paso 2 y deja sólo el warp primario. Pierdes la estratificación pero ahorras un fetch.
