# Referencia: lookup de color de /project1 (quitado 2026-11-04)

Solo referencia para un futuro FX global de color. Todo está en `/project2/_respaldo/project1_lookup_color` (sin cook): se puede copiar de vuelta tal cual.

## Cómo estaba conectado

```
feedback_HSV1 ─┬─> null42 ──────────────────────────┐ in1 (limpio)
               └─> lookup2 (in0 = imagen)           │
                     ^ in1 = paleta                 ├─> V2_COLOR (blend switch, Scene = pad ch1n13 · null39)
                     │                              │      fundido entre in1 limpio e in2 con lookup
                   base6  <── switch5 ──┐           │
                                        │  lookup2 ─┘ in2
   blend_switch2 (ramp1..16, fijas)  ───┤  switch5.index = pad ch1n28 (null50): 0 = fijas · 1 = en movimiento
   blend_switch3 (ramp17..32, phase = absTime.seconds * 0.3: se mueven solas) ─┘
   blend_switch2/3.Scene = tecla 'kdown' (null1): paleta siguiente dentro del banco
```

- **Lookup TOP** (`lookup2`): pinta la imagen según su brillo con la paleta de la entrada 1 (gradient map / duotono).
- **base6 = "convertidor de rampas"** (el .tox): `in1` (imagen de rampa) → `topto1` (TOP→CHOP) → `pattern1` → `chopto1/2` (CHOP→DAT) → `merge1` → `ramp1_keys` → `ramp1` (Ramp TOP reconstruida, suave). Expone **Phase** (bind a `ramp1.par.phase`) para girar la paleta. Sirve para tomar CUALQUIER imagen de rampa y volverla rampa de TD con fase.
- **Rampas**: Ramp TOP con tabla `rampN_keys` (pos r g b a), 3–4 colores. Ej. ramp1: negro → naranja (1, 0.3, 0) → ámbar (1, 0.58, 0), `extendleft = mirror`.
- **blend_switch2 / blend_switch3 / V2_COLOR** son el mismo COMP "blend switch" (Scene · Numinputs · Blendtime): cambia de entrada con fundido; replicator crea `in1..inN`.

## Lo que se movía en vivo (para el color futuro)

- **Fase de la paleta en movimiento**: `phase = absTime.seconds * 0.3` (banco 17–32). → En el FX nuevo: un **Phase** (giro de la paleta) con velocidad propia o con `uPhase` del reloj acumulado, y opción de que el audio lo empuje.
- **Period** que gustaba mover: knob **CC53** (`/project2/control_p1/null11` `ch1ctrl53`) → `curcuitBending.Period` (periodo del ruido del circuit bending; NO es del lookup, sigue funcionando).
- Elegir paleta: pad `ch1n28` (banco fijo / en movimiento) + tecla `kdown` (siguiente paleta) + pad `ch1n13` (limpio ↔ lookup con fundido).

## Idea para rehacerlo (cuando se haga)

Un solo FX global **Color Overlay** en vez de 32 Ramp TOPs: GLSL que haga el gradient map con la **paleta del álbum** (`_lib/paleta.py`) y parámetros **Mezcla** (limpio ↔ paleta, el fundido de V2_COLOR) · **Phase** (giro) · **Velocidad** (fase en movimiento) · **Paleta** (cuál) · **Contraste**. Va en /project1 antes de `color_final`, con sus 5 knobs en el hub `show` y la UI.
