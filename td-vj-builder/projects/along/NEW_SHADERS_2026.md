# NEW SHADERS 2026 - Along TD FX

## Red base recomendada

```text
videoDeviceIn1
level_input
select_optional_crop
glsl_fx
level_output
null_out
```

Para feedback:

```text
videoDeviceIn1 -> glsl_fx input 0 -> level_output -> feedback1 -> level_feedback -> glsl_fx input 1
glsl_fx -> null_out
```

Uniforms comunes:

- `time`: `absTime.seconds`
- `intensity`: cantidad emocional del look
- `speed`: velocidad de respiracion/animacion
- `distortion`: deformacion espacial
- `audioReactive`: energia externa desde audio analysis
- `feedbackAmount`: mezcla de eco visual o memoria de frame

## 1. COBALTO FANTASMA

Concepto emocional: frialdad intima, recuerdo azul, vulnerabilidad contenida. Debe sentirse como mirar una confesion nocturna a traves de una pantalla ligeramente triste.

Comportamiento visual: convierte la camara en monocromo cobalto, conserva altas luces con glow suave, agrega aberracion cromatica minima hacia los bordes y una respiracion lenta en el brillo.

Red TouchDesigner:

```text
videoDeviceIn1
level_soften
blur_pre_glow
glsl_cobalto_fantasma
level_out
null_out
```

Parametros importantes: `intensity` controla glow; `distortion` controla separacion RGB; `speed` controla respiracion; `feedbackAmount` oscurece bordes con memoria fria.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

build_fx_comp(op("/project1"), EFFECTS[0], x=0, y=0)
```

Shader: `shaders/01_cobalto_fantasma.frag`

## 2. GIRASOL CENITAL

Concepto emocional: luz calida que cae desde arriba, retrato romantico y expuesto, como una memoria feliz que tambien pesa.

Comportamiento visual: genera halo cenital ambar, levanta exposicion en altas luces, calienta pieles y crea una corona suave alrededor del centro superior.

Red TouchDesigner:

```text
videoDeviceIn1
level_input
blur_soft
glsl_girasol_cenital
composite_optional_over
null_out
```

Parametros importantes: `intensity` sube halo y bloom; `audioReactive` agrega respuesta en highlights; `distortion` curva ligeramente el halo.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

build_fx_comp(op("/project1"), EFFECTS[1], x=260, y=0)
```

Shader: `shaders/02_girasol_cenital.frag`

## 3. CUARTO INCLINADO

Concepto emocional: habitacion imposible, intimidad desorientada, espacio mental que se dobla sin volverse agresivo.

Comportamiento visual: inclina y comprime la imagen con perspectiva falsa, agrega lineas sutiles tipo pared/piso y oscurece bordes para crear una sensacion de cuarto surreal.

Red TouchDesigner:

```text
videoDeviceIn1
level_input
glsl_cuarto_inclinado
edge_optional
level_out
null_out
```

Parametros importantes: `distortion` define la arquitectura imposible; `speed` anima el balanceo; `intensity` colorea lineas y sombras.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

build_fx_comp(op("/project1"), EFFECTS[2], x=520, y=0)
```

Shader: `shaders/03_cuarto_inclinado.frag`

## 4. CORAZON MASCOTA

Concepto emocional: ternura rara, cartoon vulnerable, afecto jugueton sin perder melancolia.

Comportamiento visual: crea un campo de distorsion con forma de corazon, infla suavemente la imagen, posteriza colores y agrega contorno calido tipo sticker vivo.

Red TouchDesigner:

```text
videoDeviceIn1
level_input
glsl_corazon_mascota
blur_optional_tiny
composite_optional
null_out
```

Parametros importantes: `distortion` infla el corazon; `intensity` aumenta posterizacion y candy tint; `audioReactive` hace que el centro respire.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

build_fx_comp(op("/project1"), EFFECTS[3], x=780, y=0)
```

Shader: `shaders/04_corazon_mascota.frag`

## 5. PARABRISAS AMBAR

Concepto emocional: noche urbana vista desde adentro de un coche, vidrio mojado, luces calidas y nostalgia en movimiento.

Comportamiento visual: genera gotas y streaks procedurales, refracta el video como cristal mojado y convierte highlights en reflejos ambar/sodio.

Red TouchDesigner:

```text
videoDeviceIn1
level_input
blur_highlights
glsl_parabrisas_ambar
level_out
null_out
```

Parametros importantes: `distortion` controla refraccion de gotas; `intensity` controla brillo ambar; `speed` mueve lluvia; `audioReactive` enciende reflejos rosas.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

build_fx_comp(op("/project1"), EFFECTS[4], x=0, y=-260)
```

Shader: `shaders/05_parabrisas_ambar.frag`

## 6. RAYO POP POSTERIZADO

Concepto emocional: energia pop surreal, flash romantico, golpe grafico sin volverse rave.

Comportamiento visual: posteriza la camara, crea un rayo central ondulante, agrega flash suave y acentos rosa/amarillo/cian.

Red TouchDesigner:

```text
videoDeviceIn1
level_input
glsl_rayo_pop_posterizado
level_flash_control
null_out
```

Parametros importantes: `intensity` baja niveles de posterizacion; `audioReactive` sube flashes; `distortion` empuja la imagen alrededor del rayo.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

build_fx_comp(op("/project1"), EFFECTS[5], x=260, y=-260)
```

Shader: `shaders/06_rayo_pop_posterizado.frag`

## 7. ECO CONFESIONAL

Concepto emocional: memoria sentimental, confesion repetida, rastro lento de presencia humana.

Comportamiento visual: mezcla imagen actual con ecos desplazados y, si existe input 1, con feedback real. El resultado es un ghosting lento, rosado y nocturno.

Red TouchDesigner:

```text
videoDeviceIn1 -> glsl_eco_confesional input 0
glsl_eco_confesional -> level_feedback -> feedback1 -> glsl_eco_confesional input 1
glsl_eco_confesional -> null_out
```

Parametros importantes: `feedbackAmount` controla memoria; `distortion` expande el eco; `speed` mueve respiracion; `intensity` sube tinte confesional.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

comp = build_fx_comp(op("/project1"), EFFECTS[6], x=520, y=-260)
# Agrega feedbackTOP y conectalo al segundo input del glsl_fx para eco real.
```

Shader: `shaders/07_eco_confesional.frag`

## 8. VERTICAL C100T

Concepto emocional: visualizer movil, fan-cam romantica, degradacion digital nostalgica y formato vertical de festival.

Comportamiento visual: encierra el video en un marco 9:16, oscurece laterales, agrega split RGB horizontal, scanlines finas, jitter por filas y posterizacion ligera.

Red TouchDesigner:

```text
videoDeviceIn1
crop_or_fit_optional
glsl_vertical_c100t
level_out
null_out
```

Parametros importantes: `distortion` controla jitter y split RGB; `intensity` controla degradacion; `audioReactive` ilumina bordes.

Script Python:

```python
from along_td_fx.builders.build_all_fx import build_fx_comp
from along_td_fx.config import EFFECTS

build_fx_comp(op("/project1"), EFFECTS[7], x=780, y=-260)
```

Shader: `shaders/08_vertical_c100t.frag`
