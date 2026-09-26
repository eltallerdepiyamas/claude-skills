# PROYECTO: ESCUBY — DJ sonidero (Morelia)

Generado por td-vj-builder. Contexto en disco para este show.

Estetica: XV anos mexicanos con torcida punk/dreampop, pero el show visual es
**minimalista y elegante**. Mucho espacio negativo, movimiento lento y
deliberado, sin glitch ni saturacion.

Paleta ESTRICTA (no agregar otros colores):
- Azul Klein  `#002FA7`  (0.000, 0.184, 0.655)
- Blanco      `#FFFFFF`
- Negro       `#000000`

Audio: reactividad SUTIL, respiracion lenta (no pulso agresivo).

## Rutas (verificar que coincidan con esta maquina)
- Proyecto .toe: `E:/tiani/Documents/Touch Designer Projects/01. EDITABLES/ESCUBY/ESCUBY.toe`
- Shaders de visuales: `visuals_glsl/shaders/`
- Shaders de efectos:  `effects_glsl/shaders/`
- Builders de visuales (setup_baseXX_*.py): `visuals_glsl/`
- Builders de efectos  (setup_baseXX_*.py): `effects_glsl/`
- Audio canonico (CHOPs del audio_in): `../../project1/null4`  (canales: low mid high)

## Rig (fijo — no renombrar bases)
- Visuales:  base1–base16
- base17:    host de camaras / escena_modular / layouts (layout_*)
- Efectos:   base18–base24, luego base38–base45
- GLSL output resolution: ligado a `escena_modular` (`ResW`/`ResH`), fallback `me.width/me.height`

## Bases ocupadas en este show
| Base | Categoria | Nombre | Shader | Notas |
|------|-----------|--------|--------|-------|
| base1 | visual generativo | strobe_flash | visuals_glsl/shaders/strobe_flash.glsl | estrobos full-frame, FlashColor menu (Klein/blanco/negro), Rate capeado a 8 Hz (tope SEGURO), duty cycle y edge softness modulables, off siempre negro real |
| base2 | visual generativo | gradient_flow | visuals_glsl/shaders/gradient_flow.glsl | herramienta de gradientes Klein full-frame, 6 ramptypes via menu, Period 1-12, Speed signed, Phase manual, Softness (posterizado <-> degrade suave) |
| base3 | visual generativo | espiral_klein | visuals_glsl/shaders/espiral_klein.glsl | espiral logaritmica Klein full-frame, hipnotica, brazos uniformes a cualquier radio (log-spiral self-similar), Tightness=0 colapsa a slices radiales |
| base4 | visual generativo | sweep_wipe | visuals_glsl/shaders/sweep_wipe.glsl | banda Klein que barre la pantalla en un eje rotable, util para wipes/transiciones, off siempre negro (blend Add) |
| base5 | visual generativo | grid_klein | visuals_glsl/shaders/grid_klein.glsl | cuadricula cartesiana de cuadrados Klein latiendo s/ negro, onda diagonal lenta, deriva sutil del grid completo |
| base6 | visual generativo | bandera_klein | visuals_glsl/shaders/bandera_klein.glsl | bloque Klein solido casi full-frame + N barras negras deslizandose, motion graphics Saul Bass, max impacto solido |
| base7 | visual generativo | checker_opart | visuals_glsl/shaders/checker_opart.glsl | damero op-art gigante full-frame Klein/negro, slow rotacion + warp opcional + pulse sutil, estilo Bridget Riley 60s |
| base8 | visual generativo | lineas_flujo | visuals_glsl/shaders/lineas_flujo.glsl | lineas paralelas Klein curvandose como topografica, multi-octava de senos para flow organico, fwidth() para AA correcto a cualquier density |
| base9 | visual generativo | gradient_klein | visuals_glsl/shaders/gradient_klein.glsl | gradiente VERDADERO full-frame (un wash continuo, sin bandas), 6 direcciones, 3 pares de color (klein/negro, blanco/negro, klein/blanco) + Invert |
| base18 | efecto (logos) | logo_fx | effects_glsl/shaders/logo_fx.glsl | suite v3: cadena minima asset_in->glsl_fx (transform manual) con alpha sagrado, 5 sliders glow/strobo/echo/klein-tint/pulse + Opacity master fade |

## Layouts en este show (dentro de base17/escena_modular)
| Nombre | Camaras | Notas |
|--------|---------|-------|
| (ninguno) | | |

## Contrato de parametros (recordatorio)
- 5 sliders por rol: intensidad, velocidad, distorsion, color, firma.
- Bypass aparte. Pagina Audio: Audioreact + Low/Mid/High + Audiotarget + Audiomult.
- Audio se suma en la EXPRESION del uniform (clamp), no en el slider, para no chocar con MIDI.
- En ESCUBY el `Audiotarget` por defecto es **Breath** (latido), para que el show
  respire con el bombo sin que la grid "salte".

## strobe_flash (base1) — 5 sliders + extras
**Forma:** estrobos full-frame, abstracto/geometrico puro. Capa 2 ACENTO (drop /
transicion). El frame entero se llena del color elegido y conmuta a negro. El off es
SIEMPRE negro real, para que en Resolume con blend Add el negro desaparezca y solo se
vea el flash. Velocidad capeada a 8 Hz (no llega a la zona epileptogenica 12-15 Hz).
Duty cycle controla si es flash punzante (duty bajo) o bloque sostenido (duty alto).
Edge softness permite pasar de pulso cuadrado duro a sinusoidal suave.

1. `Brightness` (intensidad) — brillo del flash, 0.00–1.50 (def 1.00). Permite overshoot para acento puntual.
2. `Rate` (velocidad) — Hz del estrobo, 0.00–8.00 (def 2.00). **TOPE SEGURO en 8 — no subir.**
3. `Duty` (distorsion) — fraccion ON del ciclo, 0.02–0.98 (def 0.50). Bajo = flash corto; alto = bloque sostenido.
4. `Kleinmix` (color) — solo aplica si FlashColor=Klein: 0=blanco, 1=Klein pleno, 0.00–1.00 (def 1.00).
5. `Beat` (firma) — amplitud de respiracion del brillo con el bombo, 0.00–2.00 (def 0.00).

Extras (no audio-driveables):
- `Flashcolor` (menu Klein/Blanco/Negro, def Klein) — color del flash. Negro = blackout (off es tambien negro, sirve para apagar este layer en la mezcla).
- `Edgesoft` (0.00–1.00, def 0.00) — 0 = pulso cuadrado duro, 1 = bordes sinusoidales suaves.

Audiotarget por defecto: **Beat** con `Audiomult=0.3` (el flash respira con el bombo, sutil).

Huerfano relacionado: `corazones_grid.glsl` — rejilla de corazones blancos sobre Klein
archivada en `visuals_glsl/shaders/`, sin base asignada. Archivado por decision del
plan v2: nada figurativo dibujado con shader (se ve cheap). Los corazones se reservan
para los logos del image_player como assets PNG.

## gradient_flow (base2) — 5 sliders + extras
**Forma:** HERRAMIENTA de gradientes Klein full-frame. Capa 1 LOOK BASE (corre largo,
se modula). Seis ramptypes para mutar en vivo via menu: linear (eje 30deg), horizontal,
vertical, diagonal (45deg), circular (concentricos desde el centro) y radial (slices
angulares desde el centro). Period repite N bandas; Speed las desplaza (signed); Phase
es offset manual; Softness pasa de banding posterizado (bandas duras Klein/negro) a
degradado sinusoidal suave.

1. `Period` (intensidad) — repeticiones del gradiente, 1.00–12.00 (def 4.00)
2. `Speed` (velocidad) — desplazamiento de las bandas, signed -3.00–3.00 (def 0.30)
3. `Phase` (distorsion) — offset manual del gradiente, signed -1.00–1.00 (def 0.00). El shader hace fract() asi que envuelve.
4. `Kleinmix` (color) — color de la banda alta: 0 = blanco, 1 = Klein pleno, 0.00–1.00 (def 1.00). Banda baja siempre negro.
5. `Softness` (firma) — 0 = bandas duras posterizadas, 1 = degrade sinusoidal suave, 0.00–1.00 (def 1.00)

Extras (no audio-driveables):
- `Ramptype` (menu Linear/Horizontal/Vertical/Diagonal/Circular/Radial, def Horizontal) — geometria del gradiente.

Audiotarget por defecto: **Softness** con `Audiomult=0.3` (las bandas se ablandan con
el bombo y se reendurecen, respiracion sutil).

Huerfano relacionado: `estrellas_circulo.glsl` — anillo de estrellas blancas archivado
en `visuals_glsl/shaders/`, sin base asignada. Archivado por decision del plan v2:
nada figurativo dibujado con shader. Las estrellas del press kit se reservan para los
assets PNG del image_player.

## espiral_klein (base3) — 5 sliders
**Forma:** espiral logaritmica Klein full-frame, hipnotica y elegante. Capa 1 LOOK BASE.
En coords polares: `phase = (theta * Arms) / TAU + Tightness * log(r)`. El log mantiene
los brazos visualmente uniformes a cualquier radio (self-similar, no se apretan hacia
el centro). Tightness=0 colapsa la espiral a slices radiales puros (sin coil), como
variante. Softness pasa de bandas duras posterizadas a senoide suave. Aspect-corrected.

1. `Arms` (intensidad) — numero de brazos de la espiral, 1.00–8.00 (def 3.00)
2. `Speed` (velocidad) — rotacion de la espiral, signed -3.00–3.00 (def 0.50)
3. `Tightness` (distorsion) — apriete del coil, 0.00–3.00 (def 1.50). En 0 = slices radiales puros.
4. `Kleinmix` (color) — color del brazo alto: 0 = blanco, 1 = Klein pleno, 0.00–1.00 (def 1.00). Brazo bajo siempre negro.
5. `Softness` (firma) — 0 = bandas duras posterizadas, 1 = senoide suave, 0.00–1.00 (def 1.00)

Audiotarget por defecto: **Softness** con `Audiomult=0.3` (los brazos respiran entre
duro y suave con el bombo, sutil).

Huerfano relacionado: `cortina_teatro.glsl` — cortina de teatro Klein archivada en
`visuals_glsl/shaders/`, sin base asignada. Archivado por decision del plan v2: nada
figurativo dibujado con shader (la cortina como objeto representado entra en esa
categoria).

## sweep_wipe (base4) — 5 sliders + extras
**Forma:** banda Klein full-frame que barre la pantalla a lo largo de un eje rotable.
Capa 2 ACENTO (wipe / transicion live). Off-band siempre negro real, asi en Resolume
con blend Add solo se ve la banda en el momento del wipe. La banda se proyecta sobre
un eje a `Angle` grados; su grosor lo da `Width` (1.00 = ocupa todo el ancho del
frame en el momento de cobertura total); su posicion combina `Position` manual
(0=fuera por un lado, 1=fuera por el otro) + `Speed` signed para auto-sweep.
Softness controla edges (0=hard cut snappy, 1=feathered elegante).

1. `Width` (intensidad) — ancho de la banda, 0.05–1.00 (def 0.25). 1.0 cubre todo el frame al pasar.
2. `Speed` (velocidad) — auto-sweep signed, -3.00–3.00 (def 0.00 = manual con Position)
3. `Position` (distorsion) — posicion manual del centro de la banda, 0.00–1.00 (def 0.50). Wrap por fract.
4. `Kleinmix` (color) — color de la banda: 0 = blanco, 1 = Klein pleno, 0.00–1.00 (def 1.00). Off siempre negro.
5. `Softness` (firma) — 0 = bordes duros (wipe snappy), 1 = feathered (transicion elegante), 0.00–1.00 (def 0.00)

Extras (no audio-driveables):
- `Angle` (0.00–360.00, def 0.00) — direccion del barrido en grados. 0 = horizontal (banda vertical barriendo de izq a der), 90 = vertical, 45 = diagonal.

Audiotarget por defecto: **Position** con `Audiomult=0.3` (la banda lurchea sutil con
cada kick — mood drop/transicion).

Huerfano relacionado: `papel_picado.glsl` — tira de banderines de papel picado
archivada en `visuals_glsl/shaders/`, sin base asignada. Archivado por decision del
plan v2: nada figurativo dibujado con shader (los banderines como objeto representado
entran en esa categoria).

## grid_klein (base5) — 5 sliders + extras
**Forma:** cuadricula cartesiana de cuadrados Klein latiendo sobre negro. Cada celda
late con una onda diagonal que recorre el grid muy despacio (esquina a esquina). El grid
completo deriva en un Lissajous chico (sub-pixel a vista, no sale del frame). Lineas
guia blancas tenues opcionales (off por default = mas espacio negativo). Hermano visual
de `corazones_grid`: misma logica de rejilla + onda, motivo distinto (cuadrado vs corazon).

1. `Cellsize` (intensidad) — tamano base del cuadrado Klein dentro de la celda, 0.0–1.0
2. `Speed` (velocidad) — velocidad de la onda y de la deriva, 0.0–3.0
3. `Drift` (distorsion) — amplitud de la deriva espacial del grid, 0.0 = grid estatico, 1.0 = max
4. `Kleinmix` (color) — 0 = celdas blancas (B/N), 1 = Klein pleno, 0.0–1.0
5. `Beat` (firma) — amplitud del latido con la onda+bombo, 0.0–2.0

Extras (no audio-driveables):
- `Cols` (3–10, def 6) — columnas del grid
- `Rows` (2–7, def 4) — filas del grid
- `Linealpha` (0.0–1.0, def 0.0) — visibilidad de las lineas guia blancas

Audiotarget por defecto: **Beat** con `Audiomult=0.3` (las celdas respiran con el bombo, sutil).

Huerfano relacionado: `disco_radial.glsl` (antiguo grid_klein) — rejilla radial archivada en
`visuals_glsl/shaders/`, sin base asignada. Si lo quieres usar, dime cual base y genero el setup.

Huerfano relacionado: `lazo.glsl` — mono / lazo de XV anos archivado en `visuals_glsl/shaders/`,
sin base asignada. Al usuario no le funciono (queria algo mas solido / motion graphics).
Si quieres iterarlo o reusarlo, dime cual base y genero el setup.

## bandera_klein (base6) — 5 sliders + extras
**Forma:** bandera / signage motion-graphics — un bloque Klein solido cubre casi todo
el frame (Coverage controla cuanto), y N barras negras deslizandose lentamente lo cruzan
horizontalmente. Las barras son del mismo grosor aunque el bloque respire/encoja. Se
pueden rotar (`Angle`) para barras verticales o diagonales. Mood Saul Bass / mid-century
title sequence: solid, bold, sin glitch, max impacto. Centerpiece unico (hermano de
`cortina_teatro`). Reemplaza el `estrellas_circulo` duplicado del plan en base6.

1. `Coverage` (intensidad) — fraccion del frame que ocupa el bloque Klein, 0.30–1.00
2. `Speed` (velocidad) — velocidad de las barras (signed: + sube, - baja), -3.0 a 3.0
3. `Barwidth` (distorsion) — ancho de cada barra negra, 0.00 = sin barras, 0.30 = bandas gordas
4. `Kleinmix` (color) — 0 = bloque blanco con barras negras (B/N), 1 = bloque Klein pleno
5. `Pulse` (firma) — amplitud del latido sutil del bloque (ciclo ~15s, decoupled de Speed), 0.00–1.50

Extras (no audio-driveables):
- `Barcount` (1–5, def 2) — numero de barras
- `Angle` (0–180, def 0) — orientacion: 0 = barras horizontales, 90 = verticales

Audiotarget por defecto: **Pulse** con `Audiomult=0.3` (la bandera respira con el bombo, sutil).

Huerfano relacionado: `corazon_punteado.glsl` — single corazon punteado archivado en
`visuals_glsl/shaders/`, sin base asignada. Los corazones se reservan para los logos del
image_player; el usuario no quiere corazones en visuales generativos.

Huerfano relacionado: `emblema_solar.glsl` — sol sonidero archivado en `visuals_glsl/shaders/`,
sin base asignada. Al usuario no le funciono (centerpiece chico sobre negro no leia).

## PATRON OBSERVADO (importante para futuras propuestas)
ESCUBY funciona con visuales que LLENAN el frame (papel_picado, cortina_teatro,
grid_klein, bandera_klein, corazones_grid, checker_opart) y NO funciona con motivos
chicos centrados sobre sea de negro (lazo, emblema_solar). Default desde aqui: proponer
formas full-frame o que cubran al menos ~80% del area. Sea de negro = no lee desde la pista.

## checker_opart (base7) — 5 sliders + extras
**Forma:** damero op-art gigante full-frame — cells grandes cuadradas alternando Klein
y negro (o blanco/negro segun Kleinmix). Slow rotacion del damero entero, warp opcional
que bend el grid con sin waves, y pulse sutil del breathing (cycle ~15s, decoupled del
Speed). Estilo Bridget Riley 60s / op-art / XV anos retro. Llena el frame al 100%, max
contraste, reads desde 30m. Reemplaza el `corazon_punteado` del plan en base7.

1. `Cellscale` (intensidad) — cells por lado vertical, 2.00–12.00 (def 4 = cells GRANDES, chunky)
2. `Speed` (velocidad) — velocidad de rotacion del damero (signed), -2.00 a 2.00
3. `Warp` (distorsion) — bend del grid con sin waves, 0.00 = damero recto, 1.00 = wave fuerte op-art
4. `Kleinmix` (color) — 0 = blanco/negro classic op-art (max contraste), 1 = Klein/negro, 0.00–1.00
5. `Pulse` (firma) — amplitud del breathing del grid (sutil), 0.00–2.00

Extras (no audio-driveables):
- `Invert` (0/1, def 0) — voltea la paridad del checker (intercambia color A y B)

Audiotarget por defecto: **Pulse** con `Audiomult=0.3` (el damero respira con el bombo, sutil).

## lineas_flujo (base8) — 5 sliders
**Forma:** lineas paralelas Klein full-frame que se curvan como una topografica
(curvas de nivel). Capa 1 LOOK BASE. Base: lineas horizontales equiespaciadas
(`Density`). Cada linea se desplaza verticalmente por una suma de senos multi-octava
en x (+ una modulacion ligera en y para romper la rigidez 1D), dando flow organico
sin pagar el costo de noise procedural. `Curvature` escala la amplitud del
desplazamiento: en 0 son rectas paralelas planas, en 1+ flow topografico marcado.
`Speed` signed mueve el flow. `Thickness` es el grosor de la linea en unidades del
espaciado (0.5 maximo = lineas tocandose). AA correcto a cualquier density via
`fwidth()`. Fondo negro real.

1. `Density` (intensidad) — numero de lineas en pantalla, 4.00–40.00 (def 14.00)
2. `Speed` (velocidad) — desplazamiento del flow, signed -3.00–3.00 (def 0.50)
3. `Curvature` (distorsion) — amplitud del curveo, 0.00–2.00 (def 0.70). En 0 = rectas planas.
4. `Kleinmix` (color) — color de la linea: 0 = blanco, 1 = Klein pleno, 0.00–1.00 (def 1.00). Fondo siempre negro.
5. `Thickness` (firma) — grosor de la linea, 0.01–0.50 (def 0.06). 0.5 = lineas casi tocandose.

Audiotarget por defecto: **Curvature** con `Audiomult=0.3` (las lineas se ondulan
mas con cada kick, sutil — el flujo "respira" topograficamente).

Huerfano relacionado: `klein_zones.glsl` — 4 quadrants Mondrian-style (TL=Klein,
TR=blanco, BL=negro, BR=wildcard) con dividers oscilando, archivado en
`visuals_glsl/shaders/`, sin base asignada. NO es figurativo (es abstracto/geometrico
y funcionaba); se archiva porque el plan v2 reasigno la slot base8 a `lineas_flujo`.
Si se quiere recuperar, se le puede asignar una base disponible (base10-16).

## gradient_klein (base9) — 5 sliders + extras
**Forma:** gradiente VERDADERO full-frame entre dos colores de la paleta Klein/blanco/
negro — un solo wash continuo, **sin bandas / sin `fract()`** (esto es lo que el
usuario llama gradiente, distinto de base2 `gradient_flow` que es rampa con repeticiones
y queda pendiente de revisar). Capa 1 LOOK BASE. El gradiente se proyecta sobre una
direccion (menu de 6 ejes: horizontal, vertical, dos diagonales, radial out, radial
in). `Width` controla el ancho de la zona de transicion (0 = step duro binario; 1 =
wash que abarca todo el frame, el caso "gradiente puro"). `Position` centra la
transicion en el frame; `Speed` signed la deriva lento. `Bias` aplica una curva gamma
(0.3 = bright crece rapido, 1 = lineal, 3 = bright crece tarde).

1. `Width` (intensidad) — ancho de la zona de transicion, 0.00–1.00 (def 1.00 = gradiente full-screen). En 0 = step duro binario.
2. `Speed` (velocidad) — deriva signed del midpoint, -3.00–3.00 (def 0.00 = estatico)
3. `Position` (distorsion) — posicion del midpoint, 0.00–1.00 (def 0.50 = centrado)
4. `Kleinmix` (color) — tinte del endpoint "bright" entre blanco y Klein: 0 = blanco, 1 = Klein pleno (def 1.00). Solo aplica en modos klein/*.
5. `Bias` (firma) — curva gamma del gradiente, 0.30–3.00 (def 1.00 = lineal). <1 = bright crece rapido; >1 = bright crece tarde.

Extras (no audio-driveables):
- `Direction` (menu) — eje del gradiente. Opciones: `Horizontal`, `Vertical`, `Diagonal +45`, `Diagonal -45`, `Radial out (centro -> esquinas)`, `Radial in (esquinas -> centro)`. Def Horizontal.
- `Mode` (menu) — pareja de color. Opciones: `Klein / Negro` (def), `Blanco / Negro` (Kleinmix ignorado), `Klein / Blanco`.
- `Invert` (toggle) — intercambia los endpoints A y B del par.

Audiotarget por defecto: **Position** con `Audiomult=0.3` (el midpoint deriva sutil
con cada kick, el wash respira sin saltar).

Nota: base2 `gradient_flow` (rampa con bandas y posterizado) sigue ocupando su slot.
Pendiente revisar: el usuario quiere distinguir "rampa" de "gradiente" formalmente —
ver `feedback_escuby_gradient_vs_ramp` en memoria.

## logo_fx (base18) — 5 sliders + extras (suite de efectos para logos)
**Forma:** efecto rig universal para CUALQUIER asset (logos PNG con alpha, movies,
generadores TOP, composites, etc.). Cumple las reglas clave de `reglas_efectos_assets.txt`
EXCEPTO el Transform TOP, que se hace manual (decision del usuario).

**Cadena minima:** `asset_in (Null)` → `glsl_fx (GLSL)` → `switch1 (Bypass)` → `null1` → `out1`.
Si quieres mover/escalar/rotar el logo, pon TU Transform TOP entre tu fuente y `asset_in`
(el builder NO lo crea por default).

**Alpha sagrado:** el shader preserva alpha siempre. Background transparente por
default → el logo se puede componer encima de un visual generativo y se ve el
fondo a traves de las zonas transparentes. `Bgklein=1` rellena el fondo con Klein
opaco si se quiere.

### 5 sliders en orden de rol (cada uno = 1 efecto, 0 = off)
1. `Glow` (intensidad) — halo blanco dilatado alrededor del borde REAL del logo, 0–1
2. `Strobespeed` (velocidad) — strobo blanco/negro en Hz (respeta alpha), 0–30
3. `Echo` (distorsion) — copia Klein de la silueta offset orbitando lento (~21s/vuelta), 0–1. Mood ghost / screen-print Warhol. Visualmente fuerte pero NO es un flash. El bass acentua sutilmente.
4. `Kleinmix` (color) — tinte Klein por luma (negro→Klein→blanco), 0–1
5. `Pulse` (firma) — pulse de escala con bass desde el centro del canvas (asume Transform centrado), 0–2

### Extras (no slots, no audio-driveables)
- `Opacity` (0–1, def 1.0) — **master fade** suave, distinto del Bypass (corte duro). Mood Escuby = transiciones elegantes.
- `Invert` (0/1, def 0) — invertir colores durante el strobo
- `Bgklein` (0/1, def 0) — 0 = bg transparente (alpha preservado para componer), 1 = bg Klein opaco

Defaults: todos los sliders en 0 → asset pasa limpio.

Audiotarget por defecto: **Pulse** con `Audiomult=0.3` (el logo respira con el bombo).

### Composicion final (orden de stacking dentro del shader)
`bg → echo (sombra Klein orbitando) → glow (halo blanco) → logo (encima)`. El strobo y
el klein-tint se aplican al color del logo antes de stackear. El pulse y el echo
muestrean el input via UV displacement.

### Como usar en TD
1. Cargar `setup_base18_logo_fx.py` en un Text DAT dentro de `/project2/base18` -> Run.
2. Crear (o pegar) tu fuente dentro de base18: Movie File In TOP con tu PNG/logo, Composite, etc.
3. (Opcional) Si quieres ajustar pos/escala/rot, anade TU Transform TOP entre tu fuente y `asset_in`.
4. Cablear tu fuente (o el Transform) al `asset_in` (drag connection).
5. Dial in efectos. `Opacity` para fade suave; `Bypass` para corte duro (passthrough del asset crudo).
6. Para verificar alpha: pon el `null1` encima de un visual generativo en un Composite TOP — debe verse el fondo a traves de las zonas transparentes del logo.

## Como correr un builder
Cargar el `setup_baseXX_<name>.py` en un Text DAT dentro de `/project2/baseXX` -> Run.
(O `exec(open('<ruta>').read())` desde el Textport.)

## Notas del show (libre — el skill no borra esto)
- 
