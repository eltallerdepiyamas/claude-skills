# CLAUDE.md — Paloma Murphy

> Contexto de trabajo para Claude Code. Leer esto **antes** de cualquier tarea en este proyecto.

## Qué es
Set de **visuales generativas** para el show de **Paloma Murphy**, con estética de **marquesina de
casino ~1970**: formas planas de alto contraste definidas por contornos de bombillas con chase
secuencial. Salida a **panel LED grande**. Sin input de video (generativo puro). Research completo
en `research_casino_marquee.md`.

## Paths y estructura
- Raíz del proyecto: `H:\Mi unidad\01. FREELANCE\2026\37. PALOMA MURPHY\01. EDITABLES\`

```
01. EDITABLES\
│   CLAUDE.md                      ← este archivo (raíz)
│   research_casino_marquee.md     ← brief estético
│   PALOMA MURPHY.toe              ← .toe del proyecto
├── shaders\                       ← .frag de referencia (el código va embebido en cada builder)
└── scripts\                       ← setup_baseN_<name>.py (builders idempotentes)
```

- Correr un builder desde TextPort:
  `exec(open(r'H:\Mi unidad\01. FREELANCE\2026\37. PALOMA MURPHY\01. EDITABLES\scripts\setup_baseN_<name>.py').read())`

## Rig (recordatorio)
- `/project2`: base1–16 = VISUALES · base17 = layout de cámaras (`escena_modular`) ·
  base18–24 / base38–45 = EFECTOS de cámara.
- **No renombrar** ninguna baseX: el midisampler mapea por número de base.
- Resolución de salida: canales `resX`/`resY` del Constant CHOP `constant45`;
  referencia canónica desde un nodo dentro de baseN:
  `parent(2).op('constant45')['resX']` / `['resY']`.
- Audio: `audio_in` (Select CHOP `low mid high`) desde `../../project1/null4` (= `/project1/null4`).

## Bases ocupadas
| Base | Pieza | Signature (slider 5) | Rango |
|------|-------|----------------------|-------|
| base1 | `marquee_frame` | `Density` (marco exterior) | 16–120 (def 48) — Layout de marcos concéntricos (`Scale`/`Repeat`/`Gap`) |
| base2 | `atomic_starburst` | `Rays` | 4–24 (def 12) |
| base3 | `bulb_arrow` | `Direction` | 0–360° (def 0) — página **Icon** con 17 formas: Arrow/PM/Diamond/Heart/Spade/Club/Seven/Star/Lightning/Horseshoe/Cherry/Cocktail/Dollar/Eye/Wheel/Crown/Pyramid |
| base4 | `dot_matrix_field` | `Density` | 6–48 (def 20) |
| base5 | `spin_ring` | `Rings` | 2–8 (def 4) |
| base6 | `chevron_march` | `Count` | 3–16 (def 7) |
| base7 | `circulos` | `Rings` | 2–12 (def 5) |
| base8 | `sun_rays` | `Rays` | 4–48 (def 12) — sol imaginario abajo, rayos radiales por el arco superior con largo oscilante |
| base9 | `checker_pulse` | `Cells` | 4–24 (def 8) — tablero de bombillas con celdas on/off alternando por `Mode` (Flip/Row/Col/Diag). Ritmo binario duro |
| base10 | `spiral_hypno` | `Arms` | 2–8 (def 4) — brazos de espiral saliendo del centro y girando; `Twist` (0.5–3) controla torsión |
| base11 | `pinstripe_ticker` | `Bands` | 2–10 (def 5) — bandas paralelas de bombillas fijas cuya secuencia da ilusión de ticker corriendo; `Angle` (0–180°) rota el rig |
| base12 | `radial_bars` | `Bars` | 6–48 (def 16) — barras radiales 360° con hueco central; `Radius` (0.1–0.5), `Barmode` (Wave/Sync/Random) |
| base13 | `wave_ripple` | `Waves` | 1–8 (def 3) — anillos naciendo del centro y expandiéndose; `Falloff` (0.2–1) cuánto viven |
| base14 | `halftone_pulse` | `Density` | 6–48 (def 20) — grid donde el tamaño del bulb sigue una onda; `Angle` (dir de la onda), `Wavemode` (Linear/Radial/Diagonal2) |
| base15 | `oscilloscope_wave` | `Cycles` | 1–8 (def 3) — senoide serpenteando horizontal; `Lines` (1–5) apiladas |
| base16 | `plaza_grid` | `Rows` | 4–24 (def 10) — cuadrícula perspectiva tipo suelo Vegas/Tron corriendo hacia el horizonte; `Horizon` (0.2–0.7) altura del horizonte |

> **base17** NO es un slot de contenido: es el host de layout `escena_modular`
> (composición de cámaras). No construir visuales ahí. Los slots de contenido
> WASP4 empiezan en base18 (ver "WASP4 — luminarias físicas" más abajo).

## Contrato por base (invariante)
- **5 sliders** en orden de rol, cada uno nombrado como el uniform que maneja:
  1 `Intensity`→`u_intensity` (0–2) · 2 `Speed`→`u_speed` (0–4) · 3 `Distort`→`u_distort` (0–1) ·
  4 `Colormix`→`u_colormix` (0–1) · 5 `<Signature>`→`u_sig`.
- **Bypass** (toggle) separado: `switch1` entre el GLSL y un negro (`bypass_black`).
- **Página Audio**: `Audioreact`, `Low/Mid/High` (suman), `Audiotarget` (a qué slider empuja la
  energía), `Audiomult` (0–3). La suma se hace en la expresión del uniform vía `mod('audio_util')`.
- **Página Layout** (no audio-targeteable). Se decide **pieza por pieza**; el layout NO es
  tiling con `fract` (esa idea quedó descartada). Por defecto para las 6 piezas no-base1:
  `Scale` (0.25–4, `u_scale`) y `Chasedir` (menu Normal/Invertido, `u_dir` = +1/−1).
  - **base1 `marquee_frame`**: `Scale` (0.25–1.2; 1.0 = marco pegado al borde), `Repeat`
    (1–10, marcos concéntricos hacia adentro), `Gap` (0.06–0.40, separación) y `Chasedir`.
    Uniforms: `u_scale`, `u_repeat`, `u_gap`, `u_dir`.
- **Extras de Visual** (no audio-targeteables, van en la misma página Visual pero **no** entran
  al menú `Audiotarget`): `Chasemode` (menu Duro/Rampa, `u_ramp` = 0.0/1.0) y `Tail`
  (0.1–1, `u_tail`) — el chase con cola degradada recorre la paleta y da el efecto "iluminando".
- Colores: 3 pickers RGB `Colora/Colorb/Colorc` → `u_color1/2/3`.
  Paleta: oro `#FFB800` / rojo `#F21A33` / azul eléctrico `#0A85FF`.

## Estructura de nodos por base
`audio_util` (Text DAT módulo) · `<name>_frag` (Text DAT shader) · `audio_in` (Select CHOP) ·
`glsl_<name>` (GLSL TOP, uniforms en página Vectors) · `bypass_black` (Constant) ·
`switch1` (Switch, index = `parent().par.Bypass`) · `out1` (Out; `bgtop=./out1` para thumbnail).

## Cómo trabajan los builders
Cada `setup_baseN_<name>.py` es **standalone e idempotente**: hace snapshot de los parámetros
custom, destruye sus hijos gestionados, reconstruye y restaura los valores. Se puede re-correr
sin miedo. El binder de uniforms **prueba nombres de parámetro** (tolerante a versión) y avisa con
`[WARN]` si no encuentra los slots de la página Vectors de tu build.

## Puntos a verificar en TD (iterar por TextPort)
1. **Slots de uniform del GLSL TOP** (página Vectors): si aparece `[WARN]`, pasar los nombres de
   parámetro reales para fijar el binder.
2. **`outputresolution`**: se intenta `'custom'` / `'Custom Resolution'`; confirmar el valor de menú.
3. **Componentes RGB** (`Colorar/Colorag/Colorab`): confirmar naming si el color no engancha.
4. **Fuente de audio**: `audio_in` apunta a `../../project1/null4` por default; repuntear si Sebas
   usa su propio Select.

## Notas del show
- **Fuente de resolución del rig** = Constant CHOP `constant45` (canales `resX`/`resY`),
  **no** parámetros de `escena_modular`. Los builders usan
  `parent(2).op('constant45')['resX']` / `['resY']` en `resolutionw`/`resolutionh` del GLSL TOP.
- **Nunca** usar `me.width`/`me.height` en expresiones de parámetros del propio GLSL TOP:
  crea un cook dependency loop con el nodo `_info` (el parámetro del nodo termina dependiendo
  del output cocinado del mismo nodo). El uniform `u_res` se bindea a
  `me.par.resolutionw` / `me.par.resolutionh` (referencia a parámetro, no a propiedad cocinada).
- **Naming de parámetros custom en TD**: solo la primera letra en mayúscula (`Resw`, no `ResW`);
  aplica a todos los custom pars que se creen o consulten.
- **Layout ≠ tiling**: la repetición del visual no es en retícula con `fract`; los focos deben
  poder abarcar toda la pantalla. base1 lo hace con marcos concéntricos hacia adentro
  (`Repeat`/`Gap`); las otras 6 piezas se decidirán una por una. Los uniforms `u_tiles` y
  el helper `layoutUV` de la Parte 2 quedaron descartados.

## WASP4 — luminarias físicas
Track paralelo al panel LED grande: **luminarias físicas WASP4** con 2 caras y varias
secciones de distinta densidad / tipo de LED. Las bases WASP viven fuera del rango
base1–16 (que es el panel) y usan **resoluciones fijas** (no `constant45`).

### Secciones por unidad (referencia; el mapeo DMX se resuelve fuera)
| Sección | Cara | Canales | Qué es | Layout físico |
|---------|------|---------|--------|----------------|
| **A**   | Cara 1 | 16 CH | 4 unidades RGBW (4 canales c/u) | grid 2×2 (1,2 arriba / 3,4 abajo) |
| **B**   | Cara 2 | 9 CH  | 9 dots blancos (brillo, sin color) | grid 3×3 |
| **C-A** | Cara 2 | 27 CH | 9 píxeles RGB (3 canales c/u) | grid 3×3, **superpuesto físicamente** al mismo layout que B |

Sección B y C-A comparten layout: una **sola fuente RGB 3×3** las alimenta a las dos —
el RGB va directo a C-A; el brillo (luminancia `dot(rgb, vec3(0.299,0.587,0.114))`)
va a B. La derivación se hace en la etapa de DMX, fuera de estas bases.

### Resolución (dos enfoques según base)

**Nativo (base18, 19, 20, 24):** texturas se generan a **resolución nativa del hardware**
(2 o 3), sin downsample. `outputresolution=custom`, `resolutionw`/`resolutionh` = constante
literal (2 o 3), `u_res` se pasa como constante `(2.0, 2.0)` o `(3.0, 3.0)`. Cada píxel =
una unidad física.

**Híbrido (base21, 22, 23):** GLSL renderiza a **128×128 (high-res)** y luego un `fitTOP`
(nombrado `fit_a`/`fit_b`) hace downsample al target nativo (2×2 / 3×3) con filtro
`gaussian` (fallback `linear`, luego `best`) y `fit='stretch'`. Esto permite:
- Formas / dots / líneas moviéndose **sub-celda** (motion smooth, no saltos discretos)
- Slider `Scale` funcional para zoom del contenido antes del downsample
- Contornos antialiasing (SDFs, líneas, círculos se ven bien al downsample)

La salida al DMX **sigue siendo nativa** (después del downsample) — el pipeline hardware
no cambia. Solo se agregan 2 nodos por contenedor (`fit_a`, `fit_b`) entre el GLSL y `null_a`/`null_b`.

`u_res` en híbrido = (128, 128) (los shaders no lo usan porque trabajan en NDC `[-1,1]`
via `vUV.st * 2 - 1`).

### Bases ocupadas (WASP4)
| Base | Pieza | Notas |
|------|-------|-------|
| base18 | `wasp_faceA_pulse` (2×2) + `wasp_faceB_ripple` (3×3) — **Propuesta 1** | Cada cara tiene 6 patrones seleccionables por menú: **Cara A** (`Apattern`): Chase/Rows/Cols/Diag/Blink/Sparkle. **Cara B** (`Bpattern`): Ripple/Rotate/Scan/Cross/Blink/Sparkle. Sliders `Speed`/`Colormix`/`Signature` **independientes por cara** (`Aspeed`/`Bspeed`, etc.); `Intensity` y `Distort` (=desfase de fase A↔B) son compartidos, y los 3 pickers `Colora/b/c` también (paleta unificada del rig). Página Audio con **dos** `Audiotarget` (uno por cara), `Audiomode` (Add / Mult / Gate) y `Smoothing` (0–1). El pipeline de audio pasa por `audio_env` (Lag CHOP entre `audio_in` y los consumidores) cuyos `lag1`/`lag2` se conducen desde `Smoothing` + `Audiomode` (Gate = ataque instantáneo + release largo; Add/Mult = attack=release simétrico). El contenedor tiene **una sola salida = `out1`**; el menú `Face` (A / B / Ambas) selecciona el contenido vía `switch_content` (Switch TOP con inputs `null_a` / `null_b` / `preview_both`). `preview_both` es un Layout TOP horizontal ampliado a 512×256 con filtro nearest. Cara A cruda en `base18/null_a` (2×2), Cara B cruda en `base18/null_b` (3×3) — el pipeline DMX las tapa por path para alimentar Sección A y Secciones B + C-A respectivamente. |
| base19 | `wasp_faceA_frame` (2×2) + `wasp_faceB_reels` (3×3) — **Propuesta 2 (slot machine)** | Misma arquitectura que base18 (single `out1`, `null_a`/`null_b` para DMX, preview, Face, Bypass, 3 modos de audio + Smoothing). **Cara A** "frame lights" — menú `Apattern` con 5 modos: `Coin` (las 4 respiran juntas, Signature = profundidad), `Alt` (diagonales alternan, Signature = softness del crossfade), `Chase` (clockwise clásico, Signature = cola), `Slam` (las 4 flashean JUNTAS en beats con envolvente de decay + 30% beats silenciados random para no sentirse mecánico; Signature = frecuencia 1–4/s), `Steady` (siempre lit con color rotando). **Cara B** "slot reels" — menú `Bpattern` con 3 modos: `Spin` (3 columnas = 3 reels con velocidades independientes; Signature = spread), `Aligned` (los 3 reels en sync → franjas horizontales), `Chaos` (drift continuo + salto random por celda cada tick; Signature = velocidad general). Los "símbolos" del reel son los 3 pickers `Colora/b/c` en ciclo (color1→color2→color3→…) vía `symbolColor()`; todas las celdas siempre lit (un reel de slot no se apaga). `Audiotarget` de Cara B default = `Bspeed` (audio acelera el giro). Nota: en Slam y Chaos el tick es **independiente de Speed** (movimiento garantizado aun con Speed = 0). |
| base20 | `wasp_faceA_ambient` (2×2) + `wasp_faceB_ambient` (3×3) — **Propuesta 3 (ambient / breath)** | El "modo calmo" del rig, contraste conceptual con base18 (rítmico) y base19 (slot). **Puro sine wave** — sin ticks, sin random, sin envolventes → imposible que se pegue o actúe raro. **Cara A** "corner breath" — menú `Apattern` con 5 modos: `Sync` (las 4 respiran juntas), `Alt` (diagonales alternan en antifase), `Rotate` (brillo rota clockwise por las 4 corners), `Wave` (onda con offset por posición, cascada suave), `Steady` (siempre lit, color rotando). Signature = profundidad del breath. **Cara B** "gradient breath" — menú `Bpattern` con 4 gradientes: `Radial` (desde el centro), `LinearH` (horizontal), `LinearV` (vertical), `Diagonal` (a 45°). El gradiente recorre la paleta (rango controlado por Signature: 0 = ~15% subtle, 1 = paleta completa 3 zonas) + brightness breath sinusoidal (Distort desfasa el breath vs Cara A). Speed controla ritmo del breath + velocidad del drift de la paleta. Ideal para bajar la energía del show / transiciones. |
| base21 | `wasp_path` (mismo shader para A y B) — **Propuesta 4 (path tracer, híbrido)** | Un dot (o varios) trazando caminos geométricos en NDC. Menú `Apattern`/`Bpattern` con 5 modos: `Circle` (órbita), `Square` (perímetro cuadrado), `Figure8` (lemniscate), `Spiral` (radio creciente + wrap), `Multi` (3 dots a 120°). Slider **`Scale`** por cara (0.25–2.0) zoom sub-celda del path. Signature = tamaño del dot. Cara A y B usan el mismo shader; solo cambia el target de downsample (`fit_a` → 2×2, `fit_b` → 3×3, filter `gaussian`). |
| base22 | `wasp_sweep` (mismo shader para A y B) — **Propuesta 5 (line sweep, híbrido)** | Líneas barriendo o rotando por el plano. Menú con 5 modos: `HSweep` (línea horizontal senoidal vertical), `VSweep` (vertical), `DiagRot` (línea rotando alrededor del centro), `Radial` (rayo desde el centro tipo manecilla de reloj), `Cross` (+ pulsante). Slider **`Scale`** = amplitud del barrido, `Signature` = grosor de la línea. |
| base23 | `wasp_contour` (mismo shader para A y B) — **Propuesta 6 (contour marquee, híbrido)** | El **equivalente WASP del `marquee_frame` de base1**: contornos de figuras con "bombillas" corriendo por el perímetro en chase. Menú con 4 formas: `Circle`, `Square` (SDF), `Diamond` (norma L1), `Cross` (+ hueco). El chase corre por posición angular con envolvente `pow(1-phase, 3)`. Slider **`Scale`** = tamaño de la figura, `Signature` = grosor del contorno. Distinto a base18-20 porque usa **contornos vectoriales** (no cell-based). |
| base24 | `wasp_faceA_vu` + `wasp_faceB_vu` — **Propuesta 7 (VU meter, nativo)** | Puro audio-reactivo, res **nativa** (sin high-res, sin downsample). Único que bindea audio DIRECTO al shader vía uniforms `u_low`/`u_mid`/`u_high` (helper `bandv()` en `audio_util`, bypassea `driven()` porque en VU todas las bandas alimentan simultáneas). **Cara A** peak indicators — 4 modos: `Bands` (TL=low, TR=mid, BL=high, BR=master), `Mirror` (top=low, bot=high espejado), `Flash` (las 4 juntas si master > threshold), `Stack` (progresivo TL→TR→BL→BR según master). **Cara B** meter — 3 modos: `Vertical` (columnas = low/mid/high, llenan desde abajo), `Horizontal` (filas = bandas, llenan izq→der), `Radial` (centro=master, aristas=low, esquinas=high). Slider **`Scale`** = amplificador global de bandas (0.25–3.0). Default `Audiotarget` = `Ascale`/`Bscale` (audio empuja el amp). `Audiomult` default = 2.0 (VU necesita más ganancia). Todas las bandas ON por default. Speed no aplica. |
