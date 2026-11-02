# Fase 2 — Propuesta del contrato de 5 (efectos)

Orden fijo de los 5 sliders, igual en todas las bases (así el knob N significa lo mismo siempre):

| Slot | Rol | Knob MIDImix |
|---|---|---|
| 1 | **Intensidad / mezcla** | knob 1 |
| 2 | **Velocidad / tiempo** | knob 2 |
| 3 | **Distorsión / deformación** | knob 3 |
| 4 | **Color** | knob 4 |
| 5 | **Firma** (lo más característico del efecto) | knob 5 |

Además, separado de los 5: **Bypass** (toggle) y pestaña **Audio** (`Audioreact`, `Low`, `Mid`, `High`, `Audiotarget`, `Audiomult`).

## Dos piezas universales que el script agrega a cada base

Muchas bases no tienen control de mezcla o de color. Para que **todas** tengan sus 5:

- **Mezcla** — un Cross TOP entre la entrada limpia y el efecto. Si la base ya tiene `Drywet`/`Blend`, se usa ese.
- **Color** — un HSV Adjust al final del efecto (giro de tono). Si la base ya tiene control de color propio, se usa ese.

Con eso, los slots 1 y 4 siempre existen; los slots 2, 3 y 5 salen de los parámetros reales de cada efecto.

## Propuesta por base

`✱` = pieza universal agregada por el script · `❓` = no encontré un buen parámetro, decides tú

| Base | FX | 1 Intensidad | 2 Velocidad | 3 Distorsión | 4 Color | 5 Firma |
|---|---|---|---|---|---|---|
| base18 | Time Machine 4 Glitch | Mezcla ✱ | `Cachesize` (profundidad de tiempo) | `Threshold` | Tono ✱ | `Threshold2` (feedback opacity) |
| base19 | Slitscan | `Drywet` (pixelate) | `Int` (cache size) | `Blackoffset` | Tono ✱ | `Menu` (ramp) ❓ |
| base20 | Feedback RGB Delay | `Opacity` (data mosh) | `Bluedelay`/`Reddelay` ❓ | `Size` (filter size) | `Rgba` (edge color) → tono | `Whitewidth` ❓ |
| base21 | Optical Flow | Mezcla ✱ | ❓ (hoy lo mueve el audio) | `Displaceweight1` | Tono ✱ | `Float` (feedback opacity) |
| base22 | Liquid Feedback | Mezcla ✱ | ❓ | `Feedbackscale` | Tono ✱ | `Feedbackscale2` (feedback opacity) |
| base23 | Pixel Sort | Mezcla ✱ | ❓ | ❓ | Tono ✱ | `Feedbackopacity` |
| base24 | ASCII | `Mastercontrast` | ❓ | `Mastercellsize` | `Mastercolor` → tono | `Asciiactivefilter2` (caracteres / halftone / dither) |
| base38 | — | `Blend` | `Warprot` | `Warpscale` | Tono ✱ | `Feedbackamt` |
| base39 | — (shader roto) | `Blend` | `Speed` | `Strength` | Tono ✱ | `Radius` |
| base40 | — | `Blend` | `Decay` | `Trailblend` | `Colorshift` | `Blendmode` ❓ |
| base41 | Bloom | `Bloom` (bloom level) | `Feedbackamt` ❓ | `Dispx` | `Glowcolor` → tono | `Glow` |
| base42 | Light Tunnel | `Blend` | `Pulsespeed` | `Radius` | `Invertamt` | `Feedbackamt` |
| base43 | RGBA Delay | `Drywet` | ❓ | ❓ | Tono ✱ | ❓ |
| base44 | Radial Blur | `Drywet` | ❓ | `Strength` | `Redpreshrink` (separación RGB) | `Samples` |
| base45 | Kaleidoscope | Mezcla ✱ | `Rotatez` (animado) | `Kaleidonum` | Tono ✱ | `Fullmode` ❓ |

## Cosas que encontré de paso

- **Visuales base1–16 no tienen ningún parámetro** ni uniforms de GLSL: hay que ver qué hay adentro de cada uno antes de proponer.
- **base39** tiene el shader vacío: hay que reescribirlo (o borrarla) antes de ponerle contrato.
- **base45 y base27** leen el MIDI directo de `/project1` (`null3['ch1ctrl56']`, `null50['ch1n26']`): con el contrato eso pasa a los slots y se quita la dependencia.
- **base20** tiene un `switch1` interno con 4 entradas que no sale a ningún lado: ¿eran variantes del efecto?
- **base21** ya es audioreactivo por dentro (`optical_flow/null1['low']`): con la pestaña Audio estándar eso se unifica.
- **base24** ya tiene una pestaña `Master` que hace casi lo mismo que el contrato: es el mejor modelo a seguir.
