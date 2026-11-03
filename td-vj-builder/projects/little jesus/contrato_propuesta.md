# Fase 2 — Contrato de 5 (efectos de cámara) · v2 aplicada

> FX renumerados el 2026-11-02: base38–45 → base25–32.

Orden fijo de los 5 sliders, igual en todas las bases (el knob N significa lo mismo siempre).
Fila 2 del MIDImix (CC 18, 22, 26, 30, 48) y fila 2 de la página MIX del Stream Deck.

| Slot | Rol | Knob fila 2 | Qué esperar al girarlo |
|---|---|---|---|
| 1 | **Mezcla** | col 1 (CC18) | 0 = cámara limpia · 100% = efecto completo |
| 2 | **Tiempo** | col 2 (CC22) | velocidad, o cuánto dura la estela / memoria |
| 3 | **Distorsión** | col 3 (CC26) | cuánto deforma la imagen |
| 4 | **Color** | col 4 (CC30) | giro de tono o color del efecto |
| 5 | **Firma** | col 5 (CC48) | lo más característico del efecto |

Separado de los 5: **Bypass** (toggle) y pestaña **Audio** (`Audioreact`, `Low`, `Mid`, `High`,
`Audiotarget`, `Audiomult`, `Smooth`): el audio suma sobre el slot que elijas en `Audiotarget`.

## Piezas universales (✱) que el script agrega cuando la base no lo tiene

- **Mezcla ✱** — Cross TOP entre la entrada limpia y el efecto.
- **Tono ✱** — HSV Adjust al final (giro de tono 0–360°).
- **Estela ✱** — Feedback al final del efecto: 0 = sin estela, 100% = estela larga. Es el "Tiempo" de los FX que no tienen velocidad propia.
- **Pasos** — un knob que recorre las opciones de un menú/toggle (p. ej. 5 modos = 5 zonas del knob).
- **Macro** — un knob que mueve varios parámetros a la vez (p. ej. los 3 delays RGB).

## Contrato por base

| Base | FX | 1 Mezcla | 2 Tiempo | 3 Distorsión | 4 Color | 5 Firma |
|---|---|---|---|---|---|---|
| base18 | Time Machine 4 Glitch | Mezcla ✱ | `Cachesize` (memoria) | `Threshold` | Tono ✱ | `Threshold2` (opacidad feedback) |
| base19 | Slitscan | `Drywet` | `Int` (cache) | `Blackoffset` | Tono ✱ | `Menu` ramp en **pasos** (dirección del slit) |
| base20 | Feedback RGB Delay | `Opacity` (data mosh) | **Macro** delay RGB (`Reddelay` / `Bluedelay`) | `Size` | Tono ✱ (el edge color es blanco: girarle el tono no hace nada) | `Preshrink` (bloques del data mosh) |
| base21 | Optical Flow | Mezcla ✱ | `Float` (estela) | `Displaceweight1` | Tono ✱ | `Displaceweight2` (segunda capa) |
| base22 | Liquid Feedback | Mezcla ✱ | `Feedbackscale2` (estela) | `Feedbackscale` (zoom) | Tono ✱ | `liquid_feedback/displace1.displaceweighty` (flujo líquido, 0–0.04) |
| base23 | Pixel Sort | Mezcla ✱ | `Feedbackopacity` (estela) | `pixel_sort/displace1.displaceweighty` (largo del sort, 0–0.05) | Tono ✱ | `pixel_sort/thresh1.threshold` (umbral del sort) |
| base24 | ASCII | `Mastercontrast` | Estela ✱ | `Mastercellsize` | `Mastercolor` → tono | `Asciiactivefilter2` en **pasos** (caracteres / halftone / dither) |
| base25 | Warp Feedback | `Blend` | `Feedbackamt` | `Warpscale` | Tono ✱ | `Warprot` |
| base26 | — | ⛔ fuera del contrato hasta reescribir el shader (está vacío) | | | | |
| base27 | Trails | `Blend` | `Decay` | `Trailblend` | `Colorshift` | `Blendmode` en **pasos** (5 modos) |
| base28 | Bloom | `Bloom` | `Feedbackamt` | `Dispx` | `Glowcolor` → tono | `Glow` |
| base29 | Light Tunnel | `Blend` | `Pulsespeed` | `Radius` | `Invertamt` | `Feedbackamt` |
| base30 | RGBA Delay | `Drywet` | Estela ✱ | **Macro** separación RGB | Tono ✱ | **Macro** cantidad de delay (`Red`/`Green`/`Bluedelay`) |
| base31 | Radial Blur | `Drywet` | Estela ✱ | `Strength` | `Redpreshrink` (separación RGB) | `Samples` |
| base32 | Kaleidoscope | Mezcla ✱ | Velocidad de giro (anima `Rotatez`) | `Kaleidonum` | Tono ✱ | `Fullmode` en **pasos** (on/off) |

🔍 = el script de armado imprime los parámetros/uniforms internos de esa base y ahí elegimos;
si no hay nada útil, se usa la pieza universal más cercana.

## Cambios que trae el contrato

- **base21**: hoy el audio mueve directo `Displaceweight` y `Float`; pasa a la pestaña Audio estándar.
- **base32**: deja de leer `/project1/null50['ch1n26']`; `Fullmode` queda en el slot 5.
- **base24**: su pestaña `Master` ya era casi el contrato; solo se le suma la Estela ✱.
- **base20**: el `switch1` interno de 4 entradas sigue sin salir a nada; se deja como está.
- **base25–32**: nombres provisionales (Warp Feedback, Trails) para el Stream Deck; cámbialos si quieres.
