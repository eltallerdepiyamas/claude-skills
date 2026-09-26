# TAREA — WASP4, Propuesta 1 (contenido para base18)

> Instrucciones para Claude Code. Lee `CLAUDE.md` y `research_casino_marquee.md` primero.
> **No toques TouchDesigner** — los builders los corre Sebas desde el TextPort.
> Esto es una **prueba**: primero validamos esta propuesta antes de pensar la Propuesta 2.

## Contexto — la luminaria WASP4

Sebas probó físicamente una luminaria con **2 caras**, cada una con secciones de distinto
tipo y resolución de LED:

| Sección | Cara | Canales | Qué es | Layout físico |
|---------|------|---------|--------|----------------|
| **A** | Cara 1 | 16 CH | 4 unidades RGBW (4 canales c/u) | grid 2×2 (1,2 arriba / 3,4 abajo) |
| **B** | Cara 2 | 9 CH | 9 dots blancos (brillo, sin color) | grid 3×3 |
| **C-A** | Cara 2 | 27 CH | 9 píxeles RGB (3 canales c/u) | grid 3×3, **superpuesto físicamente** al mismo layout que B |

Las direcciones DMX de arranque (5 filas = 5 unidades físicas en el rig) son solo referencia —
**el mapeo a DMX no se resuelve en esta tarea**; esta tarea genera únicamente el contenido
visual (texturas GLSL de baja resolución) que después se exportará en la etapa de DMX del rig,
fuera de este alcance.

## Decisión de resolución (confirmada con Sebas)

Se **muestrea directo a la resolución nativa del hardware** — nada de generar en alta resolución
y hacer downsample. Esto significa:

- Textura de **Cara A**: resolución fija **2×2 px** (cada píxel = una unidad RGBW).
- Textura de **Cara B**: resolución fija **3×3 px** (cada píxel = un dot blanco + un píxel RGB
  en la misma celda — ver más abajo cómo se derivan ambos de una sola fuente).

Esto es intencional y **distinto** al patrón de resolución de los bases 1–16 (que usan
`parent(2).op('constant45')['resX']/['resY']` para llenar el panel LED grande). Aquí NO se usa
esa referencia — la resolución es una constante fija (2 o 3), no una expresión.

## Ubicación

**base18** (primer slot libre de EFECTOS de cámara; base17 es el host de layout
`escena_modular`, no un slot de contenido). Reservar mentalmente base19 para la Propuesta 2
(no se construye todavía).

## Objetivo de diseño

Contenido **generativo puro**, distinto en forma al de base1–16, pero que **acompañe**
la misma familia visual: mismo tiempo base (`absTime.seconds`), misma paleta
(oro `#FFB800` / rojo `#F21A33` / azul eléctrico `#0A85FF`), mismo espíritu de "luz que
viaja" del chase — solo que aquí, por la resolución mínima, el efecto es un **pulso/chase
de pocas celdas** en vez de bombillas individuales.

### Cara A (2×2) — `wasp_faceA_pulse`
Chase circular entre las 4 celdas (1→2→4→3→1, sentido de las manecillas siguiendo el layout
físico de la imagen), con solape entre celdas vecinas controlado por `Signature` (para que en
Signature alto varias unidades queden semi-encendidas a la vez, tipo "ola", y en Signature bajo
sea un golpe seco de una sola unidad).

### Cara B (3×3) — `wasp_faceB_ripple`
Ripple concéntrico desde el centro hacia las esquinas (mismo espíritu que `circulos` de base7,
pero resuelto a propósito en solo 9 celdas). Se calcula **una sola fuente RGB de 3×3**; a partir
de ahí:
- El **canal RGB** de esa fuente alimenta directamente la Sección C-A (9 píxeles RGB).
- El **brillo** de esa misma fuente (luminancia: `dot(rgb, vec3(0.299,0.587,0.114))`) alimenta
  la Sección B (9 dots blancos) — así ambas secciones quedan sincronizadas por diseño, sin
  duplicar lógica.

## Contrato de parámetros (página `Visual`, en base18)

| Par | Tipo | Rango | Default | Uniform | Rol |
|-----|------|-------|---------|---------|-----|
| `Intensity` | Float | 0–2 | 1.0 | `u_intensity` | slider 1 |
| `Speed` | Float | 0–4 | 1.0 | `u_speed` | slider 2 |
| `Distort` | Float | 0–1 | 0.0 | `u_distort` | slider 3 (offset de fase entre Cara A y Cara B, ver abajo) |
| `Colormix` | Float | 0–1 | 0.35 | `u_colormix` | slider 4 |
| `Signature` | Float | 0–1 | 0.35 | `u_sig` | slider 5 (ancho del pulso / solape entre celdas) |
| `Face` | Menu | `A` / `B` / `Ambas` | `Ambas` | — (controla bypass por cara, ver abajo) |
| `Bypass` | Toggle | — | 0 | — | apaga ambas caras a negro |

Estos 5 sliders son los que lista `Audiotarget` en la página `Audio` (mismo contrato que
base1–16: `Audioreact`, `Low`/`Mid`/`High`, `Audiotarget`, `Audiomult`).

`Distort` aquí no deforma geometría (no aplica a 2×2/3×3) — se reutiliza como **desfase de
fase entre Cara A y Cara B** (`0` = perfectamente sincronizadas, `1` = una cuarta parte de
ciclo de diferencia), para poder desincronizarlas si se ven "planas" corriendo idénticas.

## Uniforms compartidos (HEADER, igual criterio que base1–16)

```glsl
uniform float u_time, u_intensity, u_speed, u_distort, u_colormix, u_sig;
uniform vec2  u_res;
uniform vec3  u_color1, u_color2, u_color3;   // oro, rojo, azul (mismos valores del rig)
```

Paleta: reusar la MISMA función `palette()` del header de base1–16 (copiar, no reinventar).

## Estructura de nodos en base18

```
audio_util          (Text DAT, mismo modulo _band/energy/driven que base1-16)
facea_frag           (Text DAT, shader Cara A)
faceb_frag           (Text DAT, shader Cara B)
audio_in             (Select CHOP -> ../../project1/null4, canales low mid high)
glsl_faceA           (GLSL TOP, pixeldat=facea_frag, resolution FIJA 2x2)
glsl_faceB           (GLSL TOP, pixeldat=faceb_frag, resolution FIJA 3x3)
black_a, black_b      (Constant TOP, negro, para bypass por cara)
switch_a              (Switch: in0=glsl_faceA, in1=black_a)
switch_b              (Switch: in0=glsl_faceB, in1=black_b)
outA                 (Out TOP <- switch_a)   -- Seccion A (2x2 RGBW)
outB                 (Out TOP <- switch_b)   -- Secciones B+C-A (3x3: luminancia + RGB)
```

Lógica de los switches (expresión en `index`):

```python
# switch_a.par.index
1 if (parent().par.Bypass or str(parent().par.Face) == 'B') else 0
# switch_b.par.index
1 if (parent().par.Bypass or str(parent().par.Face) == 'A') else 0
```

`bgtop` del contenedor → `./outB` (referencia visual más rica para el thumbnail).

## Reglas (mismas de siempre)

- Todos los uniforms asignados en la página **Vectors** de cada GLSL TOP.
- Sin indexado dinámico de arrays.
- Builder **standalone e idempotente** (mismo patrón snapshot → destruir hijos → reconstruir
  → restaurar que ya usan los builders de base1–16). Nombre: `setup_base18_wasp_propuesta1.py`,
  en `scripts\`.
- Guardar los `.frag` de referencia en `shaders\` (`wasp_faceA_pulse.frag`,
  `wasp_faceB_ripple.frag`).

## Actualizar `CLAUDE.md`

Agregar sección nueva **"WASP4 — luminarias físicas"** con:
- La tabla de secciones/canales/layout de arriba (como referencia, sin resolver DMX).
- Nota: resolución de estas bases es **fija** (2×2 / 3×3), no viene de `constant45` —
  eso es exclusivo del panel LED de base1–16.
- base18 = Propuesta 1 (`wasp_faceA_pulse` + `wasp_faceB_ripple`). base19 reservado para
  Propuesta 2 (pendiente, no construir aún).
- Aclarar en "Bases ocupadas" que base17 es el host de layout, no un slot de contenido.

## Al terminar

Reporta qué archivos creaste/tocaste. Sebas corre el builder desde TextPort:

```python
exec(open(r'H:\Mi unidad\01. FREELANCE\2026\PALOMA MURPHY\scripts\setup_base18_wasp_propuesta1.py').read())
```

Si algo truena o el TextPort marca `[WARN]`, Sebas te pasa el output para iterar —
igual que con base1.
