# Proyecto CRT SCAN — especificación única para Claude Code

Documento maestro con todo lo pendiente del rig de procesamiento CRT. Ejecuta
las secciones en orden; cada una es independiente y trae sus propios criterios
de aceptación.

**Boilerplate común a todo lo de aquí:** shader `.frag` + builder Python
idempotente, 5 macros en orden de rol (intensidad, velocidad, distorsión, color,
firma) + páginas completas + presets + página Audio, uniforms empacados en
`vec4`, `_set_expr` tolerante a versión de TD, `null_src` entre la fuente y el
resto de la red. Referencia viva: `setup_base18_crt.py`. No reinventes la
estructura: cópiala y cámbiale el contenido.

## Índice

1. **Parche base18** — `ParMode` y cableado del feedback
2. **Reset por página** — base18 y base19
3. **`signal_bend`** — circuit bending de video en base19

---

# 1. Parche de `setup_base18_crt.py`

Dos cambios. No toques nada más del archivo (shader, presets, páginas y contrato
de 5 macros se quedan igual).

---

### 1. Arreglar `AttributeError: module 'td' has no attribute 'ParMode'`

En esta build de TouchDesigner `ParMode` no es atributo del módulo `td`. Además,
asignar `.expr` ya pone el parámetro en modo expresión por sí solo, así que la
línea `p.mode = ...` es redundante en todos los casos.

**Agrega este helper** junto a los demás helpers (después de `_set_par_any`):

```python
def _set_expr(p, e):
    """Asigna una expresion de forma tolerante a la version de TD.
    Asignar .expr ya cambia el modo a EXPRESSION; el set explicito de modo
    solo se intenta si ParMode existe en esta build."""
    if p is None:
        return False
    try:
        p.expr = e
    except Exception:
        return False
    PM = getattr(td, 'ParMode', None) or globals().get('ParMode', None)
    if PM is not None:
        try:
            p.mode = PM.EXPRESSION
        except Exception:
            pass
    return True
```

**Reemplaza TODAS las ocurrencias de `p.mode = td.ParMode.EXPRESSION` (y
variantes `gp.mode`, `vp.mode`, `sw.par.index.mode`) usando `_set_expr`.**
Son cuatro sitios:

1. En `_set_par_any`, la rama `if mode == 'expr':`
   ```python
   if mode == 'expr':
       if not _set_expr(p, value):
           continue
   ```
   (quita el `p.mode = td.ParMode.EXPRESSION` de ahí)

2. En `_bind_uniform`, el bloque que hace `vp.expr = e` → cámbialo por
   `_set_expr(vp, e)` y borra la línea de `.mode`.

3. En `build`, el binding de resolución:
   ```python
   if rp:
       _set_expr(gp, f"op('{sm.path}').par.{rp}")
   else:
       gp.val = fb
   ```

4. En `build`, el switch de bypass:
   ```python
   _set_expr(sw.par.index, 'parent().par.Bypass')
   ```

Después no debe quedar **ninguna** referencia a `td.ParMode` en el archivo.
Verifícalo con una búsqueda antes de terminar.

---

### 2. Meter un Null entre el Movie File In y el resto (incluido el feedback)

El `feedbackTOP` necesita una textura de entrada válida para inicializarse y
tomar resolución; sin input puede quedar negro o tronar. La fuente pasa a ir por
un Null que alimenta todo.

**Cambios en `build`:**

- Agrega `'null_src'` a la lista `managed` (para que la limpieza siga siendo
  idempotente).

- Justo después de crear y configurar `moviefilein1`, crea el null:

  ```python
  src = _create(base, nullTOP, 'null_src', -700, 0)
  _connect(mov, src)
  ```

- **Recablea todo lo que hoy sale de `mov` para que salga de `src`:**
  - `_connect(mov, glsl, 0)`      → `_connect(src, glsl, 0)`
  - `_connect(mov, cross, 0)`     → `_connect(src, cross, 0)`
  - `_connect(mov, sw, 1)`        → `_connect(src, sw, 1)`

- **Conecta el null a la entrada del feedback**, además de dejar su `Target TOP`
  apuntando al GLSL (el target es lo que captura; la entrada es lo que lo
  inicializa). El bloque del feedback queda así:

  ```python
  fb = _create(base, feedbackTOP, 'feedback1', -300, -200)
  _set_par_any(fb, (('top', glsl.name, 'val'), ('targetop', glsl.name, 'val'),
                    ('target', glsl.name, 'val')))
  _connect(src, fb, 0)      # inicializa el buffer con la fuente
  _connect(fb, glsl, 1)     # feedback -> input 1 del shader (persistencia)
  ```

- La expresión de `SRC_ASPECT` dentro de `UNIFORM_PACK` sigue leyendo
  `op('moviefilein1')` — **déjala así**, el aspecto viene del archivo original,
  no del null.

---

### Criterio de aceptación

Correr el script en un Text DAT dentro de `base18` no debe tirar excepción, y en
la red deben quedar: `moviefilein1 → null_src`, y de `null_src` salen tres
cables (a `glsl_crt` input 0, a `cross_intensity` input 0, a `switch1` input 1) más
uno a `feedback1` input 0. `feedback1` sale al input 1 de `glsl_crt`.
Los parámetros con expresión (resolución, uniforms, bypass, file/play/speed del
movie) deben verse en modo expresión (fondo azul) en la UI.

---

# 2. Reset por página (base18 CRT y base19 Bend)

Aplica a `setup_base18_crt.py` y al builder de base19. Mismo boilerplate, no
toques nada más.

### Qué se pide

Cada página de parámetros tiene **su propio botón de reset**, que devuelve a
default **solo los parámetros de esa página**. Hoy el reset arrasa con todo,
incluido el playback, y eso no puede pasar.

### Reglas

1. **Un pulse por página**, como último parámetro de cada una:
   `Resetfilter`, `Resetsource`, `Resetgeometry`, `Resetscan`, `Resetmask`,
   `Resetsignal`, `Resetgrade`, `Resetglow`, `Resetnoise`, `Resetwobble`,
   `Resetaudio`. (En base19: `Resetsync`, `Resetclock`, `Resetchroma`,
   `Resetosc`, `Resetcorrupt`, `Resetsparkle`, `Resetdrift`.)
   Label legible: `Reset Filter`, `Reset Geometry`, etc.

2. **El reset opera únicamente sobre los parámetros de su propia página.** Saca
   la lista de la página, no de una lista hardcodeada:
   ```python
   for pg in comp.customPages:
       if pg.name == page_name:
           pars = list(pg.pars)
   ```

3. **Lista negra global — estos NUNCA se resetean, en ningún reset:**
   - `Videofile`, `Play`, `Playspeed` → el video que está corriendo **no se
     toca jamás**. Este es el bug principal a arreglar.
   - Cualquier parámetro de tipo pulse (no tienen estado).
   - `Preset` → ver punto 4.

4. **El reset no debe disparar el callback de presets.** Hoy `Preset` está
   cableado a `onValueChange` → `applyPreset`, así que si el reset lo toca (o si
   al resetear otro parámetro se re-evalúa) se re-aplica el preset entero y se
   pierde el reset. Dos medidas, ambas:
   - Excluir `Preset` de todo reset.
   - Bandera de supresión a nivel de módulo en el DAT de presets:
     ```python
     _SUPPRESS = False

     def onValueChange(par, prev):
         if _SUPPRESS or par.name != 'Preset':
             return
         applyPreset(par.owner, par.eval())
     ```
     y en la función de reset, `global _SUPPRESS; _SUPPRESS = True` antes del
     loop y `False` en un `finally`.

5. **Reset = volver al `default` declarado del parámetro**, no a los valores del
   preset activo:
   ```python
   p.val = p.default
   ```
   Envuelto en try/except por parámetro, para que uno que falle no aborte el
   resto.

6. **Añade también `Resetall`** en la página Filter, debajo de `Resetfilter`:
   resetea todas las páginas respetando la misma lista negra (o sea, el video
   sigue corriendo). No es sustituto de los resets por página.

### Dónde vive el código

En el mismo Parameter Execute DAT `presets` (que ya escucha pulses vía
`onPulse`). Una sola función genérica, no una por página:

```python
PAGE_BY_PULSE = {
    'Resetfilter': 'Filter', 'Resetsource': 'Source',
    'Resetgeometry': 'Geometry', 'Resetscan': 'Scan', 'Resetmask': 'Mask',
    'Resetsignal': 'Signal', 'Resetgrade': 'Grade', 'Resetglow': 'Glow',
    'Resetnoise': 'Noise', 'Resetwobble': 'Wobble', 'Resetaudio': 'Audio',
}

NEVER_RESET = {'Videofile', 'Play', 'Playspeed', 'Preset'}

def resetPage(comp, page_name):
    global _SUPPRESS
    _SUPPRESS = True
    try:
        for pg in comp.customPages:
            if pg.name != page_name:
                continue
            for p in pg.pars:
                if p.name in NEVER_RESET or p.style == 'Pulse':
                    continue
                try:
                    p.val = p.default
                except Exception:
                    pass
        print('[reset] %s -> pagina %s' % (comp.path, page_name))
    finally:
        _SUPPRESS = False


def onPulse(par):
    if par.name == 'Applypreset':
        applyPreset(par.owner, par.owner.par.Preset.eval())
    elif par.name == 'Resetall':
        for pgname in set(PAGE_BY_PULSE.values()):
            resetPage(par.owner, pgname)
    elif par.name in PAGE_BY_PULSE:
        resetPage(par.owner, PAGE_BY_PULSE[par.name])
```

Ajusta `PAGE_BY_PULSE` a las páginas reales de cada base.

### Criterios de aceptación

- Con un video reproduciéndose, pulsar **cualquier** reset (incluido
  `Resetfilter` y `Resetall`) deja el video corriendo, en el mismo punto, con la
  misma ruta de archivo.
- `Resetgeometry` no altera ningún parámetro de Scan, Mask, etc., y viceversa.
- Después de un reset, el menú `Preset` conserva su valor y **no** se re-aplica
  el preset.
- Los pulses aparecen al final de su página, no mezclados entre los sliders.
- El builder sigue siendo idempotente.

---

# 3. Efecto `signal_bend` — circuit bending de video (base19)

> **Estado: en revisión.** La primera versión no dio el look esperado. Antes de
> volver a construir, espera la corrección de dirección del usuario sobre qué le
> faltó (violencia / que se vea como señal rota y no como ruido encima / que la
> imagen se desarme por completo a ratos). El brief de abajo sigue siendo la
> base conceptual válida.

Construye un efecto nuevo siguiendo **exactamente el mismo boilerplate** que
`setup_base18_crt.py` (shader `.frag` + builder Python idempotente, 5 macros en
orden de rol + páginas completas + presets + página Audio, uniforms empacados en
`vec4`, `_set_expr` tolerante a versión, `null_src` entre la fuente y todo lo
demás). No reinventes la estructura: cópiala y cámbiale el contenido.

- Base destino: **base19**
- Shader: `<project.folder>/effects_glsl/shaders/signal_bend.frag`
- Builder: `setup_base19_bend.py`
- GLSL TOP: `glsl_bend`, 16-bit float, feedback en input 1

---

### Qué es circuit bending de video (esto es el brief, léelo antes de codear)

Circuit bending es cortocircuitar puntos de la placa de un aparato de video
—una cámara, un VCR, un mezclador— con cables, resistencias o pots, para que el
circuito haga cosas que su diseñador nunca previó. No es "añadir ruido encima de
la imagen": es **corromper la señal mientras se está formando**, antes de que
llegue al tubo. Eso da un carácter muy específico que hay que respetar:

1. **La sincronía se rompe antes que la imagen.** El separador de sync es lo
   primero que se degrada: las líneas se desplazan horizontalmente cada una por
   su cuenta, la imagen se inclina (skew), el enganche vertical patina. La
   imagen sigue *ahí*, solo que cada línea llega tarde o temprano.

2. **Luma y croma se divorcian.** En NTSC/PAL el color viaja como una
   subportadora montada sobre la luminancia. Al puentear esa zona, el color deja
   de corresponder al objeto: aparecen bandas de arcoíris que no siguen los
   bordes, el tono rota según el brillo, y zonas oscuras salen saturadas.
   **Esta es la firma más reconocible del bending, más que el ruido.**

3. **Los relojes glitchean → estructura de columnas.** Al meterle mano a los
   registros de desplazamiento y a los clocks de muestreo, el circuito
   *sostiene* un valor más tiempo del que debe: nacen columnas verticales que
   repiten el mismo píxel, con ancho que late. Eso es lo que se ve en la
   referencia: un peine vertical de columnas onduladas, no ruido aleatorio.

4. **La imagen se realimenta a sí misma.** El brillo empuja la posición: las
   zonas claras desplazan más, así que la imagen se deforma según su propio
   contenido. Por eso el resultado *parece* tener estructura orgánica aunque sea
   un error.

5. **Errores de bit, no de nivel.** En aparatos digitales el bend produce
   inversiones duras y saltos de color: valores que se voltean (XOR), niveles
   que se cuantizan brutalmente. Bloques de color plano e invertido, con bordes
   rectos, no degradados suaves.

6. **El circuito se autooscila.** Un bend puesto no se queda quieto: canta,
   deriva, entra y sale de resonancia solo. Los parámetros deben tener un
   componente de deriva lenta y de acoplamiento entre sí, no valores fijos.

7. **Todo se sobrecarga.** Los amplificadores clipean: aparecen puntos blancos
   brillantes (sparkle) y florecimiento en los picos.

**Lo que NO es:** grano de película, glitch datamosh, ruido de sal y pimienta
uniforme, ni un filtro de color plano encima. Si el resultado se ve como "ruido
sobre el video" en vez de "video mal construido", está mal.

**Referencia visual objetivo:** peine de columnas verticales onduladas,
desplazamiento por línea acoplado al brillo, bandas de croma arcoíris
independientes del contenido, rejilla de puntos blancos en los picos, bloques de
inversión de color. Sobre todo eso, el CRT (base18) hace el resto.

---

### Cadena de señal

`base19 (bend)` va **antes** de `base18 (CRT)`: primero se corrompe la señal,
después el tubo la muestra. Implementa:

- En **base19**: `moviefilein1 → null_src → glsl_bend → cross → switch(Bypass) → null1 → out1`
  (mismo patrón que base18, feedback en input 1).
- En **base18**: agrega en la página `Source` un menú `Inputsource` con opciones
  `Archivo propio` / `Bend (base19)`. Un Select TOP apuntando a
  `/project2/base19/out1` y un Switch TOP antes de `null_src` eligen la fuente.
  No rompas nada más de base18.

---

### Etapas del shader, en este orden

Ese orden importa: cada etapa corrompe lo que dejó la anterior, igual que en la
placa real.

1. **Deriva / caos.** Calcula un `drift` global: ruido de valor suave (varias
   octavas lentas) que modula sutilmente casi todos los parámetros. `Chaos`
   controla cuánto se acoplan entre sí (con Chaos alto, el bend de sync también
   mueve el croma y el ancho de columna).

2. **Sync corruption.** Por cada línea de barrido:
   - offset horizontal = suma de (a) un oscilador lento, (b) `hash(line, tiempo)`
     escalonado (no continuo — las líneas saltan, no fluyen), (c) el brillo medio
     de la línea (crossfeed luma→posición).
   - `Skew`: rampa acumulada de arriba a abajo (imagen inclinada).
   - `Linedrop`: probabilidad de que una línea entera se reemplace por la línea
     de otra posición (línea perdida, no negra).
   - `Vhold`: patinaje vertical que envuelve con `fract`, no recorta.

3. **Sample & hold / columnas.** Cuantiza `uv.x` en columnas: 
   `uvx = floor(uv.x * cols) / cols`. `cols` modulado por un LFO y por `drift`
   para que el ancho ondule. Añade `Holdskew`: la fase de la cuantización se
   corre según `uv.y`, lo que curva las columnas (la ondulación de la
   referencia). Opcional `Holdmix` para mezclar entre columna dura y suave.

4. **Luma → displacement.** El brillo de la muestra empuja en x (y un poco en y).
   Es realimentación: usa la muestra ya desplazada para calcular el empuje
   siguiente en un segundo tap.

5. **Croma desacoplado.** Separa luma y croma:
   - Muestrea el croma en un uv distinto al de la luma (`Chromaoffset` en x/y).
   - Rota el tono según el brillo: `hue += luma * Hueluma + tiempo * Huedrift`.
   - `Chromagain` sobre 1.0 sobresatura; permite que se pase de rango y clipee.
   - Convierte con `TDRGBToHSV`/`TDHSVToRGB` o helpers propios.

6. **Inyección de oscilador.** Suma a cada canal un oscilador
   (`mix` seleccionable entre seno y cuadrada) con frecuencia alta sobre x y
   frecuencia distinta por canal (`Oscfreq`, `Oscspread` separa R/G/B). Esto
   produce las bandas de arcoíris fijas que no siguen al contenido. La amplitud
   se puede gatear por luma para que solo aparezca en zonas con señal.

7. **Corrupción de bits.** `Crush`: cuantiza a N niveles. `Xor`: convierte a
   entero 0–255, aplica XOR con una máscara derivada de posición y tiempo, y
   vuelve a float. Mezcla el resultado con `Xoramount` — a full es demasiado,
   pero en bloques gatillados por umbral queda como el aparato real.

8. **Sparkle.** Rejilla de puntos de alta frecuencia (no ruido libre) gateada por
   un umbral de luma: donde la señal satura, aparecen puntos blancos.

9. **Feedback (input 1).** Mezcla con el frame anterior con decay, pero con el uv
   ligeramente rotado/escalado (`Fbzoom`, `Fbrot`) para que el error se arrastre
   y crezca, que es lo que hace que un bend "cante". Decay **siempre < 1.0**.

10. **Wet/dry** con `Intensity` contra la fuente original.

---

### Los 5 macros (orden de rol, contrato MIDI)

| # | Rol | Par | Default | Rango | Qué hace |
|---|-----|-----|---------|-------|----------|
| 1 | intensidad | `Intensity` | 1.0 | 0–1 | wet/dry global |
| 2 | velocidad | `Speed` | 1.0 | 0–4 | rate de osciladores y deriva |
| 3 | distorsión | `Bend` | 0.4 | 0–1 | master de sync + columnas + luma→pos |
| 4 | color | `Chroma` | 0.4 | 0–1 | master de desacople + hue + oscilador |
| 5 | firma | `Chaos` | 0.25 | 0–1 | inestabilidad y acoplamiento entre etapas |

`Chaos` es la firma porque es lo que distingue un bend de un filtro: un knob que
hace que el circuito se vuelva impredecible sin tocar nada más.

### Páginas completas

- **Sync**: `Lineshift`, `Linestep` (cuantización temporal del salto), `Skew`,
  `Linedrop`, `Vhold`, `Vholdspeed`
- **Clock**: `Columns` (8–512), `Colwave` (profundidad de la ondulación),
  `Colwavefreq`, `Holdskew`, `Holdmix`
- **Feedback luma**: `Lumapush`, `Lumapushy`, `Lumabias`
- **Chroma**: `Chromaoffsetx`, `Chromaoffsety`, `Hueluma`, `Huedrift`,
  `Chromagain`, `Chromaclip`
- **Osc**: `Oscamt`, `Oscfreq`, `Oscspread`, `Oscshape` (menú seno/cuadrada),
  `Oscgate`
- **Corrupt**: `Crush` (2–256 niveles), `Xoramount`, `Xormask`, `Xorthresh`
- **Sparkle**: `Sparkleamt`, `Sparklescale`, `Sparklethresh`
- **Drift**: `Driftamt`, `Driftspeed`, `Fbdecay` (<1.0), `Fbzoom`, `Fbrot`

### Presets

`bend_suave` (defecto: legible, columnas apenas onduladas, croma corrido),
`peine` (la referencia: columnas duras, croma arcoíris, sparkle),
`sync_perdido` (skew y line drop al frente, poco color),
`arcoiris` (croma y oscilador dominantes, geometría estable),
`bits_rotos` (XOR y crush al frente),
`autooscila` (Chaos y feedback altos — advertir en comentario que se va solo),
`limpio` (todo en cero para A/B).

Presets parciales heredan de `bend_suave`, igual que en base18.

### Audio

Página estándar del rig. `Audioreact` **off** por defecto, `Audiotarget` en
`Bend`, `Audiomult` 0.5.

### Criterios de aceptación

- Corre en un Text DAT dentro de base19 sin excepción, y es idempotente
  (correrlo dos veces no duplica nodos ni parámetros).
- Con `bend_suave` la imagen sigue siendo reconocible; con `peine` se parece a la
  referencia: columnas verticales onduladas + bandas de croma + puntos blancos.
- Ningún `uniform sampler2D`: todo por `sTD2DInputs[i]`.
- Nada de `td.ParMode` (usa `_set_expr`).
- 1080p60 sin caer: máximo ~14 fetches de textura, sin loops de más de 8
  iteraciones, sin ramas pesadas por píxel.
- `Fbdecay` nunca llega a 1.0 (se satura a blanco).
