# {{PROYECTO}} — visuales TouchDesigner

Creado el {{FECHA}} desde td-vj-builder ({{VERSION}}). Esta carpeta = `project.folder`.

## Arranque
1. Llenar `proyecto.json` (resolucion, paleta, camaras).
2. Abrir el `.toe`.
3. Correr `armar.py` (por MCP o Textport) y despues `python control/gen_companion.py` (o `gen_companion_xl.py` para el Stream Deck + XL).
4. Visual: `builders/visuales/`. FX: `builders/efectos/`. Escena: `builders/layouts/`. Reconstruir con `builders/build_all.py`.

## Rig
- Visuales `base1-16` -> `switch2` -> `master_visuales`.
- `base17` = escena limpia; FX `base18-32` -> `switch23` -> `master_fx`.
- `/project1`: `select47`, `select2` -> FX globales -> `color_final` -> `ndiout1`.
- Hub `/project2/show`: color, audio (siempre mono) y resolucion.
- Salidas: `master_<que manda>`. Acomodo: de arriba a abajo, una fila por cadena.
- **Acomodo de la red (regla del usuario):** por tipo de nodo y facil de ubicar al entrar. Todo lo que no es visual (MIDI, tablas, audio, hub, UI, control) va ARRIBA. Lo vertical es solo para los visuales (y FX si hay): bajan una fila por base, con su cadena de pad constant -> logic -> chopexec a la izquierda en la misma fila. Nada encimado. **Siempre con recuadros de titulo** (annotate `zona_*`) alrededor de cada grupo: `builders/herramientas/recuadros_project2.py` los dibuja sin mover nodos (acomodar_pads.py lo corre al final); si aparece un nodo sin grupo, agregarlo a `GRUPOS`. Visual nuevo: `builders/herramientas/acomodar_pads.py` lo pone en su fila. NO usar `ordenar_project2.py` para todo /project2.
- Bases vacias sin cook; `build_visual` / `build_effect` las prenden. Pads sin contenido no hacen nada.
- 5 sliders: intensidad · velocidad · distorsion · color · firma, + pagina Audio.
- Shaders de escena: usar `uPhase`; el color sale de la paleta, nunca hue ni RGB.
- En la UI se dice ESCENA; "layout" es termino interno.

## Control
- MIDI en `/project2/midi_*`; Beatstep canal 9 escenas, 10 y 11 visuales y FX. Convencion: pads de arriba (n45-52) = visuales, pads de abajo (n37-44) = FX; CH10 cubre 1-8, CH11 cubre 9-16. Si un show necesita mas, se extiende hacia arriba (CH12, CH13, ...) con la misma estructura, nunca abajo del 9.
- Luces del Beatstep: ya no forman parte de los shows (no funcionaron). `control/quitar_beatstep_luces.py` las quita; armar.py lo corre.
- Companion: `python control/gen_companion.py` e importar `control/streamdeck.companionconfig`.
- Al traer un visual de otro proyecto: `_lib/pal_norte.py` monta su `.tox`; el parametro que mas lo distingue va al slot 5 y lo que valga la pena como extra. Todo lo que pase de 5 aparece en la UI.
- Barra de la UI: ACTUALIZAR THUMBS y RESET FEEDBACK (encuentra los Feedback nuevos solo).
- Show sin camaras ni FX: `modulos.escena_modular` y `fx` en false; `armar.py` deja solo visuales con pestana Paleta.
- Hub `/project2/show`, pestanas (orden: `setup_orden_pestanas.py`): Dispositivos · Resolucion · Audio · LUT · MIDI · Ensayo · Pantallas · Correccion de color. La UI muestra todas las que existan.
- Resolucion: todo sigue a `show` -> Resolucion (W / H), tambien en vertical. `auditar_resolucion.py` dice que no la sigue; `aplicar_resolucion.py` lo liga. Un TOP con tamano propio a proposito lleva el tag `res_propia`.
- Pantallas (`setup_test_pantallas.py`): patrones de prueba antes de `ndiout1`; boton PANTALLAS y ABRIR UI en el Stream Deck.
- MIDI por nombre (`setup_midi_devices.py`): `midi_midiin1` = MIDI Mix, `midi_midiin2` = BeatStep, aunque TD los detecte en otro orden.
- Al correr el builder de una base, la UI de perform se rehace sola (thumb nuevo incluido). VISUAL y FX muestran todas sus filas; solo ESCENA se pagina.

## Agregado 2026-11-15 (de Casa Bacardi y LJ Metropolitan)
- Stream Deck + XL: `python control/gen_companion_xl.py` (una pagina por canal del Beatstep, de `control/bancos.json`) e importar `control/streamdeck_xl.companionconfig`. En TD, una vez: `control/instalar_xl_osc.py` con `APPLY = True` (perillas, blackout, modo show, reaccion). Shows con camaras: `gen_companion_xl_camaras.py`.
- Pads y bancos: `BANCOS` en `builders/herramientas/ui_bancos.py` (vacio en la plantilla = no toca nada). De ahi salen `table1`, thumbs por canal y `control/bancos.json`. Comprobar con `probar_pads_bancos.py`.
- MODO SHOW (`setup_modo_show.py`): candado de resolucion, fuente de audio, demo, dispositivos y pantallas; boton en la barra de la UI y PARAMETROS EXTRAS para los ajustes del soundcheck.
- BLACKOUT: boton en SHOW, fundido de 0.8 s a negro; otro toque regresa. El candado nunca lo bloquea.
- Audio global (`setup_audio_global.py`, hub -> Audio): Autonivel, Reaccion y Suavizado para todo a la vez; pestana AUDIO EN VIVO en SHOW.
- Barra de la UI: chip de FPS (verde -> rojo), titulo de SHOW con estado NDI, aviso SIN SENAL por camara. Un texto de la UI nunca se corta: baja la letra y parte renglones.
- UI cortada en Perform (Windows al 125 %, 150 %): `ajustar_ventana_perform.py` (lo corre `armar.py`).
- Redes (`red`): sus shaders se cargan con el texto directo, sin syncfile (TD reescribe el archivo con BOM). Uniforms solo con `tdvj_core.bind_vectors`; poner vecN a mano dejaba los defaults 1,1,1,1.
- Camaras (LJ): `setup_devices_camaras.py` fija cada camara a su puerto USB y agrega Hay camara (`Hay1-6`); UI y Stream Deck solo muestran las que existen. Opcionales: `setup_lut_camaras.py`, `setup_feedback_salto.py`, `setup_salida_led.py`, `prueba_preshow.py` (un dia antes del show).
- Interior de cada base: `_lib/acomodo.py` lo acomoda solo al construir (bloques por tipo de nodo).
- Referencias: los visuales tienen que estar al nivel de festivales actuales (MUTEK, Sónar+D, CTM, Unsound, Ars Electronica, Decibel): ver research/referentes_contemporaneos.md; cada show suma sus referencias propias en research/.

## Audio siempre al cien (regla)
- El audio tiene que llegar a todos los visuales siempre. Al abrir un show, antes de ensayar y antes del show: `builders/herramientas/revisar_audio.py` (fuente -> audioAnalysis -> master_audio -> Energy; dice donde se corta).
- `audio_vigia` (`setup_vigia_audio.py`, lo instala armar.py) despierta `audioAnalysis` cuando su cadena interna se queda sin canales (Energy en 0 en todo, salidas con float(None)).
- Audio nuevo en un show (VST, otra fuente): no sale del ensayo si `revisar_audio.py` no dice `[ok] audio al cien`. Un VST que no carga (p.ej. neutone.vst3) va en bypass.

## Show sin operador y logo (2026-11-16, de Casa Bacardi x Corona Capital)
- Show que corre solo: `setup_piloto.py` (armar.py) = PILOTO AUTOMATICO (pestana PILOTO y chip AUTO en la UI; paginas Piloto y Vigia de `show`; apagado por default) + VIGIA DE VIDEO (por pico de brillo; reinicia feedback, luego salta). Los canales siguen siendo grupos de 16 pads aunque no haya Beatstep.
- Antes de un show sin operador: `revisar_visuales.py` (todos los pads, con musica) y una noche con `noche.py` (soak test: `control/soak_log.csv`, `control/piloto_log.txt`).
- Logo: `show.Logotamano` (pagina Logo; perilla 6 del XL en la pagina LOGOS) = mismo tamano en todos los visuales de logo; `base.Tamano` = ajuste fino. `logo_tamano.py` (armar.py) y `calibrar_logos.py`. Shaders de logo nuevos: `uniform float u_tamano`, sello con `c / u_tamano`. Pedir el sello en vector o PNG 4096.
- Referencias para construir: `research/recetario_tecnicas.md` (perfiles + 44 recetas, sintesis de video / LZX incluida).

