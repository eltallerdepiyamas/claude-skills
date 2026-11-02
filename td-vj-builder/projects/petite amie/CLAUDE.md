# PROYECTO: Petite Amie — Foro La Paz · CDMX · sábado 25 julio 2026, 20:00

Generado por `td-vj-builder`. Contexto en disco para este show — no re-preguntar en próximas sesiones.

**Última actualización:** 2026-07-24 · **23/23 items escritos** (Tandas 1-3 completas + 8 APF adaptados). Falta verificación en TD y correr `builders/setup_all.py` para armar todo.

---

## Rutas (verificar en esta máquina)

- Proyecto .toe: `H:/Mi unidad/01. FREELANCE/2026/38. PETITE AMIE/01. EDITABLES/`
- Shaders de efectos:  `effects_glsl/shaders/`
- Shaders de visuales: `visuals_glsl/shaders/`
- Builders:            `builders/`
- Audio canónico (CHOPs del `audio_in`): `../../project1/null4` (canales: `low mid high`)
- Brief de origen: `PETITE_AMIE_build.md`
- Set APF fuente: `H:/Mi unidad/01. FREELANCE/2026/27. APF/feedback_filters/`

## Rig (fijo — no renombrar bases)

- Visuales:  `base1`–`base8` (base9–base16 libres)
- `base17`:  host de cámaras / `escena_modular` / layouts
- Efectos:   `base18`–`base24`, luego `base38`–`base45`
- GLSL output resolution en efectos: **Use Input** (heredan tamaño del switch de base17)
- GLSL output resolution en visuales: leído de `escena_modular` `ResW`/`ResH`
- **Cámara del show: switcher externo → una sola señal (program) en `base17/switch1`.** No se construyen layouts CCTV.

## Bases ocupadas en este show

### Efectos de cámara (todos con feedback)

| Base | Nombre | Shader | Notas |
|------|--------|--------|-------|
| base18 | nucleo_frio | `effects_glsl/shaders/nucleo_frio.frag` | **look base** — cara limpia al centro, feedback en bordes |
| base19 | soft_halate | `effects_glsl/shaders/soft_halate.frag` | **look base** — halación de película, aura cálida |
| base20 | eco_lento | `effects_glsl/shaders/eco_lento.frag` | Estela larga con luma gate — sólo lo brillante deja cola |
| base21 | dos_voces | `effects_glsl/shaders/dos_voces.frag` | Dos capas de feedback con decay distinto y tinte propio |
| base22 | anamorph_ghost | `effects_glsl/shaders/anamorph_ghost.frag` | Fantasma horizontal estirado con box blur |
| base23 | retrato_focal | `effects_glsl/shaders/retrato_focal.frag` | Nítido al centro, acuarela desaturada en periferia |
| base24 | breath_zoom | `effects_glsl/shaders/breath_zoom.frag` | **el audio-reactivo del set** — túnel que respira con el bajo |
| base38 | liquid_memory | `effects_glsl/shaders/liquid_memory.frag` | **APF 03** verbatim — deformación por isolíneas de luma |
| base39 | memory_marbling | `effects_glsl/shaders/memory_marbling.frag` | **APF 07** verbatim — mármol, warping recursivo |
| base40 | rgb_trail_decay | `effects_glsl/shaders/rgb_trail_decay.frag` | **APF 02** verbatim — decay independiente por canal (post-hook para vec2 offsets) |
| base41 | liquid_light_show | `effects_glsl/shaders/liquid_light_show.frag` | **APF 08 EXTENDIDO** — se añadieron uMix, uHueDrift, uOffsetScale para llenar los 5 slots |
| base42 | echo_fractal | `effects_glsl/shaders/echo_fractal.frag` | **APF 04** verbatim — espiral cromática content-driven |
| base43 | crt_edge_bleed | `effects_glsl/shaders/crt_edge_bleed.frag` | **APF 09 EXTENDIDO** — se añadieron uMix, uThreshold, uGain, uPhosphorDecay |
| base44 | plasma_currents | `effects_glsl/shaders/plasma_currents.frag` | **APF 05** verbatim — filamentos plasma solar (acento breve) |
| base45 | spectral_mitosis | `effects_glsl/shaders/spectral_mitosis.frag` | **APF 06** verbatim — mitosis cromática sólo en bordes (acento breve) |

### Visuales generativos puros

| Base | Nombre | Shader | Paleta |
|------|--------|--------|--------|
| base1 | grano_degradado | `visuals_glsl/shaders/grano_degradado.glsl` | crema · rosa · violeta |
| base2 | liquid_light | `visuals_glsl/shaders/liquid_light.glsl` | ámbar · turquesa · rosa |
| base3 | niebla_capas | `visuals_glsl/shaders/niebla_capas.glsl` | negro violáceo · violeta · crema |
| base4 | humo_tinta | `visuals_glsl/shaders/humo_tinta.glsl` | violeta · turquesa · crema |
| base5 | campo_bokeh | `visuals_glsl/shaders/campo_bokeh.glsl` | ámbar · rosa · crema |
| base6 | mareas_color | `visuals_glsl/shaders/mareas_color.glsl` | turquesa · ámbar · rosa |
| base7 | eclipse | `visuals_glsl/shaders/eclipse.glsl` | ámbar · negro violáceo · rosa |
| base8 | cuerdas | `visuals_glsl/shaders/cuerdas.glsl` | crema · violeta · turquesa |

**Descartado del brief:** `base38 cortina_franjas` (reemplazado por set APF por decisión de show).

## Notas sobre los APF extendidos

`base41 liquid_light_show` y `base43 crt_edge_bleed` originalmente tenían sólo 1–2 uniforms expuestos (el resto eran literales hardcoded como `0.97`, `0.92`, `0.4`, `1.05`). Para no colapsar 4 knobs MIDI al mismo control se **extendió el shader** reemplazando literales por uniforms nuevos:

- `liquid_light_show`: añadidos `uMix` (reemplaza `0.97`), `uOffsetScale` (reemplaza `0.003`), `uHueDrift` (nuevo — hue shift del feedback)
- `crt_edge_bleed`: añadidos `uMix` (reemplaza `0.92`), `uThreshold` (reemplaza `0.4`/`0.8`), `uGain` (reemplaza `1.05`), `uPhosphorDecay` (nuevo — decay del trail fosfórico)

Los otros 6 APF (`liquid_memory`, `memory_marbling`, `rgb_trail_decay`, `echo_fractal`, `plasma_currents`, `spectral_mitosis`) son copia verbatim del set original.

**base40 rgb_trail_decay** usa `uOffsetR/G/B` como `vec2` en el shader; el slot 3 MIDI expone sólo la componente X (`Offsetrx`, típico chroma-split horizontal). Los `_post_hook_rgb_trail_vec2_fix` bindea Y=0 en las 3 vec2 para que no quede indefinida.

## Contrato de parámetros (recordatorio)

- 5 sliders por rol: **intensidad, velocidad, distorsión, color, firma**.
- `Bypass` aparte. Página `Audio`: `Audioreact` + `Low`/`Mid`/`High` (suman) + `Audiotarget` (menú a 1 de los 5) + `Audiomult` (0–3).
- Energía de audio se suma en la **expresión** del uniform (con clamp al rango real), no en el slider — el slider queda libre para MIDI.
- Todos los efectos usan Pixel Format **16-bit float (RGBA)** en el GLSL TOP **y** el Feedback TOP (obligatorio con 16 loops vivos).
- Extend U/V = **Mirror** en el GLSL TOP de cualquier efecto con zoom/displacement acumulativo.

## Convenciones de shader

- Efectos (`base18–24`, `base38–45`): **camelCase**. `uTime`, `uResolution`, input 0 = cámara (`sTD2DInputs[0]`), input 1 = feedback (`sTD2DInputs[1]`).
- Visuales (`base1–16`): **snake_case**. `u_time`, `u_res`, `u_bass`, `u_color1/2/3`. Generativos puros (sin `u_input`).
- Nunca redeclarar lo que TD inyecta: `in vec3 vUV;`, `sTD2DInputs[]`, `uTDOutputInfo`.
- Nunca `uniform sampler2D` para entradas de TD.
- Salida: `fragColor = TDOutputSwizzle(vec4(color, 1.0));`
- Sin dynamic array indexing (cadenas `if/else if` para floats-como-int).

## Cómo correr los builders

### ⚠ IMPORTANTE — leer antes de correr

Este `.toe` partió del proyecto de **Paloma Murphy**. `base1` y `base2` contenían nodos huérfanos (`glsl_marquee_frame`, `glsl_atomic_starburst`, `audio_util`) con expresiones que referenciaban Custom Parameters ya borrados → cascada de `td.ParCollection has no attribute X`. Ver `PETITE_AMIE_fix_bases.md` para el diagnóstico completo.

**Fix aplicado en el código:**
- `setup_all.py`: `build_visual` hace `full_clean=True` por default (destruye TODOS los children, no sólo la lista managed). `build_effect` mantiene `full_clean=False` porque las bases de efectos están limpias.
- `setup_base01_*.py` y `setup_base02_*.py` (backups individuales): también hacen full clean.
- Alternativa nuclear: `builders/clean_bases.py` vacía base1–8 desde cero.

### Opción A — Armar todo de un jalón (recomendado)

```python
exec(open(r'H:/Mi unidad/01. FREELANCE/2026/38. PETITE AMIE/01. EDITABLES/builders/setup_all.py').read())
```

Corre los 23 items en secuencia. Idempotente. Los visuales se limpian a fondo antes de reconstruir, los efectos sólo destruyen su lista managed. Si una base no existe imprime `[skip]` y sigue. Al final imprime resumen con `ok`/`skipped`/`errores`.

### Opción B — Limpieza nuclear primero, luego build

Si prefieres separar los dos pasos:

```python
exec(open(r'H:/Mi unidad/01. FREELANCE/2026/38. PETITE AMIE/01. EDITABLES/builders/clean_bases.py').read())
# verificar en TD que base1–8 están vacías (sin children, sin custom pars)
exec(open(r'H:/Mi unidad/01. FREELANCE/2026/38. PETITE AMIE/01. EDITABLES/builders/setup_all.py').read())
```

### Opción C — Un builder individual (para debugging)

Los 4 builders individuales de Tanda 1 (`setup_base01_*`, `setup_base02_*`, `setup_base18_*`, `setup_base19_*`) siguen disponibles. Cargar en un Text DAT dentro del `baseXX` → Run Script. Los de base1/base2 hacen full clean; los de base18/base19 sólo destruyen la lista managed.

**Todos los builders son idempotentes** y **NUNCA renombran el `baseX`.**

### Checklist post-build (por base)

- [ ] `base.children` sólo contiene nodos del builder de Petite Amie (no queda `glsl_marquee_frame`, `glsl_atomic_starburst`, `audio_util`)
- [ ] Cero `ParCollection has no attribute` en el TextPort
- [ ] GLSL compila y muestra imagen
- [ ] Las páginas custom son las del contrato (`Visual`/`Filter` con 5 sliders + Bypass, y `Audio`)

## Checklist por base construida (§12 del brief)

- [ ] El GLSL TOP compila sin errores en el TextPort
- [ ] Cero warnings de tipo `Uniform 'X' is not assigned`
- [ ] Pixel format = 16-bit float en GLSL TOP **y** Feedback TOP (efectos)
- [ ] `Bypass` corta a passthrough limpio
- [ ] Los 5 sliders mueven algo visible en todo su rango
- [ ] `Audiotarget` empuja el slider correcto y `Audiomult=0` lo desactiva
- [ ] Con el fader de intensidad al máximo, las caras siguen reconocibles (efectos)
- [ ] El feedback no satura a blanco tras 5 minutos corriendo
- [ ] `bgtop = ./out1` en la pestaña Look del contenedor

## Performance — nota crítica del brief

16 loops de feedback simultáneos cuestan mucho más que 16 shaders normales. **Verificar el cooking de las bases inactivas y apagarlo donde se pueda.**

## Notas del show

<!-- Sección libre — el skill NO borra esto en actualizaciones. Anotar aquí:
     bugs vistos en TD, rangos que se sintieron bien en vivo, cambios sobre
     los defaults del brief, mapeos MIDI concretos, sorpresas, etc. -->

- 
