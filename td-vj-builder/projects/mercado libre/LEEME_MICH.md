# Visuales del piso LED · Mercado Libre — handoff

## Plug & play (recomendado): `ML_floor_pack.tox`

Todo en uno: el hub de tracking + todos los visuales + un menú para elegir cuál sale.

1. Arrastra `ML_floor_pack.tox` a tu red (p. ej. `/project2`).
2. Entra al pack → nodo **tracking_input** → página **Input**:
   - **Con TOP de blobs (recomendado):** **Source** = `Externo TOP (blobs)` y arrastra tu TOP al campo
     **TOP de blobs** (ver abajo).
   - **Con CHOP:** **Source** = `Externo CHOP (Hokuyo)` y arrastra tu CHOP al campo **CHOP externo**.
   - Mira **Status**: debe decir `top · N persona(s)` o `external · N persona(s)`.
3. En el pack, página **Pack** → **Visual**: elige el look. La salida es `out1` del pack (1920x1080 por ahora).

Viene con **Source = Simulate** (3 caminantes sintéticos) para que veas movimiento en cuanto lo abras.

## Opción recomendada: mandar un TOP con blobs (Source = `Externo TOP (blobs)`)

En vez de un CHOP, manda una **textura**: fondo negro y **un blob blanco por persona**.
El cuadro completo = el piso (abajo-izquierda del TOP = esquina abajo-izquierda del piso).

1. `tracking_input` → página **Input** → **Source** = `Externo TOP (blobs)`.
2. Arrastra tu TOP al campo **TOP de blobs**. **Status** debe decir `top · N persona(s) · N mancha(s)`.
3. Página **Seguimiento**:
   - **Threshold**: brillo mínimo para contar como blob (0.5 sirve para blanco sobre negro).
   - **Min Area**: px mínimos de un blob (a la resolución de análisis) → filtra ruido.
   - **Dilate**: une pedazos de una misma persona (p. ej. dos piernas) en un solo blob.
   - **Resolución de análisis W**: el TOP se reduce a este ancho (160 por defecto; el alto sigue
     la proporción del piso). Más = más preciso y más lento.
   - **Match Dist / Smooth / Hold**: seguimiento. Cada blob recibe un **ID estable** mientras se
     mueva; si desaparece se conserva **Hold** frames y luego se suelta. No hay lista que crezca:
     cada frame se lee de la imagen.
   - **Max People**: hasta 8.
4. Dentro de `tracking_input` está **blob_view** (vista de debug): blanco = blob, cruz roja = blob
   ignorado, cruz de color = persona seguida (un color por slot).
5. **Swap XY / Flip X / Flip Y / Descartar fuera del piso** también aplican aquí.
   (Unidades y Origen no: el TOP ya es el piso completo.)

Si dos personas se juntan tanto que sus blobs se tocan, cuentan como una sola hasta separarse.

## Screensaver: `ML_screensaver.tox` + carpeta `screensaver/`

12 screensavers en **capa alfa** para poner **encima** del pack: el negro sale transparente.
Tú haces el fade (cuando entra alguien, Opacity/Level a 0 → solo queda el interactivo).

6 son **de video** (los videos del cliente reacomodados) y 6 **de shader** (las figuras del moodboard en
composiciones grandes). Ninguno reacciona a la gente ni lleva marcadores: eso solo pasa en las escenas
interactivas.

1. Copia la carpeta **`screensaver/`** (los videos) **junto a tu `.toe`** — los videos no caben dentro de un .tox.
2. Arrastra `ML_screensaver.tox` a la misma red que `ML_floor_pack`.
3. Compón: `ML_screensaver/out1` **encima** de `ML_floor_pack/out1` (Over TOP o Composite TOP, modo Over).
   La salida es RGBA premultiplicada y ya sale a la resolución del hub (`tracking_input` → Salida).
4. Página **Screensaver**:
   - **Screensaver** — de video: `Piso LED` · `Mosaico de cuadros` (los 6 videos cuadro A–F en 3×2) ·
     `Caleidoscopio` (piso en 6 gajos) · `Espejo` (piso en 4 cuadrantes) · `Cinta de cuadros` (filas que corren) ·
     `Ventanas` (los 6 cuadros flotando). De shader: `Desfile de figuras` · `Eclipse` · `Óvalos` · `Constelación` · `Órbitas` ·
     `Op-art gigante`.
   - **Ciclo automático** + **Segundos por screensaver**: los va rotando solo. Apagado = el del menú.
   - **Velocidad (efectos y shaders)**, **Separación de los cuadros**.
   - **Carpeta de videos**: viene `screensaver` (relativa a tu .toe; también acepta ruta absoluta).
     **Video piso** = nombre del archivo del piso.
   - **Fit** (para el video del piso): `Llenar` (recorta) · `Encajar` · `Estirar`.
   - **Alpha**: `Negro → transparente` · `Opaco`. **Nivel de negro**: súbelo si el fondo no queda limpio.
   - **Opacity**: para pruebas; el fade de show es tuyo.
5. Página **Colores**: Color 1 (amarillo) · Color 2 (lila) · Color 3 (blanco) de los screensavers **de shader**
   (por si piden ajustes). Los de video son los archivos del cliente y no cambian de color.

## Paleta

Todos los visuales usan la paleta Mercado Ads: **Color1 amarillo #FFE600** (protagonista) · **Color2 lila
#AB86FF** (acentos) · **Color3 negro** (fondo). Se cambian en la página Visual de cada base.

## Los visuales

| Base | Look |
|---|---|
| base1 · floor_presence | auras que se fusionan + ondas + capa Debug de calibración |
| base2 · envios_network | red de envíos: nodos + rutas con paquetes entre personas cercanas |
| base3 · hud_detection | HUD de detección: caja + etiqueta por persona, guías, medición, radar |
| base4 · flow_field | flujo de líneas que rodea a cada persona, con paquetes viajando |
| base5 · bauhaus_ml | módulos Bauhaus que se rellenan y giran alrededor de cada persona |
| base6 · matrix_pulse | matriz LED: celdas que crecen y se encienden alrededor de cada persona |
| base7 · eclipse_field | cuadros amarillos con círculo negro que las personas empujan |
| base8 · estela | cada persona pinta el piso: trazo amarillo que envejece a azul (botón "Reset estela") |
| base9 · splashes | cada persona salpica: impacto + corona de gotas que dejan manchas (botón "Reset estela") |
| base10 · destellos | puntos LED que titilan; un destello fijo sobre cada persona + satélites chicos (slider Satellites) |
| base11 · op_sphere | esfera op-art blanca (moodboard) que rueda bajo cada persona |
| base12 · ovalos | anillo de óvalos amarillos que se voltean como monedas + esfera lila al centro (moodboard) |
| base13 · cuadritos | cuadros blancos que titilan; cerca de cada persona crecen y se vuelven amarillos |
| base14 · ondas | cada persona emite anillos amarillos tipo halo; lila donde se cruzan las ondas |
| base15 · esferas | campo de esferas amarillas (algunas lila) que la gente empuja y agranda |
| base16 · piso_amarillo | piso todo amarillo; cada persona abre un eclipse negro con borde brillante |

Cada base tiene:
- Página **Figura** (todas menos base11 y base12, que ya son figuras): **Figura por persona** = `Original` (el look tal cual) o una figura del
  moodboard encima de cada persona: `Esfera op-art` · `Arco de óvalos` · `Destello` · `Eclipse` · `Esfera lila`.
  **Tamaño (m)**, **Opacidad**, **Velocidad**. **Ocultar marcador original** quita el anillo/mira de la base
  mientras hay figura. Así cada look tiene las dos opciones.
- Página **Visual**: 5 sliders en orden fijo (1 intensidad · 2 velocidad · 3 distorsión · 4 color · 5 firma),
  extras propios del look, Color1–3 y Bypass.
- Página **Tracking**: ya apunta al hub (`tracking_input/out1`, ruta relativa). **Simulate** aquí es local
  (ignora el hub); déjalo apagado. Piso, flips y resolución se ajustan solo en el hub.

## Sin el pack (montar bases sueltas en tu rig)

`tracking_input.tox` + `baseN_<nombre>.tox`: arrástralos **al mismo nivel** (hermanos). Cada base busca
`tracking_input` junto a ella. El hub se configura igual que arriba.
