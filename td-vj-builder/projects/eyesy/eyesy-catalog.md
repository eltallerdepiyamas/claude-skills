# EYESY Virtual — catálogo de modes y mapa de familias

Proyecto: recrear la librería de factory modes del EYESY (Critter & Guitari, pygame)
como visuales GLSL en base1–16. 34 modes analizados desde sus `main.py` originales.
Los dos modes de feedback puro (espejo infinito, bola-espejo) se excluyen: el usuario
genera su feedback aparte. Overflow a base18–24/38–45 solo si hace falta (documentar).

## Mapa base → familia (aprobado 2026-07)

| Base | Familia | Modes originales agrupados | Variant (signature) |
|---|---|---|---|
| base1 | Scope clásico | línea conectada; línea+sombra gris; rayos de ancla-LFO a la onda; área rellena bajo la curva (filled scope) | 0=línea 1=sombra 2=rayos 3=área rellena |
| base2 | Scope barras | barras+bolitas vertical; horizontal; dos paneles (knob1/knob2 origen); tres zonas espejadas | orientación/layout |
| base3 | Spectrum retícula | retícula+barras desde bordes; retícula+barras espejo al centro | 0=bordes 1=centro |
| base4 | Grid | círculos; triángulos; rects outline; rects filled; polígonos random (trigger); grid 4 capas nudge | forma |
| base5 | Radiales | pinwheel de rayos; anillo scope; triángulos sobre círculo; brazos giratorios (peak) | 0..3 |
| base6 | Perimeter arcs | arcos en 4 bordes (trae selector propio de 6 formas → se respeta como sub-selector) | forma del arco |
| base7 | Perimeter líneas | líneas en 4 lados con LFOs adjust1/adjust2 | — |
| base8 | Random lines trigger | horizontales; verticales; horizontales+sombra; verticales+sombra | orient×sombra |
| base9 | Trigger shapes | cuadros random; cluster de bolas denser-LFO; triángulo mutante; rect caminante 8-dir; ráfaga líneas+scanlines | 0..4 |
| base10 | Nubes de círculos | cluster serpenteante (gradientes); gusano vertical swell | 0..1 |
| base11 | Fila LFO | triángulos en fila rebotando; círculos en fila | 0=tri 1=circ |
| base12 | Barras LFO | dos barras viajeras (4 líneas); barras subiendo (rise) | 0..1 |
| base13 | Líneas viajeras | screensaver línea horizontal; aguja rotatoria on-trigger (con trails→Bgsel alpha) | 0..1 |
| base14 | Web/abanico | aalines cruzadas web; abanico 5 puntos; béziers random on-trigger | 0..2 |
| base15 | Caras | boca scope + ojos LFO; boca con dientes (sin su feedback) | 0=ojos 1=dientes |
| base16 | Bounce | bola rebotando (trigger baja y); triángulo rotando rebotando | 0..1 |

## Estado

- [x] Infraestructura EYESY_AUDIO (waveform 100x1 + peak/trigcount)
- [x] base1 Scope clásico — piloto (setup_base1_eyesy_scope.py). Nota: V3 cambiado
  de "barras+puntos" a "área rellena bajo la curva" para eliminar redundancia con base2.
- [x] base2 Scope barras — 4 layouts (setup_base2_eyesy_scopebars.py)
- [ ] base3–16 — producir por tandas tras validar los pilotos

## Notas de análisis

- Patrón dominante: loop de 50–100 segmentos leyendo `audio_in[i]`, color por bloque
  `sel = knob4*8` con `sin(i*c + time)`. → paleta `eyesyPal` compartida.
- Trigger (`audio_trig or midi_note_new`) re-randomiza listas de posiciones → en GLSL:
  `trigcount` como uSeed + hash. Familias 8, 9, 14, 16 lo necesitan.
- Trails con `veil.set_alpha` (aguja, béziers): aproximar con feedback del usuario o
  ignorar (el fondo opaco del frame ya limpia).
- Knob5 siempre = bg color → extra `Bgsel` en todas las familias.
