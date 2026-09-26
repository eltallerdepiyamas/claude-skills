---
name: td-flyer-audioreactivo
description: Anima flyers, pósters e imágenes fijas en TouchDesigner como loops audio-reactivos, escribiendo el shader GLSL y el script de Python (builder) que arma y cablea toda la red a partir de la imagen. Úsalo SIEMPRE que el usuario quiera animar un flyer/póster/portada/story, mencione "anima este flyer", "haz que se mueva este póster", "story loop", "flyer reactivo", "que reaccione a la música", o suba una imagen fija para volverla movimiento en TouchDesigner — aunque no diga "shader" o "TouchDesigner" explícitamente. Cubre boil, feedback/estela, chroma split (aberración RGB), halftone y threshold wobble, con reactividad de audio por bandas. Es un workflow SEPARADO del rig de VJ (td-vj-builder) — contenedor propio, sin baseXX ni /project2 ni MIDI.
---

# TD Flyer Audioreactivo

Convierte una imagen fija (flyer, póster, portada) en una pieza animada y reactiva al audio dentro de TouchDesigner. El skill NO opera TouchDesigner: produce archivos — un builder de Python que el usuario corre en un Text DAT, y opcionalmente shaders GLSL. El builder arma una red autocontenida en su propio contenedor (un Base COMP), sin tocar nada del rig de VJ.

## En qué se diferencia del rig (td-vj-builder) — léelo

Este workflow y el del rig **se contradicen a propósito**, por eso son skills separados. No mezcles convenciones:

- **Sin baseXX, sin /project2, sin escena_modular.** Crea su propio Base COMP (default `flyer_loop`) en `/`.
- **Sin contrato de 5 sliders ni Audiotarget único, sin MIDI.** Aquí los parámetros son libres y el audio se rutea por efecto (cada efecto elige su banda).
- **Cadena de audio propia.** No toma `base17/audio_in`; construye su análisis de 3 bandas (low/mid/high) desde un Audio Device In.
- La entrada es una **imagen fija**, no cámara ni generativo.

Si el usuario quiere meter un efecto a su rig en vivo con MIDI, ese es el otro skill. Aquí es flyer aparte.

## Flujo de trabajo

1. **Pregunta el destino antes de construir** (decide casi todo lo demás):
   - **Loop autónomo** (se exporta como MP4/GIF para subir como story) — o —
   - **Reactivo en vivo** (corre en TD reaccionando a audio en tiempo real).
   Ver `references/loop-vs-vivo.md` para qué cambia en cada caso (sobre todo el feedback no cierra loop perfecto; en vivo da igual, en export hay que trimear).

2. **Consigue la imagen.** Pide la ruta local del flyer (en TD el Movie File In apunta a la máquina del usuario, no a este entorno). Si te suben la imagen, analízala: paleta, contraste, motivos con movimiento implícito (estelas, círculos, trazos), tratamiento del logo. Eso guía qué efectos proponer.

3. **Propón efectos desde el catálogo.** Lee `references/efectos.md` y elige según el flyer (no metas todo siempre). Para cada uno di qué aporta y a qué banda de audio lo amarrarías. Confirma con el usuario antes de construir.

4. **Construye desde el template.** Parte de `templates/flyer_builder.py`:
   - Pon `IMAGE_PATH` con un placeholder claro y recuérdale al usuario cambiarlo.
   - Activa solo los efectos acordados (puedes recortar la cadena; está comentado por bloques).
   - Revisa `library/shaders/` antes de escribir un shader nuevo (ej. el chroma ya existe).
   - Guarda el builder (y shaders sueltos si los hay) en `/mnt/user-data/outputs/` y preséntalos.

5. **Cierra honesto:** el builder es idempotente (reconstruye limpio al re-correr, pero borra ajustes manuales de la sesión). Avisa del caveat de loop si aplica, y del `gain` de audio que puede necesitar ajuste según la interfaz del usuario.

6. **Aprende:** al terminar, propón al usuario una entrada en `LEARNINGS.md` (rangos que gustaron, nombres que conservó, qué se rompió) y copia a `library/` cualquier shader reutilizable. El usuario aprueba cada escritura.

## Arquitectura que arma el builder

```
flyer_in (Movie File In)
  ├─ boil_noise (Noise, en círculo) ─┐
  └────────────────────────────────► boil_displace (Displace)
                                         │
                          trail_comp (Composite/Over) ◄── trail_level ◄── trail_xform ◄── trail_fb
                                         │                                   (feedback: Target TOP = trail_comp)
                                         ▼
                                      chroma (GLSL: RGB split)
                                         ▼
                                      grade (Level) ► out_null ► out1

audio_devicein ► [af_low|af_mid|af_high] ► analyze(RMS) ► rename ► merge ► lag ► gain ► null 'audio'
```

Los parámetros viven en el contenedor: página **Flyer** (valores base, arrastrables) y página **Audio** (Audioreact, Audiosmooth, y por efecto un menú de banda `*source` + un `*audio` de cantidad).

## Convenciones técnicas (gotchas reales, respétalas)

- **Builder idempotente:** lista `managed` de nodos → destruir → reconstruir. Nunca dejes duplicados. Path-fallback en `run()` (`/CONTAINER`, etc.).
- **Trig en expresiones de TD:** `cos`/`sin` NO existen sueltas en el namespace de expresiones. Usa `math.cos` / `math.sin`. (Da `NameError: name 'cos' is not defined`.)
- **Feedback TOP:** se alimenta por **parámetro Target TOP** (escrito, no arrastrado), con el **input vacío**. El target es el nodo del que quieres el frame anterior (ej. `trail_comp`). Si conectas un input además, sale *"Cook dependency loop detected"*; si lo dejas sin target ni input, sale *"Not enough sources specified"*. Prueba nombres de par `('top','targetop','target')` según versión.
- **16-bit float** en los TOPs del feedback (Composite/Feedback/Level) para evitar banding.
- **Audio en la expresión, no en el slider:** el slider de la página Flyer queda como valor base arrastrable; el término de audio se SUMA en la expresión del parámetro consumidor (ver helper `audio_term`). Así el slider no se "congela".
- **Tolerancia de versión:** setea parámetros probando varios nombres (`_set_par`, `_set_menu`) porque los nombres internos cambian entre versiones de TD.
- **Resolución:** los TOPs heredan la del Movie File In (el flyer). No hardcodees.

## Ajuste de feel (rangos que funcionaron)

- `Boilamt` 0.005–0.02 (más se vuelve líquido). `Boilscale` bajo = ondas grandes, alto = textura fina.
- `Trailzoom` 1.01 ≈ eco hacia afuera; 0.99 ≈ túnel hacia adentro. Si se "quema" a blanco, baja `Traildecay` antes que el zoom.
- `Chromaamt` 1–4 base; el empuje de audio (`Chromaaudio`) puede ir alto (20–40) para que el split lata en los agudos.
- `gain` del `audio_gain` ≈ 20 como punto de partida; súbelo si el audio no engancha.
