# EYESY → TouchDesigner: convenciones de traducción

Referencia para generar modes EYESY como visuales GLSL en el rig (base1–16).
Leer junto con SKILL.md; esto NO reemplaza el contrato de 5 sliders, lo especializa.

## Infraestructura compartida

`/project2/EYESY_AUDIO` (construido por `setup_eyesy_audio.py`, una sola vez):

| Salida | Qué es | Equivalente EYESY |
|---|---|---|
| `waveform_out` (TOP 100x1, 32f) | audio crudo resampleado a 100 muestras/frame | `etc.audio_in[0..99]` |
| `trig_out` canal `peak` | pico absoluto del frame | `etc.audio_peak` |
| `trig_out` canal `trigcount` | contador que incrementa en cada trigger | base para `etc.audio_trig` |

El usuario cablea su audio crudo a `EYESY_AUDIO/in_audio` manualmente (su patrón habitual).
`Gain` y `Trigthresh` son custom pars del contenedor.

## Mapeo del API EYESY

| EYESY | En el rig |
|---|---|
| `etc.audio_in[i]` | `texture(sTD2DInputs[0], vec2((i+0.5)/100.0, 0.5)).r` → ±1 normalizado. El waveform SIEMPRE es input 0 del GLSL TOP vía Select TOP `waveform`. Los divisores originales (`/35`, `/100`, `0.00003058`) ya normalizaban a ±1: en GLSL se sustituyen por `audN(i) * amp_en_px`. |
| `etc.knob1..5` | Los 5 sliders del contrato, reordenados por ROL, no por número. El mapeo real knob→slot se documenta en comentario del shader. |
| `etc.color_picker(k)` | Paleta procedural de 8 zonas (`eyesyPal`) fiel a los bloques `sel = knob4*8` de los modes originales. Slot 4 = Colorsel. |
| `etc.color_picker_bg(k)` | `bgPicker(k)`: 0=negro, sube por matiz. Par extra `Bgsel`. |
| `etc.audio_trig` | Familias de trigger: bind `uSeed` ← canal `trigcount` de `trig_out`. En el shader, `hash(uSeed)` re-genera posiciones random. Estado sin feedback: el shader es puro, el contador ES el estado. |
| `time.time()` | `u_time * (0.25 + 2.0*u_speed)` — el ciclo de color/LFO va al slot Speed. |
| `etc.xres/yres` | `u_res` ← `me.width/me.height`. Resolución del GLSL TOP en custom, ligada a ResW/ResH de escena_modular. |
| LFO class (triángulo) | `abs(fract(t*rate)*2.0-1.0)` en GLSL. |
| Feedback (`last_screen`) | NO se implementa dentro del mode — el usuario cuelga su propio feedback aparte. |

## Contrato de slots para familias EYESY

1. **Amplitude** — escala de la onda / tamaño de elementos (intensidad)
2. **Speed** — ciclo de color + rate de LFOs (los modes EYESY rara vez tienen anim temporal propia; se comenta la adaptación)
3. **Offset/Spread** — deformación espacial (línea base, ancla, espaciado)
4. **Colorsel** — paleta 8 zonas
5. **Variant** — SIGNATURE: selector de variante dentro de la familia (equivale a los `sel` internos de EYESY; float 0..N-1, `int(clamp(...))` en shader)

Extras permitidos fuera de los 5 (no MIDI): `Thickness`, `Shadow`, `Bgsel`, etc.
Página Audio: contrato estándar del skill (Audioreact/Low/Mid/High/Audiotarget/Audiomult).

## Reglas de rendimiento

- Loops de segmentos ≤ 50 iteraciones, 1 fetch por iteración (textura 100x1 = cache-friendly).
- Variantes por `if/else` sobre `int(u_variant)` — nunca indexado dinámico de arrays.
- AA con `smoothstep(th, th+1.5px)`; grosores en px relativos a 1080 (`px = u_res.y/1080`).

## Nombres de archivo

- Builders: `setup_baseN_eyesy_<familia>.py` en la raíz del proyecto
- Shaders EN DISCO (fuente de verdad): `<proyecto>\shaders\baseXX_<familia>\baseXX_<familia>.frag`.
  El builder liga el Text DAT al archivo (par file + syncfile) y referencia pixeldat
  por OPERADOR, no por string de ruta (evita "Invalid path ./glsl_code").
- Al validar en show → copiar el .frag a `library/` del skill
