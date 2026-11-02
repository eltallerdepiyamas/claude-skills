# PROYECTO: CASA BACARDI — Booth Interactivo / Temporada de Festivales 2026

Generado por td-vj-builder. Contexto en disco para este show.
Última actualización: 2026-07-15

---

## Rutas (verificar que coincidan con esta máquina)
- Proyecto .toe:         H:\Mi unidad\01. FREELANCE\2026\CASA BACARDI\casa_bacardi.toe
                         (ajustar si difiere — usar project.folder desde TextPort: `print(project.folder)`)
- Shaders de efectos:   effects_glsl/shaders/
- Audio canónico:        /bacardi_audio/null_audio   (canales: low mid high)
                         ⚠️ Ruta a confirmar con Sebas — es propia del .toe, no ../../project1/null4

---

## Arquitectura del proyecto (STANDALONE — no es /project2)

Este .toe es INDEPENDIENTE del rig principal. No existe /project2. La jerarquía es:

```
/
├── bacardi_input          → host de entrada (YOLO + webcam)
│     ├── webcam_in        → Video Device In TOP (webcam principal)
│     ├── yolo_plugin      → YOLO CHOP/TOP (face, object y pose tracking)
│     ├── compositor       → mezcla / switch entre feed limpio y overlays de YOLO
│     └── switch_main      → salida hacia los filtros (equivalente a base17/switch1)
│
├── bacardi_audio          → análisis de audio del show
│     └── null_audio       → salida con canales low / mid / high
│
├── base01 … base06        → EFECTOS / FILTROS sobre el feed de switch_main
│                            (override de numeración en este proyecto — ver tabla abajo)
├── base18                  → EFECTO existente (NO destruir; coexiste con base01-06)
│
├── bacardi_banners        → banners audio-reactivos existentes (NO TOCAR)
│
└── switch_FINAL           → salida a pantalla LED 16:9
```

### Señal de un efecto
`/bacardi_input/switch_main` → `baseXX` (efecto) → `switch_FINAL` → pantalla LED

### Fuente de video para efectos
Cada efecto lee su input desde `/bacardi_input/switch_main` (no desde base17).
En los builders, reemplazar la ruta de `select_video` por `/bacardi_input/switch_main`.

### Fuente de audio
Select CHOP interno apuntando a `/bacardi_audio/null_audio`, canales: `low mid high`.
En los builders, reemplazar `../../project1/null4` por la ruta real de null_audio.

### Datos de YOLO disponibles (canales confirmados del CHOP `yolo_in`)
| Canal      | Rango     | Uso en shaders                                          |
|------------|-----------|--------------------------------------------------------|
| `x`        | 0.0–1.0   | Posición horizontal del objeto → `uFaceX`              |
| `y`        | 0.0–1.0   | Posición vertical del objeto → `uFaceY`                |
| `width`    | 0.0–1.0   | Ancho del bounding box → proxy de presencia → `uPresence` |
| `height`   | 0.0–1.0   | Alto del bounding box → escala del efecto              |
| `score`    | 0.0–1.0   | Confianza de detección → gate de activación            |
| `id`       | int       | ID del objeto (no usar en shaders)                     |
| `object`   | int       | Clase del objeto (no usar en shaders)                  |

**Ruta canónica del CHOP de YOLO (confirmada):**
```python
parent(2).op('YOLO_PLUGIN/null7')
```
Cada builder crea un Select CHOP llamado `yolo_in` dentro del baseXX apuntando a esa ruta.

**Uniforms derivados — mapeo canónico para todos los builders:**
```python
uFaceX    = op('yolo_in')['x']          # posición horizontal normalizada
uFaceY    = 1.0 - op('yolo_in')['y']   # Y invertido (TD vs GLSL)
uPresence = op('yolo_in')['width']      # 0=nadie, >0.1=persona detectada
uScore    = op('yolo_in')['score']      # gate: score < 0.4 → ignorar detección
```

**Video de entrada a los shaders:** feed de webcam LIMPIO, sin overlay de YOLO.
Los datos de posición llegan SOLO como uniforms — el cuerpo siempre legible.
`yolo_in` se conecta como CHOP separado, nunca como TOP.

---

## Bases ocupadas en este proyecto

> **Override de numeración:** este show usa base01–base06 (no las ranges canónicas
> 18–24/38–45). El midi sampler interno del booth está mapeado a estos números.

| Base   | Categoría | Nombre                  | Shader                       | Inputs extra                          | Audio directo    | Notas                              |
|--------|-----------|-------------------------|------------------------------|----------------------------------------|------------------|------------------------------------|
| base01 | efecto    | body_aura               | body_aura.frag               | YOLO CHOP (uFaceX/Y, uPresence, uScore)| —                | Halo alrededor de silueta (bbox aprox.) |
| base02 | efecto    | echo_trails             | echo_trails.frag             | feedback                               | —                | Estelas de movimiento (exp. múltiple) |
| base03 | efecto    | **mascara_rostro**      | mascara_rostro.glsl          | face mask TOP (YOLO_PLUGIN/face_mask)  | uAudioLow/uAudioHi | Mosaico/signal SOLO en rostro. Mode: 0=RUBI (rojo Bacardi) 1=MENTA (verde menta) |
| base04 | efecto    | **rostros_slitscan**    | rostros_slitscan.glsl        | mask TOP + red multi-GLSL interna      | uAudioLow/uAudioHi | Slit-scan SOLO en rostro. Mode: 0=RUBI / 1=MENTA. Arquitectura GLSL Multi: tex3d1 + ramp1+noise1→displace1→time1 |
| base05 | efecto    | neon_edge               | neon_edge.frag               | —                                      | —                | Sobel + glow neon Bacardi          |
| base06 | efecto    | liquid_gold             | liquid_gold.frag             | YOLO CHOP + feedback                   | —                | Warp fluido per research (look base) |
| base07 | efecto    | **asset_rostro**        | asset_rostro.glsl            | CHOP `yolo_in` + Movie File In `asset_face` + Feedback TOP (loop sobre GLSL) | uAudioLow/Mid/Hi | PNG con alpha sobre bbox del rostro con **displace** (UV noise, graves) y **feedback trail** (agudos). Extras: Offsetx/Sizemult/Displace/Feedback. Audioboost multiplica los uniforms directos. |
| base18 | efecto    | (existente)             | —                            | —                                      | —                | Filtro previo — NO destruir        |

> base03 y base04 nuevos (2026-07-13): efectos aplicados SOLO al rostro
> detectado por YOLO, con dos looks Bacardi crossfadeables por `Mode`
> (0=**RUBI** rojo #FF1F3A / 1=**MENTA** verde menta #6DC49A). Los tints
> vienen de `uColorA`/`uColorB` — expuestos como RGBA pickers en la
> página Filter, se pueden ajustar en vivo. Ambos requieren un TOP de
> máscara de rostro desde YOLO — la ruta por defecto es
> `parent(2).op('YOLO_PLUGIN/face_mask')`, pendiente confirmar el nombre
> exacto con Sebas. Si no existe, el select TOP sale negro y el efecto
> se desactiva por sí solo (mask=0 → passthrough).
>
> base07 nuevo (2026-07-15, v4): compone un PNG con alpha (Movie File In
> `asset_face`) sobre el rostro detectado por YOLO, con **displace** y
> **feedback trail** audio-reactivos. Usa el CHOP `YOLO_PLUGIN/null7`
> (canales `x y width height score`) para tracking automático + offsets
> manuales para calibrar el desalineamiento:
> - **Offsetx / Offsety / Sizemult** — calibración del bbox de YOLO.
> - **Scale (slot 3 MIDI)** — escala global del asset.
> - **Displace (extra)** — amplitud del noise que deforma el UV del asset.
>   Empujado por `uAudioLow` → el asset "respira" con los graves.
> - **Feedback (extra)** — persistencia del frame anterior (estela).
>   Empujado por `uAudioHi` → estela más larga con agudos.
> - **Audioboost** (página Audio) — multiplica los uniforms directos
>   `uAudioLow / uAudioMid / uAudioHi` (patrón base03).
> Feedback TOP `feedback1` con target = `glsl_asset_rostro`, cableado al
> input 2 del mismo GLSL. `uAudioMid` pulsa el tamaño (~15%) para dar
> ritmo visible en medios. Gate por `uScore < 0.4` → passthrough.
>
> Los builders antiguos (`setup_base03_tropical_refract.py`,
> `setup_base04_bacardi_chroma_split.py`) quedan en la carpeta como referencia
> pero no deben ejecutarse — usar los `setup_base03_mascara_rostro.py` y
> `setup_base04_rostros_slitscan.py`.

---

## Contrato de parámetros (recordatorio — igual que el rig principal)

- 5 sliders por rol en orden fijo: intensidad, velocidad, distorsión, color, firma.
- `Bypass` aparte (toggle). Página `Audio`: Audioreact + Low/Mid/High + Audiotarget + Audiomult.
- Audio se suma en la EXPRESIÓN del uniform (clamp), no en el slider — el slider sigue mappeable a MIDI.
- GLSL output resolution: **Use Input** (el efecto hereda el tamaño del video de entrada).
- `uResolution` → `me.width` / `me.height` del propio GLSL TOP.
- `uTime` → `absTime.seconds`.

---

## Diferencias respecto al rig principal (LEER ANTES DE CONSTRUIR)

| Aspecto               | Rig principal (/project2)          | Casa Bacardi (standalone)                  |
|-----------------------|------------------------------------|--------------------------------------------|
| Raíz del proyecto     | /project2                          | / (raíz del .toe)                         |
| Fuente de video       | /project2/base17/switch1           | /bacardi_input/switch_main                 |
| Fuente de audio       | ../../project1/null4               | /bacardi_audio/null_audio (confirmar ruta) |
| Resolución de ref.    | escena_modular ResW/ResH           | Definir nodo de referencia de resolución   |
| Hay base17            | Sí                                 | No — reemplazado por bacardi_input         |
| Hay escena_modular    | Sí                                 | No                                         |
| Layouts CCTV          | layout_* en escena_modular         | No aplica en esta edición                  |
| YOLO / tracking       | No                                 | Sí — CHOP data disponible para uniforms    |

---

## Cómo correr un builder

```
# Opción A: desde Text DAT dentro del baseXX
exec(open('<ruta_absoluta>/setup_baseXX_<name>.py').read())

# Opción B: pegar el contenido en el Text DAT y hacer Run
```

Los builders son idempotentes: destruyen y reconstruyen los children manejados.
El baseXX contenedor nunca se destruye ni renombra.

---

## Pantalla LED
- Resolución de salida: 16:9 (confirmar resolución física con producción — típico 1920×1080 o superior)
- Fuente: switch_FINAL → salida de video al procesador LED
- Los efectos deben verse bien en LED: evitar detalles muy finos, preferir contraste alto y movimiento legible a distancia

---

## Notas del show (libre — el skill no borra esto)
- Edición 3 de Casa Bacardi. Las dos primeras ediciones usaron banners audio-reactivos (bacardi_banners). Ahora se agrega pantalla LED con experiencia interactiva.
- El filtro en base18 ya existe y funciona — no destruir.
- La estética Bacardi es energética pero premium: movimiento continuo, colores vibrantes, legibilidad del performer siempre presente.
- Sebas conecta manualmente el audio y el YOLO — los builders no deben asumir rutas rígidas donde haya incertidumbre.
