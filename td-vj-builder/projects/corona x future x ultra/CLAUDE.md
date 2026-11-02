# CORONA x FUTURE x ULTRA — Visuales en tiempo real (Future Festival + Ultra 2026)

Contexto de trabajo del show para la skill `td-vj-builder`. Esta carpeta = `project.folder` (guarda aquí el `.toe`).
Última actualización: 2026-10-23

**Alcance:** dos festivales: **Ultra CDMX** (7–8 nov 2026) y **Future Festival Monterrey** (13–14 nov 2026) — fechas confirmadas por el usuario 2026-10-19.
Cotización (2026-10-19, `exports/cotizacion/`): paquete $150,000 + IVA · solo Future MTY $100,000 · solo Ultra CDMX $90,000 (+ IVA).
Pago al término del evento. Viáticos fuera (Monterrey). Generador en `exports/cotizacion/_generador/`.
Estudio: El Taller de Piyamas. Brief completo: `research/PROJECT_CONTEXT_FUTURE_ULTRA.md`.
- **Pantalla central** → VISUALES generativos audio-reactivos (base1–18; base17–18 desde 2026-10-23). Se construyen de menos a más, por partes.
- **Pantallas laterales** → assets de marca (image player / video) procesados con efectos en los bases de
  filtros (base19–24, luego base38–45). Pendiente: assets del cliente.
- Truss / asteras (mapping): no confirmado. Layouts CCTV: no aplican.

Gustos del usuario: NO caleidoscopios, NO "Joy Division" (líneas apiladas), NO metal líquido, NO láser en abanico (base2 fuera 2026-10-18).
Referencias 2026-10-18 (media/SnapInsta*.mp4): torres de andamio con paneles/tiles de luz sueltos (cuadros, rombos)
que se encienden como unidades, mucho negro, humo; secuencias que suben; vista cenital con cuadro de luz por módulo. Sí: precisión, arquitectura, luz.
Dirección: techno industrial + Future/Ultra leído como instalación tipo MUTEK (precisión, luz, negro profundo), geometría abstracta, interferencia, distorsión, texturas metálicas, feedback, alto contraste.

## Estructura

```
01. EDITABLES/
├── <show>.toe                   ← (por guardar aquí)
├── CLAUDE.md                    ← este archivo
├── _lib/tdvj_core.py            ← núcleo compartido (contrato de parámetros, audio, resolución, grafo, uniforms)
├── _lib/booth_geo.py            ← geometría aproximada del booth (Python puro, desde el PDF de SPECTA)
├── _templates/                  ← setup_baseXX_visual.py + visual.frag de ejemplo
├── shaders/visuales/            ← .glsl de la pantalla central (Text DAT con Sync to File)
├── shaders/efectos/             ← .glsl de los filtros de marca
├── shaders/_descartados/
├── builders/build_all.py        ← corre todos los builders (visuales y luego efectos)
├── builders/visuales/           ← setup_baseXX_<nombre>.py (base1–18)
├── builders/efectos/            ← setup_baseXX_<nombre>.py (base19–24, 38–45)
├── builders/herramientas/       ← limpiar_bases.py · aplicar_paleta.py · aplicar_resolucion.py · setup_salidas.py · setup_previz.py
├── builders/_descartados/
├── research/                    ← brief del proyecto
├── media/                       ← CORONA_ULTRA_rev.pdf (plano SPECTA) + 2 renders del booth (WhatsApp .mp4)
├── media/marca/                 ← assets del cliente (PNG transparentes ~2048px / video)
└── exports/previews/            ← PNG de cada look (render fuera de TD, 4 niveles de audio)
```

## Cómo correr un builder

1. En TD, crea un Text DAT (en `/project2` o dentro del base) → `File` = `builders/visuales/setup_baseXX_<nombre>.py`.
2. Clic derecho → **Run Script**. Textport: `[tdvj]` = ok, `[WARN]` = revisar.
3. Editar el shader en un editor externo recarga solo (Sync to File). Re-ejecutar el builder es seguro:
   conserva valores y mapeos MIDI de los sliders y rehace solo los nodos con tag `tdvj`.
4. Todo de una vez: `builders/build_all.py`.

## Rig (no negociable)

- Visuales en base1–18 (página `Visual`) · Efectos base19–24 y base38–45 (página `Filter`). Nunca renombrar/mover/destruir un baseX.
- **Limpieza (2026-10-23):** `builders/herramientas/limpiar_bases.py` (una vez, antes de build_all) quita páginas y nodos de
  shows anteriores; los nodos viejos van a `/project2/_respaldo/baseN` (no se borran). Tag `mio` = nodo propio que no se toca.
- 5 sliders en orden de rol: **1 intensidad · 2 velocidad · 3 distorsión · 4 color · 5 firma**. `Bypass` aparte (visual → negro; efecto → fuente sin procesar).
- **Audio en TODAS las bases** (página `Audio`): Audioreact (on) · Low/Mid/High (suman) · Audiotarget (a cuál de los 5 empuja) ·
  Audiomult 0–3 · Smooth (s, Lag CHOP) · Audio CHOP (default `/project1/null4`, se puede arrastrar otro) · Energy (lectura).
  Grafo: `audio_in` (Select CHOP, `low mid high`) → `audio_smooth` (Lag). El shader recibe la energía ya sumada en
  `u_bass` (visuales) / `uEnergy` (efectos); además empuja el slider elegido en Audiotarget (en la expresión, no en el slider → MIDI intacto).
  `audio_in` también selecciona `kick` (Audio Analysis). Uniforms opcionales: si el shader declara `u_low`/`u_mid`/`u_high`
  (bandas sueltas) o `u_kick` (kick crudo) se enlazan solos. `extra=tdvj_core.kick_step` → página Secuencia + `u_step`.
  `resolution=(w, h)` en el CONFIG = default de Salida al crear la base.
- **Resolución por base** (página `Salida`: Resw/Resh, default 1920x1080 provisional). El aspecto se calcula en el shader:
  nada se deforma al cambiarla. Para todas a la vez: `builders/herramientas/aplicar_resolucion.py`.
- Paleta Corona (2026-10-15): Color1 blanco · Color2 **amarillo Corona (1.0, 0.78, 0.17) ≈ #FFC72C** (acento) · Color3 negro.
  Bases ya construidas: `builders/herramientas/aplicar_paleta.py` (los builders solo ponen color al crear el parámetro).
- **Paleta del cliente (2026-10-23): 70% azul · 20% amarillo · 10% blanco — en TODAS las bases (1–18).**
  **Color4 = azul rey (0.0, 0.25, 0.9)** (provisional, ajustar al Pantone del cliente). Cada elemento (celda, tile, línea,
  nivel, punto, bloque, estela) elige color con `pick(h)`: `White` (extra, 0.1) → blanco · `Accent` (slot 4 color, 0.2)
  → amarillo · resto → azul. Shaders por columna (ring_chase, scanner) usan `colRank` = reparto fijo por columna.
  Bases ya construidas: `build_all.py` y luego `aplicar_paleta.py` (pone colores + Accent 0.2 / White 0.1).

## El booth (de media/: plano SPECTA + renders)

Marca **Corona** (corona, botella; dorado/amarillo + azul rey). Booth de andamio 4.14 x 4.13 m, esquinas ochavadas,
pasillo 2.07 m, alto 4.46 m. Superficies LED:
- **Columnas**: 8 paneles verticales en las caras ochavadas de las 4 torres (~0.74 x 2.45 m c/u).
- ~~Alas~~: quitadas del previz (2026-10-15). El plano no muestra LED arriba de las torres; el ISO sugiere paneles
  inclinados DENTRO de las esquinas del techo. Confirmar con producción / OBJ (`booth_geo.alas()` sigue ahí, sin usar).
- **Techo**: centro (corona) + 4 brazos escalonados (2.58 / 3.09 / 3.56 / 4.05 m); visto desde abajo. Barras de pixeles alrededor del centro.

## Previz 3D

`builders/herramientas/setup_previz.py` → `/project2/previz` (out1). Geometría de `_lib/booth_geo.py` (aproximada,
reemplazar por OBJ/FBX cuando llegue: necesita las pantallas como objetos separados con nombre + UVs + metros).
Página Previz: Brillo · Vista (libre/frente/iso/interior/techo/**usuario**) + órbita libre · Lente.
**Usuario** (default): persona en el pasillo — X/Z (posición), altura de ojos, voltear arriba (tilt), girar, giro auto, lente (90°).
El mapeo final se hace en **Resolume** (TD → Syphon → Advanced Output slices); el previz es para diseñar. Techo = proyección cenital 1:1.
Canvas sugeridos: columnas repartido ≈ 2.4:1 · techo 1:1.
Solo cocina mientras se mira su salida.

## Bases ocupadas

| Base | Nombre | Shader | Estado |
|---|---|---|---|
| base1 | Rejilla industrial | `shaders/visuales/industrial_grid.glsl` | Repetido. Rejilla de acero + moiré; audio → celdas, cortes. Firma: Cells |
| base2 | Constelación de tiles | `shaders/visuales/tile_constellation.glsl` | 2026-10-18 (reemplaza laser_fan). Repartido + techo propio. Tiles cuadro/rombo sueltos con humo, kick = grupo. Firma: Rows |
| base3 | Datamatics | `shaders/visuales/datamatics.glsl` | 2026-10-18 (reemplaza step_sequencer). Repartido + techo propio, página Secuencia. Estilo datos/Ikeda: números 3x5, barcode, líneas 1px, gráfica; modo por columna cambia con el kick; estrobo binario. Techo: retícula de medición. Firma: Density |
| base4 | Escalones | `shaders/visuales/tier_pulse.glsl` | 2026-10-18 + versión columnas. Repartido + techo propio. Techo: anillos en los escalones (graves ext., medios, agudos int., kick centro) · Columnas: 3 bandas por columna. Firma: Lines |
| base5 | Torre que sube | `shaders/visuales/tower_climb.glsl` | 2026-10-18 (reemplaza scaffold_echo). Repartido + techo propio. Niveles que suben con estela, Skew = espiral, drop = todo; techo: anillos hacia el centro. Firma: Levels |
| base6 | Persecución circular | `shaders/visuales/ring_chase.glsl` | Repartido. Pulsos que dan la vuelta al booth. Usuario: "no se veía continuo" — revisar en TD (Snap=1 prende columnas enteras). Firma: Count |
| base7 | Escáner | `shaders/visuales/scanner.glsl` | Repartido. FAVORITO del usuario. Líneas que suben/bajan por columna + marcas. Firma: Phase |
| base8 | Matriz de puntos | `shaders/visuales/dot_matrix.glsl` | Repartido. EN DUDA (cliente). Puntos LED, Mode 0 = auto. Firma: Pitch |
| base9 | Código de datos | `shaders/visuales/data_barcode.glsl` | Repartido. EN DUDA (cliente). Bandas de código de barras. Firma: Rows |
| base10 | Radar | `shaders/visuales/radar_sweep.glsl` | 2026-10-18 + versión columnas. Repartido + techo propio. EN DUDA (cliente). Columnas se encienden al pasar el barrido por su azimut (sincronizado con el techo); Reverse si gira al revés. Firma: Segments |
| base11 | Bloques de golpe | `shaders/visuales/kick_blocks.glsl` | Repartido, página Secuencia. Patrón de bloques por kick, para drops. Firma: Density |
| base12 | Módulos | `shaders/visuales/module_grid.glsl` | 2026-10-18. Repartido + techo propio. Columnas: cuadro de luz por módulo + humo + diagonal (ref. cenital) — al usuario le jala. Techo (rehecho): el techo entero = UN módulo gigante, cuadro = panel central. Firma: Rows |
| base13 | Lluvia de código | `shaders/visuales/code_rain.glsl` | 2026-10-23, ref. cliente pinterest1+2 (misma idea, solo cambiaba color). Repartido + techo propio (lluvia hacia la corona). Glifos 5x7 que caen y mutan, 3 capas de profundidad. Firma: Columns |
| base14 | Matriz de anillos | `shaders/visuales/ring_matrix.glsl` | 2026-10-23, ref. pinterest3. Repartido + techo propio. Puntos LED: racimos de anillos que cambian a saltos. Firma: Pitch |
| base15 | Muro de placas | `shaders/visuales/shingle_wall.glsl` | 2026-10-23, ref. pinterest4. v2: la v1 (placas chiquitas) se veía aplastada/ilegible → placas GRANDES (Plates 7 por alto, Across 2 por tira) que prenden como unidad. Techo = muro cuadrado. Firma: Shine |
| base16 | Estallido | `shaders/visuales/warp_burst.glsl` | 2026-10-23, ref. pinterest5. Repartido (un estallido por tira). Techo rehecho (`burstTecho`): carriles rectos por brazo que saltan de escalón en escalón + onda cuadrada desde la corona. Firma: Count |
| base17 | Túnel de rejilla | `shaders/visuales/grid_tunnel.glsl` | 2026-10-23, ref. pinterest6 (antes en base18; base17 ya no es host de cámaras). Repartido (túnel por tira). Techo rehecho (`tunnelTecho`): sin perspectiva, anillos a paso constante que salen de la corona y suben por los escalones. Firma: Cells |
| base18 | Malla de puntos | `shaders/visuales/dot_wave.glsl` | 2026-10-23, ref. pinterest7 (antes en base19). Repartido, techo recorta. Hilos de puntos que ondulan; color por altura. Primera pasada (pliegues débiles). Firma: Lines |

Bases 13–18: registro de las refs. del cliente para ir descartando. Previews en `exports/previews/<shader>.png`.

## Salidas a Resolume (regla vigente 2026-10-18)

**Una base alimenta columnas Y techo a la vez** (se acabaron superficie/pareja). `builders/herramientas/setup_salidas.py`
→ `/project2/salidas`. Página Salidas: **Visual** (una base = todo el booth) · Separar/Columnas/Techo · **Marca** (18+, 0 = apagada) · Enviar.
- **TD_columnas** (Formato Colw/Colh 1920x800, Panels 8): SIEMPRE 8 tiras de 240x800 lado a lado. TD acomoda la base con
  `shaders/herramientas/layout_columnas.frag` según su **Salida → Colmap** (lo fija el builder, no se opera):
  *repartido* = un canvas alrededor del booth · *repetido* = el centro del canvas en cada columna. Recorta, no deforma.
- **TD_techo** (Techow/Techoh 1080x1080): si la base tiene **versión de techo** (`techo=True` en el builder → GLSL `glsl_techo`
  con el mismo shader y `u_surface = 1`, Salida → Techores, sale por `out_techo`) usa esa; si no, recorta out1 a 1:1.
  Shaders con dos versiones: `uniform float u_surface;` (0 columnas · 1 techo).
- **Forma REAL del LED del techo** (`booth_geo.techo()`, canvas 1:1 = planta 4.14 m): NO es un cuadro lleno. Es la corona
  (cuadro central, d < 0.058, lo MÁS BAJO a 2.58 m) + 3 escalones de barras en 4 brazos que SUBEN hacia afuera:
  d ≈ 0.087–0.179 · 0.184–0.275 · 0.292–0.384 (d = max(|x|,|y|) desde el centro); esquinas y d > 0.384 = nada.
  Diseñar el techo en ese espacio (anillos cuadrados, carriles por brazo). Radiales finos o perspectiva con fuga
  al centro se ven raros (base16/17 v1). Revisar previews con la máscara de esa forma.
- **REGLA (usuario, 2026-10-23): techo = SIEMPRE un solo visual extendido en todo el canvas** (nunca por columna ni recorte
  de tiras). Columnas = visual por columna salvo que el usuario diga otra cosa. Hoy TODAS las bases (1–18) tienen
  `techo=True`: las continuas (1, 8, 9, 18) usan el mismo shader a 1:1; las demás tienen rama `u_surface = 1` propia
  (6 pulsos girando alrededor del centro · 7 cuadros concéntricos · 11 retícula cuadrada · 15 un solo muro, etc.).
- 2026-10-23: `VISUAL_BASES` = 1–18 (`_lib/tdvj_core.py`; base17 ya no aloja escena_modular, sin cámaras en este show);
  `EFFECT_BASES` = 19–24, 38–45 → marca desde base19. Salidas → Visual acepta 1–45.
- Tipos de display (a definir con el usuario): secuencia continua · canvas completo (repartido) · canvas repetido por panel.
- **TD_marca**: igual que columnas, con alfa, acomodo según el Colmap de la base de marca; capa encima en Resolume.
- **Resolume**: 8 slices FIJOS de 1/8 de TD_columnas, en este orden (visto desde arriba, empezando al frente-derecha y
  girando hacia el fondo): 1-2 torre frente-derecha (cara frente, cara lado) · 3-4 fondo-derecha · 5-6 fondo-izquierda ·
  7-8 frente-izquierda. Mismo orden que `booth_geo.columnas()`. TD_techo → paneles del techo por su región en planta.
- Regla en `_lib/tdvj_route.py`. `salidas/vista_columnas` = marca encima de columnas. Solo cocinan las bases al aire.
- 2026-10-23: el techo salía con out1 (canvas de columnas recortado = "visual repetido") porque la elección
  out_techo/out1 era una expresión cacheada. Ahora `src_*` de salidas se re-evalúa cada cuadro (`absTime.frame`)
  y `tdvj_core.refresh_salidas()` corre al final de cada builder. Chequeo: `op('/project2/salidas/src_techo').par.top.eval()`
  debe terminar en `/out_techo`.
- **Previz** muestra solo lo que sale de salidas (vista_columnas → 8 columnas, fit_techo → techo). La base se elige en salidas.
- `build_all.py` corre bases → salidas → previz.

## Pendientes

- Pixel map / aspecto real de pantallas (central y laterales) → ajustar Resw/Resh.
- Assets de marca → `media/marca/` → primer filtro en base19 (image player como fuente).
- Confirmar en TD que `/project1/null4` existe en este `.toe` (si no, arrastrar el CHOP de análisis a Audio → Audio CHOP).

## Notas del show

<!-- Tuyo: venue, resolución real, ruta de audio, lo que funcionó en ensayo. La skill no borra esta sección. -->
