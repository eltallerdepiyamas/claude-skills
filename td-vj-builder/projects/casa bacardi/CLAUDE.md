# CASA BACARDI X CORONA CAPITAL — visuales TouchDesigner

Creado el 2026-11-06 desde td-vj-builder (255a968). Esta carpeta = `project.folder`.

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

## Este show
Casa Bacardi x Corona Capital. **Solo visuales generativos en `base1-16`:** sin camaras, CCTV, FX ni YOLO.
- `proyecto.json`: `modulos.fx` y `modulos.escena_modular` = false. `base27-32` quedan vacias.
- Paleta (`00. ASSETS/260319-BCD-PANTONES-CASA.pdf`): fondo negro + rojo (185 C) o turquesa (346 C, #6DC49A). El color principal lo define el cliente. No usar otros colores. Brief de referencia: `research/research_casa_bacardi_2026.md`.
- Sin brief propio: la casa se adapta al festival; misma linea que las ediciones anteriores. Salida 1920x1080 por ahora.
- Tono: festivo y premium; evitar caleidoscopio, tunel, arcoiris y strobe agresivo.
- `research/referencia_bacardi/`: shaders de ediciones anteriores, solo de referencia. Eran efectos sobre camara; no correrlos tal cual.
- Pendiente: color principal y lista de visuales.

## Visuales
Los visuales nuevos respetan la forma circular del sello (`assets/logo_murcielago.png`) y sus bandas concentricas; pedido expreso del cliente para Tunel Circular.
Canal 10 = puros visuales, canal 11 = puros logos. Cada pestana de thumbs es un canal completo (CH10 VISUALES, CH11 LOGOS), con los 16 pads en 8x2 y siempre abajo del preview de su columna, nunca de lado. Fuente unica: `BANCOS` en `builders/herramientas/ui_bancos.py`; de ahi salen `table1`, thumbs, luces y `control/bancos.json` para el Stream Deck (setup_ui.py lo corre al final). Comprobar con `probar_pads_bancos.py`.

No hay FX: todo entra a `switch2` (entrada N = fila N de `table1`); `switch23` no recibe visuales y no llega a la salida.

Regla: si usa logo va en canal 11; canal 10 es sin logo.

Canal 9 (OTROS, no circulares): Ron Liquido (base9, v2 con causticas de Cristal; v1 en `ron_liquido_v1.glsl`), Pulso Neon, Code Rain, Industrial, Barcode, Bandas, Grille Bocina, Orbitas, Dot Matrix, y 9-10 a 9-16 (2026-11-15, linea MUTEK/Sonar): Cordillera (base43, ridgeline con historia de audio), Laser (base44, haces en humo; kick cambia figura), Seda (base45, curl noise + feedback), Reaccion (base46, Gray-Scott 6 pasos/cuadro), Slit Scan (base47, Texture 3D + Time Machine), Cortinas (base48), Pixel Sort (base49). Bases nuevas: `crear_bases_ch9.py`; todo junto: `build_ch9.py` y luego `registrar_ch9.py` (pads, UI, paleta, thumbs). Pad 9-16 usa la cadena `constant_pad50/logic_pad50/chopexec_pad50` (fila 50 de table1).
Redes con shader propio (`red` en base43/46/47): el texto del shader se carga directo, sin syncfile (TD reescribia el archivo con BOM). Para tomar un cambio de shader de red: `rehacer_redes_ch9.py`. Uniforms de red siempre con `tdvj_core.bind_vectors` (asignar vecN a mano dejaba el default 1,1,1,1).
Canal 10 (CIRCULARES): ver `BANCOS` en `ui_bancos.py`.

Canal 11: Murcielago, Vortice, Time Glitch, Disolucion, Sello Giratorio, Onda Circular, Tunel Circular, Halftone, Eclipse, Moneda Glitch; 11-16 libres. Fuera: Datamosh, Scan Glitch, Fractura.

Logo sin texto: `assets/logo_murcielago.png`. Las redes (`red`) no se rehacen si ya existen, asi se conservan los cambios a mano; para rehacer una, borrar su COMP `red`.

`Tono` (knob 4): 0 rojo, 1 turquesa. Referencias generativas en `CASA BACARDI PAL NORTE V2.36.toe`: vortice, liquid_time, osciloscopio, ondas_oficiales, tunel_infinito_marca, SMOOTHWAVES, circulo_radar, bg_noise, bg_scanlines. Color: pestana Paleta de `show` (Color A, Color B, Rampa) manda sobre todos los visuales; despues de `build_all.py` correr `paleta_show.py` (o `armar.py`). Turquesa por default mas azul que el 346 C por pedido de Sebas. Decision: FX integrado en cada visual, no bases de FX.

Base4: `.tox` en `assets/tox_pal_norte/` + `_lib/pal_norte.py` + `post_pal_norte.glsl`. Mezcla: 1 paleta, 0 colores originales.

Ondas, Tunel y Smoothwaves salieron: no eran audioreactivos; builders en `builders/_referencia/`, solo como referencia.

**Regla al traer visuales de otros proyectos:** detectar el parametro que mas distingue la red y ponerlo en el slot 5; lo demas que valga la pena va como extra. Todos los parametros de mas de 5 se muestran en la UI.

Burbujas y Anillos no gustaron (builders en `_referencia`). El estilo buscado es el de Pal Norte: redes de nodos con feedback, logo y marca; no shaders geometricos genericos.

Boton RESET FEEDBACK (barra superior de la UI): reinicia todos los Feedback TOP de /project1 y /project2, tambien los nuevos, porque los busca al pulsarlo.

Direccion pedida para los visuales que faltan: feedback, time glitch y distorsion digital, propositivos. Vortice 1, 2 y 3 eran variantes de Vortice: fuera.

Stream Deck: se acomoda a `proyecto.json`. Sin escena_modular: paginas VISUALES y LOGOS (`control/bancos.json`), y MENU con COLOR A/B, RESET FEEDBACK, ACTUALIZAR THUMBS y ABRIR UI; sin MULTIVIEW, SINGLE CAM ni CAMARAS.

## Para retomar (2026-11-06)
- Los visuales de los canales 10 y 11 ya existen. Falta verlos con musica y ajustar.
- Cinta Feedback satura casi toda la pantalla (brillo 0.88); Plasma Tiempo sale muy oscuro (0.04). Revisar Lineas Rotas, Vortice (pixelado) y Time Glitch.
- Pendiente: exponer los parametros de los UberRamp del Generador siguiendo la subescena activa; hoy solo hay Escena, Auto y Mezcla.
- Stream Deck: ABRIR UI (`/td/ui`) abre `/perform` como ventana aparte. Hoy el principal es el + XL.
- Pendiente: confirmar luces del Beatstep, importar Companion, color principal con el cliente.

## Stream Deck + XL (2026-11-15)
- `python control/gen_companion_xl.py` -> importar `control/streamdeck_xl.companionconfig`. Una pagina por canal (CH9 / CH10 / CH11): 16 pads 8x2, filas fijas (COLOR A/B, AUDIO, SENS, RESET, RESET FEEDBACK · BLACKOUT, MODO SHOW, ABRIR UI, THUMBS, BEATSTEP, DEMO, REC), pestanas a la derecha. Perillas 1-5 = los 5 parametros del visual al aire; perilla 6 = Reaccion global del audio.
- Lado TD ya instalado (`builders/herramientas/instalar_xl.py` corre `control/instalar_xl_osc.py` con APPLY): `/td/xl/...` en `oscin1_callbacks.py`, `show/xl_feedback` y la marca `streamdeck_xl` (mix_feedback ya no "presiona" la tecla 1/1/0, que en el XL es un pad).
- El de 15 teclas (`gen_companion.py`) sigue como respaldo; ya ve OTROS / CIRCULARES / LOGOS.

## Traido de LJ Metropolitan (2026-11-15) · `builders/herramientas/aplicar_lj.py`
- BLACKOUT con fundido de 0.8 s (bajo el preview de SHOW), MODO SHOW (candado, barra superior), chip de FPS (verde -> rojo), pestana AUDIO EN VIVO (Autonivel · Reaccion · Suavizado: `setup_audio_global.py`), textos de la UI que nunca se cortan, clics de pestanas ocultas ignorados, reset MIDI ch1n26 por base real, BOM en callbacks, `/perform` a resolucion nativa (`ajustar_ventana_perform.py`).
- No se trajo lo de camaras, setlist, titulos, test de pantallas ni salida LED: este show no lo usa.
- Luces del Beatstep: en LJ se retiraron porque no funcionaron en el aparato; probar antes de invertir tiempo.

## Nivel de los visuales
- `research/referentes_contemporaneos.md` (MUTEK, Sonar+D, CTM...): cada visual nuevo se revisa contra sus 8 puntos.
