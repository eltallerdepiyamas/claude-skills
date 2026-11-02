# {{PROYECTO}} — Visuales en tiempo real

Contexto de trabajo del show para la skill `td-vj-builder`. Esta carpeta = `project.folder` (guarda aquí el `.toe`).
Creado desde el boilerplate {{VERSION}} el {{FECHA}}.

**Alcance:** <!-- fechas, venue, pantallas, qué va en cada una -->
**Brief:** `research/` (generado con `references/research-prompt.md` de la skill).
**Gustos / no:** <!-- lo que el usuario pidió evitar -->

## Estructura

```
01. EDITABLES/
├── <show>.toe
├── CLAUDE.md                    ← este archivo
├── _lib/tdvj_core.py            ← núcleo (contrato, audio, resolución, grafo, uniforms) — NO editar por show
├── _lib/rig.py                  ← lo propio del show: rangos de bases, CHOP de audio, cámaras
├── _templates/                  ← setup_baseXX_visual.py + visual.frag de ejemplo
├── shaders/visuales/ · shaders/efectos/
├── builders/build_all.py        ← corre todos los builders
├── builders/visuales/ · builders/efectos/   ← setup_baseXX_<nombre>.py
├── builders/herramientas/       ← limpiar_bases.py · aplicar_resolucion.py (+ salidas/previz del show)
├── control/                     ← Stream Deck (Companion) + MIDI: ver "Control en vivo"
├── research/ · media/ · exports/
```

## Rig (no negociable)

- Visuales `base1`–`16` (página `Visual`) · `base17` = fuente limpia (cámaras) · Efectos `base18`–`24` y `base38`–`45` (página `Filter`).
  Nunca renombrar/mover/destruir un baseX. Rangos en `_lib/rig.py`.
- 5 sliders en orden de rol: **1 intensidad · 2 velocidad · 3 distorsión · 4 color · 5 firma** + `Bypass` aparte.
- Página `Audio` en TODAS las bases: Audioreact · Low/Mid/High · Audiotarget · Audiomult · Smooth · Audio CHOP · Energy.
- Página `Salida`: Resw/Resh por base.

## Control en vivo (`control/`)

| Controlador | Rol |
|---|---|
| **Stream Deck** (Companion) | **elegir**: visual, FX, escena, cámara. Botones que se quedan encendidos. |
| **MIDImix** | **continuo**: fila de arriba knobs 1–5 = visual activo · fila de abajo knobs 1–5 = FX activo · sección de color · faders. |
| **Beatstep Pro** (respaldo) | pads: canal 10 = visuales 1–8 (arriba) y FX 17–24 (abajo) · canal 11 = visuales 9–16 y FX 38–45. |

- Companion → OSC `127.0.0.1:7010` → OSC In DAT (`control/oscin1_callbacks.py`). El 7000 lo usa Resolume.
- TD → Companion OSC `127.0.0.1:12320` (`control/setup_companion_feedback.py`): activar OSC en Companion (asistente → Services).
- Botones del Stream Deck: `python control/gen_companion.py` → importar `control/streamdeck.companionconfig`.

## Bases ocupadas

| Base | Nombre | Shader / origen | Firma | Estado |
|---|---|---|---|---|

## Pendientes

## Notas del show

<!-- Tuyo: venue, resolución real, ruta de audio, lo que funcionó en ensayo. La skill no borra esta sección. -->
