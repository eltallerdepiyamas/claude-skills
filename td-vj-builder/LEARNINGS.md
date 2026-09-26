# LEARNINGS — TD VJ Builder

Registro append-only. El skill LEE esto antes de proponer y ESCRIBE aquí al cerrar
cada proyecto. Anota rangos que se sintieron bien, nombres que el usuario conservó,
qué se rompió y cómo se arregló. El usuario aprueba cada escritura.

Formato por entrada:
## YYYY-MM-DD — <proyecto>
- Construido: <visuales / efectos / layouts y sus bases>
- Rangos que funcionaron: ...
- Nombres/convenciones que el usuario conservó o cambió: ...
- Problemas y fixes: ...
- Shaders movidos a library/: ...

---

## (semilla) Convenciones confirmadas con el usuario
- 5 sliders por rol fijo (intensidad, velocidad, distorsión, color, firma); Bypass aparte.
- Página Audio: Audioreact + Low/Mid/High (suman) + Audiotarget (menú a 1 de los 5) + Audiomult 0–3.
- audio_in = un solo Select CHOP, Channel Names = "low mid high", CHOPs = /project2/base17/audio_in.
- Energía de audio se suma en la EXPRESIÓN del uniform (clamp), no en el slider, para no chocar con MIDI.
- Bases: visuales 1→16; efectos 18→24 y 38→45 (respetar el salto); layouts = layout_* en escena_modular.
- NUNCA renombrar un baseX. El midi sampler depende del número de base.

## 2026-06-02 — proyecto de prueba (synth-pop / base18 neon_bleed)
- Problema: GLSL TOP tiró "Uniform 'uTime' / 'uResolution' is not assigned (Vectors page)"
  y el efecto salía plano. Causa: el effect_builder no inyectaba uTime/uResolution,
  solo los 5 macros + extras.
- Fix: el effect_builder ahora asigna SIEMPRE, como primeros uniforms de la pagina
  Vectors: uTime = absTime.seconds ; uResolution = escena_modular ResW/ResH (fallback 1920x1080).
- Regla añadida al SKILL.md: asignar TODOS los uniforms que el shader declare; nunca
  dejar uTime/uResolution sin cablear.
- Pendiente confirmar: si en escena_modular del usuario los params son Resw/Resh o ResW/ResH
  (el builder prueba ambos; al escribir a mano usar el correcto).

## 2026-06-02 — ajustes tras primera prueba en TD (base18)
- audio_in: la ruta CANONICA del rig es ../../project1/null4 (Channel Names = low mid high),
  NO /project2/base17/audio_in. Fijada en los templates.
- GLSL output resolution: default = Use Input (no custom). El efecto hereda el tamano del
  video de entrada; el usuario cambia el tamano en la fuente. uResolution -> me.width/me.height.
- Feedback: ademas de feedback1.Target=glsl y feedback1->input1 del glsl, conectar tambien
  select_video -> input0 del feedback1 automaticamente (el usuario no quiere cablearlo a mano).

## 2026-06-02 — fix ParMode (AttributeError)
- Sintoma: "module 'td' has no attribute 'ParMode'". El build corria pero fallaba
  silenciosamente cada vez que ponia un parametro en modo expresion (uniforms, Bypass).
- Causa: se usaba td.ParMode.EXPRESSION; en TD se accede como ParMode.EXPRESSION (global,
  sin prefijo td.) — como en los scripts originales del usuario que ya funcionaban.
- Fix: reemplazado td.ParMode -> ParMode en los 3 templates; asignaciones sueltas
  envueltas en try/except para que nunca aborten el build.

## 2026-06-02 — fix uniform/parametro desincronizados (base19 pulse_grid)
- Sintoma: "td.ParCollection object has no attribute 'Phosphor'" al cocinar el GLSL.
- Causa: el shader declaraba un uniform mapeado a parent().par.Phosphor, pero ese
  Custom Parameter nunca se creo en el base (shader y lista de params desincronizados).
- Fix preventivo: _bind_uniform ahora valida (con owner/base) que todo parent().par.X
  referenciado exista ANTES de escribir la expresion; si falta, imprime [WARN] con el
  nombre y se salta ese uniform en vez de dejar que TD truene. Aplicado en los 3 templates.
- Regla en SKILL.md: shader y parametros se generan como par sincronizado; tras escribir
  un shader, verificar que cada uniform tenga su Custom Parameter.

## 2026-06-02 — CLAUDE.md por proyecto (automatico)
- El skill ahora escribe/actualiza un CLAUDE.md en la carpeta del show al construir,
  con rutas reales (project.folder), rig, y tabla de bases/layouts ocupados.
- Merge seguro: refresca tablas y fecha, preserva "Notas del show". No confundir con el
  CLAUDE.md de arquitectura del patch (/project2).
- Plantilla en references/project-claude-md-template.md.

## 2026-06-16 — Casa Bacardi (booth interactivo, standalone)
- Proyecto STANDALONE: no /project2, raiz directa con /bacardi_input, /bacardi_audio.
  Video: /bacardi_input/switch_main. Audio: /bacardi_audio/null_audio (low mid high).
- Override de numeracion confirmado por el usuario: base01-base06 para este show
  (no las ranges canonicas 18-24/38-45). Razon: midi sampler interno del booth,
  separado del rig principal. base18 existente queda intacto y coexiste.
  *No aplicar este override a otros proyectos por defecto.* Es decision del show.
- Construido: 6 efectos
  - base01 body_aura  (YOLO bbox de persona)
  - base02 face_kaleido  (YOLO face position)
  - base03 pose_trails  (YOLO wrists + feedback)
  - base04 bacardi_chroma_split
  - base05 neon_edge
  - base06 liquid_metal  (+ feedback)
- Patron YOLO nuevo: agregar un Select CHOP 'yolo_in' por base (apunta a
  /bacardi_input/yolo_plugin con channel names guess). Bindear uniforms via
  expresion `op('yolo_in')['<chan>'].eval() if .chan(...) is not None else <default>`
  para que si el plugin tiene nombres distintos no truene, solo caiga al default.
  El usuario ajusta los nombres en el Rename del Select CHOP.
- Path fallback de los builders: ('/baseXX', '/project1/baseXX', '/project2/baseXX')
  porque el .toe raiz puede ser cualquiera de esos contextos.
- Pendiente confirmar en TD: nombres exactos de canales del yolo_plugin
  (person_x/y/w/h, face_x/y, wrist_l_x/y, wrist_r_x/y). Si el plugin usa otros
  (p.ej. tx0/ty0 o face0:x), el usuario renombra en yolo_in.
- Tints Bacardi usados (defaults rojo/dorado premium):
  - body_aura: (1.0, 0.55, 0.15)
  - face_kaleido: (1.0, 0.7, 0.3)
  - pose_trails: (1.0, 0.6, 0.2)
  - chroma_split: (1.0, 0.55, 0.15)
  - neon_edge: (1.0, 0.5, 0.2)
  - liquid_metal: (1.0, 0.65, 0.2)
- Shaders pendientes de mover a library/ tras prueba en TD.

## 2026-07-15 — Casa Bacardi / base04 rostros_slitscan (GLSL Multi TOP en TD 2023.11600)
- Problema 1 (vertex): el builder inyectaba un vertex pass-through con
  `gl_Position = TDSOPToProj(TDPos());` — en TD 2023.11600 `TDPos()` sin
  argumentos no existe con esa firma y el vertex no compila.
- Fix: dejar el parametro Vertex Shader del `glslmultiTOP` VACIO. TD usa su
  vertex por defecto, que ya emite `vUV` (vec3) interpolado al pixel shader.
  El builder ya no crea `glslmulti1_vertex` pero lo mantiene en la lista
  `managed` para destruir restos de builds anteriores (idempotencia).
- Problema 2 (pixel): el shader declaraba `in vec3 vUV;` explicitamente y
  el compilador tiraba `'vUV' : redefinition`. TD ya inyecta `vUV` en TODOS
  los GLSL TOPs (incluido GLSL Multi TOP).
- Fix: eliminar del pixel shader cualquier `in vec3 vUV;` / `in vec2 vUV;` /
  `varying vec2 vUV;`. Usar `vUV.st` directamente (ya existe).
- **REGLA GENERAL para todos los shaders del skill:**
  En GLSL TOPs de TD, NUNCA redeclarar los identificadores que TD inyecta:
    * `in vec3 vUV;`          <- TD lo inyecta en pixel shader
    * `uniform sampler2D sTD2DInputs[];` <- TD lo inyecta
    * `uniform sampler3D sTD3DInputs[];` <- TD lo inyecta
    * `uniform ... uTDOutputInfo;`       <- TD lo inyecta
  Redeclararlos causa `'redefinition'` al compilar. Solo declarar
  uniforms propios (uTime, uResolution, uColorA, etc.) y el `out vec4 fragColor;`.

## 2026-07-15 — Casa Bacardi / base07 asset_rostro (asset PNG sobre bbox de rostro)
- Nuevo patron util: en vez de pixelar/deformar el rostro (base03/04),
  se puede COMPONER un PNG con alpha encima del rostro usando el bbox
  del CHOP `YOLO_PLUGIN/null7` (canales `x y width height score`).
- No requiere `face_mask` TOP: los uniforms `uFaceX/uFaceY/uFaceW/uFaceH`
  bastan para calcular UV local del asset. Ventaja: si el proyecto no
  expone `face_mask`, este patron sigue funcionando.
- Movie File In TOP dentro del baseXX como slot para que el usuario
  arrastre su asset. `alphapremultiply='straight'` para PNG con alpha
  correcto (NO `premultiplied`, o los bordes salen negros).
- Aspecto del asset: leer con `uTD2DInfos[N].res.zw` y combinarlo con el
  aspecto del frame (`uResolution`) para NO deformar el PNG cuando
  se escala con `uScale`.
- Gate por `uScore`: si YOLO pierde confianza (< ~0.4), passthrough
  automatico. Evita que el asset "vibre" en el centro cuando no hay cara.
- 5 sliders reasignados al contrato para overlay:
  Intensity=opacidad, Speed=wobble, Distortion=escala, Color=tinte, Signature=offsetY.
- Uniforms YOLO se envuelven en guard: `(expr) if op('yolo_in') and numChans>0 else 0.0`
  — igual patron que en base06 (liquid_gold). Si el CHOP no esta cableado,
  no rompe el cook.

## 2026-07-15 — Casa Bacardi / base07 iteracion final: CHOP YOLO + offsets manuales
- Al probar base07 con el CHOP `YOLO_PLUGIN/null7`, el asset seguia al
  rostro pero con un OFFSET consistente (probablemente distinto sistema
  de coords entre YOLO y el video base). El usuario probo el rediseno
  con Select TOP manual, pero prefirio volver al CHOP porque el tracking
  automatico es mas comodo que posicionar a mano en vivo.
- Solucion definitiva: **CHOP YOLO + controles manuales de calibracion.**
  El CHOP da posicion y tamano automaticos; dos parametros manuales
  compensan el offset una sola vez y despues el asset sigue solo:
    - `Offsetx` (-0.5..0.5) - offset horizontal manual (extra, no MIDI)
    - `Offsety` (-0.5..0.5) - offset vertical (slot 5 signature MIDI)
    - `Sizemult` (0.1..3.0) - multiplicador del tamano detectado (extra)
    - `Scale`   (0.5..3.0)  - escala global del asset (slot 3 distortion)
- **Leccion general:** cuando un CHOP externo (YOLO, MediaPipe, plugins de
  terceros) da lecturas con offset o escala mal calibrados, la solucion
  practica no es abandonar el CHOP (perderias el tracking automatico)
  sino exponer los offsets manuales como parametros de calibracion. El
  usuario calibra una vez y el CHOP sigue haciendo su trabajo.
- Este patron es reusable: cualquier efecto face-tracked del skill puede
  seguir la formula "coord = uFaceX + uOffsetX ; size = uFaceW * uSizeMult".

## 2026-07-15 — Casa Bacardi / base07 v4: displace + feedback audio-reactivos
- Sobre base07 (asset PNG sobre rostro) el usuario pidio anadir "algo con
  audio reactividad — un displace o feedback o ambos". Ambos, combinados,
  dieron un look Bacardi consistente: energetico, con movimiento, sin
  perder legibilidad del asset.
- Patron util (aplicable a otros efectos face-tracked del skill):
  * **DISPLACE en shader** (no en TOP externo): deforma el UV del asset
    con `noise2()` value-noise 2D animado por tiempo. Amplitud base
    `uDisplace` + empuje directo por `uAudioLow` → asset "respira" con
    el kick. Barato: ~4 samples por pixel.
  * **FEEDBACK con Feedback TOP loop**: el `feedback1` tiene target = el
    propio GLSL y se conecta al input 2 del GLSL. En shader:
    `col = mix(current, max(current, prev), fbAmount)`. El `max` preserva
    zonas brillantes → estela luminosa (no oscurece). Amplitud base
    `uFeedback` + empuje directo por `uAudioHi` → agudos = estela larga.
  * **PULSE del tamano por `uAudioMid`** (~15%): da ritmo visible al asset
    sin cambiar posicion. Bajo costo, alto valor visual.
- Uniforms directos de audio (`uAudioLow`, `uAudioMid`, `uAudioHi`) usan
  el patron base03: multiplicados por `Audioboost * Audioreact` en la
  expresion, NO por Audiotarget. Asi son independientes del sistema
  MIDI de slot activo.
- El `Audioboost` va en la pagina Audio (no en los 5 slots) — es un
  control global de "cuanto empuja el audio directo a los efectos audio-
  reactivos internos". Default 1.0, rango 0-3.
- Gate por `uScore`: cuando la cara desaparece, en vez de cortar el
  feedback en seco, el shader hace `mix(original, max(original, prev),
  fbAmount * 0.8)` para que la estela decaiga suavemente. Detalle
  pequeno pero importante — sin esto, la estela desaparece de golpe y
  se ve como "corte" cada vez que YOLO parpadea.
