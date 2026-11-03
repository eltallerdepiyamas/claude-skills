# Little Jesus — estado del .toe (2026-11-02)

Proyecto: `E:\Mi unidad\01. FREELANCE\2026\14. LITTLE JESUS\01. EDITABLES\` (Drive).
Scripts y reportes de trabajo en su carpeta `control/`. Aquí van copias de lo que sirve consultar
desde cualquier compu: `controladores.md` (qué hace cada knob/botón/pad), `contrato_propuesta.md`,
`inventario_project1.md`, `knobs_mapa.md`, `botones_mapa.md`, `mapa_pads.md`, `CLAUDE.md`.

## Estructura

| Dónde | Qué | Control |
|---|---|---|
| `/project2` base1–16 | visuales (línea V1) — **sin parámetros todavía** | pads Beatstep (fila de arriba) |
| `/project2` base17 | cámaras: `escena_modular` (layouts multicam + Rand) | Stream Deck (escenas) + faders 4–8 |
| `/project2` base18–24 | FX de cámara (línea V2) con **contrato de 5** (Mezcla, Tiempo, Distorsion, Color, Firma) + Bypass + Audio | pads Beatstep (fila de abajo) |
| `/project2` base25 | **Prism** (antes `/project1/PrismTop4`), sin contrato, sus 23 parámetros expuestos en base25 | pad ch11 abajo 1 |
| `/project2` base26–32 | libres para FX nuevos (los viejos en `control/respaldo_tox/`) | pads ch11 abajo 2–8 |
| `/project1` | "master": FX globales de la línea V2 (mono, color HSV, rampas de color, V2_COLOR, glitch `curcuitBending1`, luma, overlays, strobe con kick, CAM_2 encima) → `ndiout1` → Resolume | botones MIDImix + fila 3 |

## Decisiones

- Salida a Resolume: recomendado **Spout** (misma compu); NDI solo si Resolume está en otra máquina.
- Faders 1–3 + MASTER del MIDImix = OSC a Resolume (Visual, Artist, CCTV, master). Faders 4–8 = escena multicam activa (**solo en este show**).
- MIDImix: fila 1 = visual activo (fase 3) · fila 2 = FX de cámara activo (fase 3) · fila 3 = glitch global.
- Botones MIDImix = FX globales por línea (V1 arriba, V2 abajo), se quedan como están.
- Prism como FX de cámara en base25, no global.
- Los FX base25–32 originales (Warp Feedback, Trails, Bloom, Light Tunnel, RGBA Delay, Radial Blur, Kaleidoscope, Displace Wave vacío) se borraron por limpieza; `.tox` en `control/respaldo_tox/`.

## Pendiente

1. Fase 3: filas 1 y 2 del MIDImix siguen al visual / FX activo, con takeover y lag. Prism: Pattern0alpha, velocidad de giro (anima Rotsinphase), Distortion, Chromatic, Pattern0instances.
2. Contrato en visuales base1–16 (hoy sin parámetros).
3. Fase 4: limpiar `/project1` (3 MIDI In, ~57 Select CHOP, `select47`/`null18` sueltos, `curcuitBending` es solo panel de control del `curcuitBending1`), un MIDI In por controlador, nombres claros.
4. Página MIX del Stream Deck: espejo de las filas del MIDImix con nombre y % de cada slot.
5. Botones/pads libres: ch11 abajo 2–8, Seq 2, knobs del Beatstep, MIDImix n25 (ex Prism on/off), knob fila 3 col 7.
