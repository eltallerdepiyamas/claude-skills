# Registro de controladores — Little Jesus

Hecho con el modo learn el 2026-11-02 (`learn_log_parte1.md` + `learn_log.md`).
Para pedir algo, basta con decir el control: "MIDImix knob fila 2 col 3", "Beatstep ch11 pad abajo 4".
Columna **Hoy**: lo que hace hoy en el `.toe`. *Libre* = nadie lo lee.

## MIDImix — canal 1 · entra por `/project1/midiin1` (y `midiin2`, duplicado)

### Knobs

| Col | Fila 1 | Fila 2 | Fila 3 |
|---|---|---|---|
| 1 | CC17 · libre (fase 3: visual activo) | CC18 · Prism Instances (ya no mueve nada: Prism está en base25) | CC19 · Glitch AMT |
| 2 | CC21 · libre | CC22 · Prism Radius (sin efecto) | CC23 · Glitch TX |
| 3 | CC25 · libre | CC26 · Prism Instance Scale (sin efecto) | CC27 · Glitch TY |
| 4 | CC29 · libre | CC30 · Prism Alpha (sin efecto) | CC31 · Glitch AMT2 |
| 5 | CC47 · libre | CC48 · `select40` (por rastrear) | CC49 · Glitch VSTEP |
| 6 | CC51 · libre | CC52 · `/project2/select1` + `select38` (por rastrear) | CC53 · Glitch PERIOD |
| 7 | CC55 · libre | CC56 · Kaleido (era base27 viejo, ya borrado) | CC57 · libre (antes cambiaba visuales) |
| 8 | CC59 · libre | CC60 · LUMA (`lumalevel1` black level) | CC61 · Glitch TRIGGER (`base4/trigger1`) |

Fase 3: fila 1 col 1–5 = visual activo · fila 2 col 1–5 = FX de cámara activo (base18–25).

### Botones

| Col | Arriba (nota) | Abajo (nota) |
|---|---|---|
| 1 | n2 · `select6` (junto con LUMA) — rótulo "V1 ←" | n4 · `select11` — rótulo "VFX2 ←" |
| 2 | n5 · cambia `switch1` de los visuales base1–6, 9–13 — rótulo "V1 →" | n7 · `select18` — rótulo "VFX2 →" |
| 3 | n8 · `select37` — "VFX1 on/off" | n10 · `select37` — "VFX2 on/off" |
| 4 | n11 · `select33` — "V1 color" | n13 · `V2_COLOR` escena — "V2 color" |
| 5 | n14 · Glitch panel Power — "V1 glitch" | n16 · Glitch (`curcuitBending1`) Power + Fx1 — "V2 glitch" |
| 6 | n17 · Glitch Fx2 + Fx3 — "Glitch FX1" | n19 · `select4` — "Prism" |
| 7 | n20 · Glitch Fx4 + Fx5 + Scaledownres — "Glitch FX2" | n22 · `blend_switch` escena + monocromo (`switch10`) — "Bypass" |
| 8 | n23 · `switch12` — "Invert V1" | n25 · Prism on/off (`switch1` de /project1) → **libre** desde que Prism se movió |

| Botón | Nota | Hoy |
|---|---|---|
| BANK LEFT | n26 | `select27` (por rastrear) |
| BANK RIGHT | n27 | `select27` (por rastrear) |
| SOLO | n28 | `switch5` de /project1: banco de rampas de color — rótulo "strobe" |

### Faders

| Fader | CC | Hoy |
|---|---|---|
| 1 | CC20 | VISUAL → OSC a Resolume |
| 2 | CC24 | ARTIST → OSC a Resolume |
| 3 | CC28 | CCTV → OSC a Resolume |
| 4–8 | CC32, 50, 54, 58, 62 | parámetros de la escena multicam activa (`setup_scene_faders.py`) — **solo en Little Jesus** |
| MASTER | CC63 | OSC a Resolume (`/project1/select1`) |

## Faders 4–8 por escena (Little Jesus)

Salen de `setup_scene_faders.py`; se reasignan solos al cambiar de escena (con takeover).

| Escena | F4 | F5 | F6 | F7 | F8 |
|---|---|---|---|---|---|
| Gridwall | Gap |  |  |  |  |
| Pip | Pipsize | Pipborder | Pippadding | Pipspeed | Pipmovement |
| Breathing Grid | Breatheamt | Breathespeed | Phaseoffset |  |  |
| Float Chaos | Speed | Spread | Camsize |  |  |
| Floating Pieces | Piecesize | Speed |  |  |  |
| Gridwall Drift | Speed | Sizevariance |  |  |  |
| Magnetic Pull | Speed | Pullstrength | Pullradius | Camsize |  |
| Orbit Dance | Orbitradius | Orbitspeed | Piecesize | Herosize | Bgscale |
| Pendulum | Speed | Amplitude | Camsize |  |  |
| Split Asimetrico | Splitratio | Gap |  |  |  |
| Ripple Grid | Speed | Rippleamt | Ripplefreq |  |  |
| Swarm | Speed | Swarmradius | Centerspeed | Camsize |  |
| Wave Scroll | Speed | Waveamt | Wavefreq | Camsize |  |
| Rand Collage / Drift / Orbit / Swing | Lagtime | Tilesize |  |  |  |
| Rand Bend / Flow / H / Morph / Offset / Pulse / Split / Stair / V / Wave | Lagtime |  |  |  |  |
| Hero / Grid Dinamico / Fullscreen | — |  |  |  |  |

## Beatstep Pro · entra por `/project1/midiin3` (y `/project2/MIDI`)

### Pads (modo drum)

| Canal | Fila | Notas (izq → der) | Hoy |
|---|---|---|---|
| 10 | arriba | n45–52 | visuales base1–8 |
| 10 | abajo | n37–44 | FX base17 (limpio) – base24 |
| 11 | arriba | n45–52 | visuales base9–16 |
| 11 | abajo | n37–44 | n37 = base25 Prism · n38–44 = **libres** (base26–32 vacíos) |

Los pads también mandan aftertouch (`chNNaftertouchNN`): se ignora.

### Knobs — canal 11

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Arriba | CC11 | CC75 | CC72 | CC77 | CC78 | CC94 | CC74 | CC76 |
| Abajo | CC115 | CC19 | CC20 | CC17 | CC18 | CC92 | CC80 | CC73 |

Hoy: **libres** (los mapeos viejos esperaban `ch10ctrl21–28`, que ya no llegan).
⚠️ Mandan CC17–20 en canal 11; el MIDImix usa CC17–20 en canal 1. No chocan mientras se lean con el canal (`ch11ctrl17` ≠ `ch1ctrl17`).

### Secuenciadores (teclado, notas 61–73)

| Seq | Canal | Notas | Hoy |
|---|---|---|---|
| Seq 1 | 1 | n61–73 | libre (no choca con el MIDImix: sus notas son n2–n28) |
| Seq 2 | 2 | n61–73 | `table1` → pads viejos que mandaban `switch5` (capa borrada) → **sin efecto** |

Orden de teclas registrado: arriba n62, 64, 67, 69, 71 (negras) · abajo n61, 63, 65, 66, 68, 70, 72, 73 (blancas).

## Pendientes que salieron del registro

- Fila 2 del MIDImix: hoy mueve cosas que ya no existen (Prism viejo, Kaleido de base27). Se libera en la fase 3.
- Rastrear `select40`, `select38`/`/project2/select1`, `select27`, `select33`, `select37`, `select4`, `select6`, `select11`, `select18`: qué mueven al final de su cadena.
- Seq 2 y los pads de canal 11 n38–44 quedan libres para cosas nuevas.
- Fase 4: un solo MIDI In por controlador (hoy MIDImix entra por `midiin1` y `midiin2`; Beatstep por `midiin3` y `/project2/MIDI`).
