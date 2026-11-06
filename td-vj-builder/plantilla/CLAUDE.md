# {{PROYECTO}} — visuales TouchDesigner

Creado el {{FECHA}} desde td-vj-builder ({{VERSION}}). Esta carpeta = `project.folder`.

## Arranque
1. Llenar `proyecto.json` (resolucion, paleta, camaras).
2. Abrir el `.toe`.
3. Correr `armar.py` (por MCP o Textport) y despues `python control/gen_companion.py`.
4. Visual: `builders/visuales/`. FX: `builders/efectos/`. Escena: `builders/layouts/`. Reconstruir con `builders/build_all.py`.

## Rig
- Visuales `base1-16` -> `switch2` -> `master_visuales`.
- `base17` = escena limpia; FX `base18-32` -> `switch23` -> `master_fx`.
- `/project1`: `select47`, `select2` -> FX globales -> `color_final` -> `ndiout1`.
- Hub `/project2/show`: color, audio (siempre mono) y resolucion.
- Salidas: `master_<que manda>`. Acomodo: de arriba a abajo, una fila por cadena.
- Bases vacias sin cook; `build_visual` / `build_effect` las prenden. Pads sin contenido no hacen nada.
- 5 sliders: intensidad · velocidad · distorsion · color · firma, + pagina Audio.
- Shaders de escena: usar `uPhase`; el color sale de la paleta, nunca hue ni RGB.
- En la UI se dice ESCENA; "layout" es termino interno.

## Control
- MIDI en `/project2/midi_*`; Beatstep canal 9 escenas, 10 y 11 visuales y FX.
- Luces de pads: Out Device del Beatstep en el MIDI Mapper.
- Companion: `python control/gen_companion.py` e importar `control/streamdeck.companionconfig`.
- Al traer un visual de otro proyecto: `_lib/pal_norte.py` monta su `.tox`; el parametro que mas lo distingue va al slot 5 y lo que valga la pena como extra. Todo lo que pase de 5 aparece en la UI.
- Barra de la UI: ACTUALIZAR THUMBS y RESET FEEDBACK (encuentra los Feedback nuevos solo).
- Show sin camaras ni FX: `modulos.escena_modular` y `fx` en false; `armar.py` deja solo visuales con pestana Paleta.
