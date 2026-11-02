# ON TOUR x MERCADO LIBRE — Piso LED interactivo (Hokuyo)

Contexto de trabajo del show para la skill `td-vj-builder`. `.toe`: `HOKUYO MERCADO LIBRE.toe` (esta carpeta = `project.folder`).
Última actualización: 2026-10-08

**Alcance:** solo VISUALES generativos (base1–16) para un piso LED de 7 x 5 m con tracking Hokuyo.
Sin efectos de cámara ni layouts CCTV. La webcam se usa únicamente para probar los visuales.

## Estructura

```
02. EDITABLES/
├── HOKUYO MERCADO LIBRE.toe
├── CLAUDE.md                    ← este archivo
├── HANDOFF_EXPLICADO.md         ← cómo funciona el handoff a Mich + checklist de pruebas + preguntas
├── _lib/tdvj_core.py            ← núcleo compartido (contrato de parámetros, grafo, binding de uniforms)
├── _lib/scripts/                ← scripts de Script CHOP (tracker de blobs)
├── _templates/                  ← visual.frag + setup_baseXX_visual.py de ejemplo
├── shaders/visuales/            ← .frag/.glsl del show (Text DAT con Sync to File)
├── shaders/herramientas/        ← shaders de herramientas (demo_composite.frag)
├── builders/build_all.py        ← corre todos los builders + demo tools
├── builders/visuales/           ← setup_baseXX_<nombre>.py del show
├── builders/herramientas/       ← setup_tracking_input.py (hub) · setup_demo_tools.py · handoff.py
├── builders/_legacy/            ← builders viejos, ya reemplazados (no usar)
├── research/                    ← video de referencia del cliente + frames/ (hoja de contactos)
├── media/images/                ← PNG transparentes (~2048px) para image players
└── exports/                     ← renders · previews/ (PNG de cada look) · handoff/ (.tox + LEEME_MICH.md)
```

## Cómo correr un builder

**Todo de una vez:** `builders/build_all.py` corre todos los `builders/visuales/setup_base*.py` y al final `setup_demo_tools.py`.

1. En TD, crea un Text DAT (en `/project2` o dentro del base) → `File` = `builders/visuales/setup_baseXX_<nombre>.py`.
2. Clic derecho → **Run Script**. Mira el Textport: `[tdvj]` = ok, `[WARN]` = revisar.
3. Editar el shader en un editor externo recarga solo (Sync to File). Re-ejecutar el builder es seguro:
   conserva valores y mapeos MIDI de los sliders y rehace solo los nodos con tag `tdvj`.

## Tracking → demo → handoff

**Hub de tracking** `/project2/tracking_input` (`builders/herramientas/setup_tracking_input.py`):
una sola entrada para todas las bases. Source = **Simulate** / **Webcam** (webcam_tracker) / **Externo** (Hokuyo).
Convierte formatos (contrato `p{i}x…` o canales X/Y por sample), metros→0..1, origen, swap/flip, clip.
Todas las bases leen `me.parent().op('tracking_input/out1')` (relativo → sirve igual dentro del pack).
**Externo TOP (blobs)** (2026-10-08, pedido de Mich: su lista de samples en CHOP crecía sin limpiarse):
Mich manda un TOP con un blob blanco por persona → `blob_src` → `blob_small` (Analysisw px, aspecto del piso)
→ el Script CHOP del hub umbraliza, busca componentes y asigna ID estable (página **Seguimiento**); `blob_view` = debug.
Lógica en `_lib/scripts/tracking_hub_callbacks.py` (`_from_top`), vista en `hub_blob_view_callbacks.py`.
Formato samples (CHOP) con **Retrack** (default on): ignora orden de filas e IDs del CHOP y re-sigue con el
mismo tracker (`_retrack`). Causa del bug de Mich (videos 2026-10-08): su tabla `touches` (x y id a) reordena
filas, deja filas viejas con ID repetido y regenera IDs (124→136 en 10 s) → slot = fila saltaba entre personas.
Simulate de cada base = local, apagado por defecto. Contrato: `p{i}x p{i}y` 0..1 · `p{i}a` · `p{i}id`, i = 0..7.

1. `builders/build_all.py` → hub + todas las bases + demo tools.
2. Webcam: `setup_demo_tools` crea `webcam_test`, `webcam_tracker` (Capture BG, Threshold, Min Area, Dilate;
   su viewer es la vista de debug) y `demo_render`. En el hub: Source = Webcam.
3. `demo_render`: **Visual (base)** (menú; **Refresh bases** tras construir una nueva) · Mode = Solo visual /
   Overlay con webcam / Lado a lado · **Record** → `exports/<base>_demo.mov`.
   Flujo: demo_render para ver/grabar; cada base solo para sus propios parámetros.
4. `builders/herramientas/handoff.py` → `exports/handoff/`: **ML_floor_pack.tox** (hub + bases + menú Visual,
   plug & play), `tracking_input.tox` y cada base suelta. Todo congelado. Guía: `exports/handoff/LEEME_MICH.md`.

`source='webcam'` en el CONFIG de un visual mete además la imagen de la webcam en `sTD2DInputs[0]`
(para visuales que usen `u_input`). Todo visual interactivo usa `tracking=True` (lógica en
`tdvj_core.build_tracking`); los shaders trabajan en metros con aspecto de pantalla (`aspectM()`).

## Rig (no negociable)

- Visuales en base1–16, página `Visual`. Nunca renombrar/mover/destruir un baseX.
- 5 sliders en orden de rol: **1 intensidad · 2 velocidad · 3 distorsión · 4 color · 5 firma**. `Bypass` aparte (→ negro).
- **Sin audio en este proyecto:** los builders usan `audio=False` (sin `audio_in` ni página Audio; `u_bass` = 0).
  El core lo soporta (`audio=True` → página Audio con fuente `/project1/null4`) por si se necesita después.
- **Resolución y piso: en el hub** (`tracking_input` → página **Salida**: Piso ancho/alto (m), Resolución W/H (px)).
  Todas las bases usan `resolution='hub'` y leen de ahí (`tdvj_core.hub_expr`). Ahora 1920x1080 provisional;
  poner la res nativa del LED (7x5 m ≈ 1.4:1) → las formas no se deforman (los shaders calculan el aspecto).

## Bases ocupadas

| Base | Nombre | Shader | Estado |
|---|---|---|---|
| base1 | FloorPresence | `shaders/visuales/floor_presence.glsl` | probado en TD. Auras metaball + ondas + capa de calibración. Paleta ML desde 2026-09-24 (cada persona amarilla o azul; el builder migra los colores viejos) |
| base2 | Red de envíos | `shaders/visuales/envios_network.glsl` | compila, sin probar en TD. Nodos + rutas en L con paquetes (marca ML) |
| base3 | HUD de detección | `shaders/visuales/hud_detection.glsl` | compila, sin probar en TD. Cajas + etiqueta código de barras, guías CAD, medición, radar (marca ML) |
| base4 | Flujo | `shaders/visuales/flow_field.glsl` | compila, sin probar en TD. Líneas de flujo que rodean a cada persona (flujo potencial) + paquetes (marca ML) |
| base5 | Bauhaus ML | `shaders/visuales/bauhaus_ml.glsl` | compila, sin probar en TD. Plano técnico → módulos Bauhaus rellenos que giran cerca de la gente (marca ML). Afinar con el video de referencia |
| base6 | Matriz LED | `shaders/visuales/matrix_pulse.glsl` | compila, sin probar en TD. Celdas punto→cuadro, azul→amarillo, ondas + escaneo (marca ML) |
| base7 | Campo de eclipses | `shaders/visuales/eclipse_field.glsl` | compila, sin probar en TD. Cuadros amarillos + círculo negro del video; la gente empuja los círculos (negro/amarillo/lila) |
| base8 | Estela | `shaders/visuales/estela.glsl` | compila, preview con feedback OK, sin probar en TD. Trazo amarillo → azul ML que se desvanece (feedback=True) |
| base9 | Splashes | `shaders/visuales/splashes.glsl` | preview OK, sin probar en TD. Pedido del cliente: "splashes". Impacto + anillo con mira + corona de gotas; manchas persistentes (feedback, estado en alfa + `glsl_opaque` para salida opaca) |
| base10 | Destellos | `shaders/visuales/destellos.glsl` | jala en TD. Pedido del cliente: "destellos". Retícula LED que titila + 1 destello principal por persona (fijo encima) + satélites chicos (slider Satellites, 0 = solo el principal) + barrido |
| base11 | Esfera op-art | `shaders/visuales/op_sphere.glsl` | 2026-10-08, rescatada de _descartados (moodboard Mercado Ads). Compila + preview OK, sin probar en TD. Medias lunas blancas grandes, rueda al caminar |
| base12 | Arco de óvalos | `shaders/visuales/ovalos.glsl` | 2026-10-08, moodboard (reemplaza petal_bloom). Compila + preview OK, sin probar en TD. Anillo de óvalos que se voltean + esfera lila al centro (Core) |
| base13 | Cuadritos | `shaders/visuales/cuadritos.glsl` | 2026-10-08, moodboard. Compila + preview OK, sin probar en TD. Cuadros blancos que titilan → amarillos cerca de la gente |
| base14 | Ondas | `shaders/visuales/ondas.glsl` | 2026-10-08, moodboard. Compila + preview OK, sin probar en TD. Anillos tipo halo por persona, lila en los cruces |
| base15 | Esferas | `shaders/visuales/esferas.glsl` | 2026-10-08, moodboard. Compila + preview OK, sin probar en TD. Esferas con degradado empujadas por la gente (Accent = fracción lila) |
| base16 | Piso amarillo | `shaders/visuales/piso_amarillo.glsl` | 2026-10-08, guía de marca (amarillo 80%). Compila + preview OK, sin probar en TD. Eclipse negro por persona (smooth-min entre personas cercanas) |

**Cambios del cliente (2026-10-08)** — audio de Mich: 1) colores fáciles, 2) meter figuras del moodboard a los
interactivos, 3) screensavers en loop como capa alfa encima (Mich hace el fade al entrar alguien).
- Paleta Mercado Ads: Color1 amarillo #FFE600 (~80%) · Color2 lila #AB86FF (acentos ~5%) · Color3 negro. Ya NO azul ML
  ni azul marino. Defaults en todos los builders + `builders/herramientas/aplicar_paleta.py` (escribe en las bases vivas).
- Screensaver: `builders/herramientas/setup_screensaver.py` → `/project2/ML_screensaver`, 12 modos (menú Screensaver,
  Ciclo automático). Video: Piso LED · Mosaico (6 GLSL `screensaver_tile.frag` de una entrada + Add TOPs) ·
  Caleidoscopio · Espejo · Cinta · Ventanas (`screensaver_fx.frag`; 3–4 leen el piso, 5–6 el mosaico).
  Shader: Desfile · Eclipse · Óvalos · Constelación · Órbitas · Op-art gigante (`screensaver_gen.frag`, 6 GLSL `gen_*`
  sin entradas; funciones copiadas de `figuras.frag`; colores u_c1/u_c2/u_c3 = página Colores). Ninguno reacciona a la gente ni lleva marcadores. La pestaña Invitación / modo
  dormido se probó y se descartó (2026-10-08). `select` = Select TOP por expresión →
  `screensaver.frag` (fit + negro→alfa premultiplicado). Videos en `media/screensaver/`. `handoff.py` exporta
  `ML_screensaver.tox` (Folder = 'screensaver') + copia los videos. Preview: `exports/previews/screensavers.png`.
  **Cableado desde Python (aprendido en TD 2025.33230):**
  `glslTOP.inputConnectors[1]` no existe hasta que TD cocina (IndexError) y `outOP.outputConnectors[0].connect(OP)`
  conecta SIEMPRE a la entrada 0 (reemplaza). Usar solo `inputConnectors[0]` de GLSL y OPs de 2 entradas fijas
  (Add TOP), y para elegir entre fuentes un Select TOP con `top.expr` (solo cocina la elegida). La página Samplers
  del GLSL (`samplerNname/top`) se intentó y no se confirmó que funcionara en TD (se dejó de usar).
- Moodboard (figuras): destello (≈ base10), eclipse (≈ base7), esfera op-art blanca (≈ `_descartados/op_sphere`),
  arco de óvalos amarillos (≈ `_descartados/petal_bloom`), esfera lila con degradado, cuadritos blancos.

- **Capa Figura** (2026-10-08): `build_visual(figures=None→tracking)` crea la página **Figura** + GLSL `figuras`
  (`shaders/herramientas/figuras.frag`) justo antes de `bypass` (después de `extra`). Menú: Original · Esfera op-art ·
  Arco de óvalos · Destello · Eclipse · Esfera lila (colores de marca fijos). Shaders con `u_hide_marker`
  (bauhaus_ml, envios_network, flow_field, matrix_pulse: `marker()` envuelve a `marker0()`) ocultan su marcador
  mientras hay figura. base11/base12 usan `figures=False`. Preview: `exports/previews/figuras.png`.

**Dirección creativa (2026-09-23):** lo que funciona es FloorPresence: se ve *tech*/funcional y la interacción
se lee clara. Seguir por ahí + **marca Mercado Libre** (amarillo #FFE600, azul #3483FA, fondo azul marino;
mundo de envíos/rutas/paquetes/datos). Explorar de 1–2 looks por ronda.
Descartados (en `shaders/_descartados/`): esfera op-art, burbujas amarillas, flor de pétalos, Bauhaus+vidrio. Todo lo activo (base1–16, rig lleno) ya va en la línea tech + ML; se conservan todas.

## Notas del show

<!-- Tuyo: fechas, venue, resolución real del piso LED, ruta del CHOP de tracking, lo que funcionó en ensayo. La skill no borra esta sección. -->
