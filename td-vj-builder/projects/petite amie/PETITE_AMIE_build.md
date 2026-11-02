# PROYECTO: PETITE AMIE — Foro La Paz, CDMX · 25 julio 2026, 20:00

Brief ejecutable para Claude Code. Construir con la skill `td-vj-builder`.

---

## 0. Cómo usar este archivo

Claude Code debe:

1. Leer `SKILL.md`, `LEARNINGS.md` y `references/shader-conventions.md` de la skill **antes** de escribir nada.
2. Construir en el orden de la §10 (tandas). No saltar tandas.
3. Por cada ítem generar **dos archivos**: el shader y el builder `setup_baseXX_<nombre>.py`, derivado de `templates/effect_builder.py` o `templates/visual_builder.py`.
4. Shaders a `effects_glsl/shaders/` y `visuals_glsl/shaders/` dentro de la carpeta del `.toe`.
5. Escribir/actualizar el `CLAUDE.md` del proyecto con `references/project-claude-md-template.md`, preservando "Notas del show".

**Sebas corre los builders desde el Text DAT / TextPort. Claude Code nunca opera TouchDesigner.**

### ⚠ Confirmar antes de correr nada

La §7 asigna **base1–base8** a los visuales. Sebas ya tiene visuales propios que ha usado con esta banda. **Verificar qué bases están ocupadas y remapear la tabla de la §7 antes de ejecutar el primer builder** — los builders destruyen los children del base destino.

---

## 1. Meta del show

- **Banda:** Petite Amie (CDMX)
- **Venue:** Foro La Paz, Av. de la Paz 57, 1er piso, San Ángel, Álvaro Obregón
- **Fecha:** sábado 25 de julio de 2026, 20:00
- **Luz:** interior, nocturno, foro chico de piso. El público está cerca del escenario → **las caras deben seguir legibles**. Esta es la restricción que manda sobre todo lo demás.
- **Tono:** hipnótico, brillante, líquido, nostálgico

## 2. Dirección visual

Pop-rock psicodélico / dream pop. Dos vocalistas cantando en francés y español, guitarras acústicas, sintetizadores envolventes, solos con fuzz, baterías prominentes. Influencias declaradas: Beatles, Pink Floyd, Melody's Echo Chamber, Unknown Mortal Orchestra, Crumb, Big Thief, y el trip-hop de Bristol de los 90. Segundo disco *Hay Veces* (enero 2025).

**Referencias a extraer:**

| Referencia | Qué tomar |
|---|---|
| Liquid light shows sesenteros | Aceite y agua proyectados: blobs que se dividen y funden. Movimiento lento, sin cortes. |
| Cine en 16mm | Grano, halación en altas luces, weave de proyector |
| Fotografía de doble exposición | Capas que conviven sin jerarquía |
| Trip-hop Bristol 90s | Densidad, penumbra, no todo iluminado |
| Pink Floyd (era *Meddle*) | Formas circulares simples, coronas de luz |
| Nouvelle vague / french pop | Pasteles desaturados, encuadre limpio |

**Paleta de arranque** (los 3 pickers RGBA por base permiten repintar en vivo):

| Rol | Hex |
|---|---|
| Ámbar | `#F2B33D` |
| Rosa | `#E86A92` |
| Violeta | `#6C4AB6` |
| Turquesa | `#2AA79B` |
| Crema | `#F4EDE4` |
| Negro violáceo | `#151020` |

**Evitar:** caleidoscopios y mandalas (ya usados en Psych Fest), strobo agresivo, glitch duro, cortes rápidos, saturación de rave.

## 3. Contexto de cámara

3 cámaras físicas (2 escenario, 1 house) pero **pasan por un switcher externo**. Al rig llega **una sola señal: el program**.

**Consecuencia:** no se construyen layouts CCTV (`layout_*`). Necesitarían feeds separados en `CAM_1..5`. Todos los efectos operan sobre `base17/switch1`.

## 4. Audio

- **Banda dominante:** `Low` — baterías prominentes y bajo presente.
- **Carácter:** respiración lenta, presión. **No trigger de beat.** Toda energía de audio pasa por `smoothstep`/`mix` antes de tocar un uniform.
- **Default en cada base:** `Audioreact` ON, `Low` ON, `Mid`/`High` OFF, `Audiomult` 1.0.

## 5. Contrato de parámetros (fijo, no negociable)

Cinco sliders float en orden de rol, con rango real:

1. Intensidad / cantidad
2. Velocidad / tiempo
3. Distorsión / deformación espacial
4. Color / cromática
5. Firma

Más, aparte de los cinco: toggle `Bypass`, y página `Audio` con `Audioreact` + `Low`/`Mid`/`High` (suman) + `Audiotarget` (menú a uno de los 5) + `Audiomult` 0–3.

La energía de audio se suma en la **expresión del uniform** con clamp, nunca en el slider — el slider queda libre para MIDI.

## 6. Reglas técnicas no negociables

Destiladas de `LEARNINGS.md`. Violarlas es lo que rompió builds anteriores.

**Feedback (aplica a los 16 ítems de este proyecto):**

- **Pixel Format `16-bit float (RGBA)`** en el GLSL TOP **y** en el Feedback TOP. Sin excepción. Con 16 loops vivos, 8-bit produce banding en minutos.
- Ningún `uDecay` / `uAccum` con default ≥ 1.0. Ninguno. Un feedback saturado a blanco a media rola no se recupera sin bajar el fader.
- Cableado: `feedback1.Target` = el GLSL TOP; `feedback1` → input 1 del GLSL; `select_video` → input 0 del `feedback1` (automático, Sebas no lo cablea a mano).
- `Extend U/V = Mirror` en el GLSL TOP cuando haya zoom o displacement acumulativo.

**GLSL en TouchDesigner:**

- **Nunca redeclarar lo que TD inyecta:** `in vec3 vUV;`, `sTD2DInputs[]`, `sTD3DInputs[]`, `uTDOutputInfo`. Causa `'redefinition'` al compilar. Usar `vUV.st` directo.
- Nunca `uniform sampler2D` para entradas. Input 0 = cámara, input 1 = feedback.
- Salida: `fragColor = TDOutputSwizzle(vec4(color, 1.0));`
- Sin dynamic array indexing: reemplazar loops sobre arrays por cadenas `if / else if`.
- En GLSL Multi TOP, dejar el parámetro Vertex Shader **vacío** (`TDPos()` sin argumentos no compila en TD 2023.11600).

**Builders:**

- `ParMode.EXPRESSION` — global, **sin** prefijo `td.`.
- `me.par.resolutionw` / `me.par.resolutionh` en expresiones de parámetro; **nunca** `me.width` / `me.height` (loop de cook).
- Output resolution del GLSL = **Use Input** en efectos; `uResolution` → `me.width`/`me.height`.
- `audio_in` = un Select CHOP, CHOPs = `../../project1/null4`, Channel Names = `low mid high`.
- Todo uniform declarado en el shader debe tener su Custom Parameter creado. `_bind_uniform` valida y avisa con `[WARN]` en vez de tronar.
- Builders idempotentes: snapshot → destruir managed children → reconstruir.
- **Nunca renombrar un baseX.** El MIDI sampler depende del número.

**Performance:**

- 16 loops de feedback simultáneos cuestan mucho más que 16 shaders normales. Anotar en el `CLAUDE.md` que Sebas debe verificar el cooking de las bases inactivas y apagarlo donde se pueda.

## 7. Asignación de bases

**Efectos de cámara** (canónico: 18–24, luego 38–45):

| Base | Nombre | Feedback |
|---|---|---|
| base18 | `nucleo_frio` | sí |
| base19 | `soft_halate` | sí |
| base20 | `eco_lento` | sí |
| base21 | `dos_voces` | sí |
| base22 | `anamorph_ghost` | sí |
| base23 | `retrato_focal` | sí |
| base24 | `breath_zoom` | sí |
| base38 | `cortina_franjas` | sí |

**Visuales** (generativos puros — `GENERATIVE_ONLY = True`):

| Base | Nombre |
|---|---|
| base1 | `grano_degradado` |
| base2 | `liquid_light` |
| base3 | `niebla_capas` |
| base4 | `humo_tinta` |
| base5 | `campo_bokeh` |
| base6 | `mareas_color` |
| base7 | `eclipse` |
| base8 | `cuerdas` |

---

## 8. Efectos de cámara — specs

Convención camelCase. Input 0 = `base17/switch1`. Input 1 = feedback.

### base18 · `nucleo_frio` — **look base**

El centro del frame no acumula feedback; los bordes sí. La cara queda limpia y legible mientras todo alrededor se convierte en pintura líquida. Es el efecto más seguro del set para un foro chico.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uAccum` | Accum | 0.0 – 0.98 | 0.86 |
| 2 | velocidad | `uDrift` | Drift | 0.0 – 0.02 | 0.004 |
| 3 | distorsión | `uWarp` | Warp | 0.0 – 0.04 | 0.012 |
| 4 | color | `uChroma` | Chroma | 0.0 – 0.02 | 0.005 |
| 5 | firma | `uCoreRadius` | Coreradius | 0.10 – 0.90 | 0.42 |

Extras: `uCoreSoft` (Coresoft) 0.05–0.50 def 0.22 · `uTint` (Tint) RGBA def `(0.95, 0.85, 0.70)`

Audio: `Audiotarget` = Accum, `Low`. El warp usa gradiente de luminancia del feedback (cruz de 4 muestras) enmascarado por `1.0 - smoothstep(coreRadius - coreSoft, coreRadius + coreSoft, dist)`.

### base19 · `soft_halate` — **look base**

Halación de película: las altas luces sangran color cálido alrededor y el aura persiste unos frames. Suaviza sin destruir.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uHalation` | Halation | 0.0 – 1.0 | 0.45 |
| 2 | velocidad | `uBleedSpeed` | Bleedspeed | 0.0 – 2.0 | 0.50 |
| 3 | distorsión | `uSpread` | Spread | 0.0 – 0.06 | 0.018 |
| 4 | color | `uWarmth` | Warmth | 0.0 – 1.0 | 0.60 |
| 5 | firma | `uThreshold` | Threshold | 0.40 – 1.00 | 0.72 |

Extras: `uDecay` (Decay) 0.80–0.98 def 0.92 · `uTint` (Tint) RGBA def `(1.0, 0.72, 0.42)`

Audio: Halation, `Low`. Extraer altas luces con `smoothstep(uThreshold, 1.0, luma)`, expandirlas radialmente y acumularlas con `max()` para que el aura no oscurezca.

### base20 · `eco_lento`

Estela larguísima donde sólo lo brillante deja cola. Con `uLumaGate` alto, la banda se mueve limpia y sólo las luces de escenario dejan rastro.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uEcho` | Echo | 0.0 – 0.99 | 0.90 |
| 2 | velocidad | `uLag` | Lag | 0.0 – 1.0 | 0.35 |
| 3 | distorsión | `uPull` | Pull | 0.0 – 0.03 | 0.008 |
| 4 | color | `uHueDrift` | Huedrift | −0.006 – 0.006 | 0.0015 |
| 5 | firma | `uLumaGate` | Lumagate | 0.0 – 1.0 | 0.55 |

Extras: `uGain` (Gain) 0.5–2.0 def 1.15

Audio: Echo, `Low`. `uLag` invierte la inyección de frame nuevo (`mix = 1.0 - uLag`). Componer con `max()`.

### base21 · `dos_voces`

Dos lecturas del feedback con decay distinto y tinte propio cada una, ligeramente espejadas. Concepto directo: las dos vocalistas. Una capa recuerda más que la otra.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uBlend` | Blend | 0.0 – 1.0 | 0.55 |
| 2 | velocidad | `uDecayFast` | Decayfast | 0.70 – 0.98 | 0.86 |
| 3 | distorsión | `uMirrorShift` | Mirrorshift | 0.0 – 0.30 | 0.08 |
| 4 | color | `uTintSplit` | Tintsplit | 0.0 – 1.0 | 0.70 |
| 5 | firma | `uDecaySlow` | Decayslow | 0.90 – 0.995 | 0.975 |

Extras: `uTintA` (Tinta) RGBA def `(1.0, 0.55, 0.72)` · `uTintB` (Tintb) RGBA def `(0.42, 0.78, 0.72)`

Audio: Blend, `Mid`. La firma es la **diferencia** entre `uDecaySlow` y `uDecayFast`: si se igualan, el efecto desaparece.

### base22 · `anamorph_ghost`

Un fantasma estirado en horizontal y desenfocado flota detrás de la imagen. El fantasma es el frame anterior, no una copia del actual.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uGhost` | Ghost | 0.0 – 1.0 | 0.50 |
| 2 | velocidad | `uGhostDecay` | Ghostdecay | 0.80 – 0.99 | 0.93 |
| 3 | distorsión | `uStretch` | Stretch | 1.0 – 4.0 | 2.20 |
| 4 | color | `uGhostTint` | Ghosttint | RGBA | `(0.55, 0.62, 1.0)` |
| 5 | firma | `uOffsetX` | Offsetx | −0.15 – 0.15 | 0.04 |

Extras: `uBlur` (Blur) 0.0–0.03 def 0.010

Audio: Ghost, `Low`. El desenfoque es un box blur de 5 muestras horizontales, no gaussiano — más barato y el estiramiento lo disimula.

### base23 · `retrato_focal`

Nítido en el centro, disolución acuarela hacia afuera. La periferia acumula, así que la acuarela se va formando sola durante la rola.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uSoftness` | Softness | 0.0 – 1.0 | 0.60 |
| 2 | velocidad | `uFlow` | Flow | 0.0 – 0.02 | 0.005 |
| 3 | distorsión | `uSpread` | Spread | 0.0 – 0.05 | 0.018 |
| 4 | color | `uDesat` | Desat | 0.0 – 1.0 | 0.35 |
| 5 | firma | `uFocusRadius` | Focusradius | 0.10 – 0.80 | 0.38 |

Extras: `uFocusSoft` (Focussoft) 0.05–0.50 def 0.25 · `uDecay` (Decay) 0.85–0.99 def 0.95

Audio: Softness, `Mid`.

**Nota:** `nucleo_frio` y `retrato_focal` comparten la idea de máscara central. La diferencia es el carácter — `nucleo_frio` deforma con gradiente de luminancia (líquido, direccional), `retrato_focal` difunde y desatura (acuarela, sin dirección). Mantenerlos distintos al escribir los shaders; si terminan pareciéndose, `retrato_focal` es el prescindible.

### base24 · `breath_zoom` — **el audio-reactivo del set**

Zoom y rotación acumulativos → túnel que respira con el bajo. Es donde la reactividad se siente sin volverse trigger.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uBreath` | Breath | 0.0 – 0.06 | 0.018 |
| 2 | velocidad | `uRate` | Rate | 0.05 – 1.5 | 0.28 |
| 3 | distorsión | `uSwirl` | Swirl | −0.03 – 0.03 | 0.006 |
| 4 | color | `uTunnelTint` | Tunneltint | RGBA | `(0.42, 0.30, 0.72)` |
| 5 | firma | `uDecay` | Decay | 0.85 – 0.995 | 0.955 |

Extras: `uMix` (Mix) 0.05–0.60 def 0.25

Audio: Breath, `Low`. La respiración es `sin(uTime * uRate * TWO_PI)` **más** la energía de audio, ambas pasadas por `smoothstep`. Nunca conectar la energía cruda al zoom.

### base38 · `cortina_franjas` — **acento**

Franjas horizontales donde cada una lee el feedback a distinta profundidad temporal. Una cortina hecha de tiempo.

| Slot | Rol | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|---|
| 1 | intensidad | `uReveal` | Reveal | 0.0 – 1.0 | 0.60 |
| 2 | velocidad | `uScroll` | Scroll | −1.0 – 1.0 | 0.15 |
| 3 | distorsión | `uSkew` | Skew | 0.0 – 0.30 | 0.0 |
| 4 | color | `uTintLag` | Tintlag | RGBA | `(1.0, 0.72, 0.30)` |
| 5 | firma | `uBands` | Bands | 2.0 – 48.0 | 12.0 |

Extras: `uLagDecay` (Lagdecay) 0.85–0.995 def 0.97

Audio: Reveal, `Mid`. La profundidad temporal por franja se logra variando el decay efectivo según `fract(uv.y * uBands)`, no con múltiples buffers.

---

## 9. Visuales — specs

Convención snake_case, `GENERATIVE_ONLY = True`, sin `u_input`. Los tres `u_color1/2/3` son pickers RGBA para armar la paleta en vivo.

### base1 · `grano_degradado` — **fondo continuo**

Degradado de tres colores con grano analógico y drift lentísimo. El fondo que puede estar puesto toda la noche sin cansar.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_grain` | Grain | 0.0 – 0.60 | 0.18 |
| 2 | `u_drift` | Drift | 0.0 – 0.30 | 0.05 |
| 3 | `u_warp` | Warp | 0.0 – 1.0 | 0.25 |
| 4 | `u_blend` | Blend | 0.0 – 1.0 | 0.50 |
| 5 | `u_angle` | Angle | 0.0 – 6.283 | 1.20 |

Extras: `u_vignette` (Vignette) 0.0–1.0 def 0.30
Colores: crema `#F4EDE4` · rosa `#E86A92` · violeta `#6C4AB6`
Audio: Grain, `Low`.

### base2 · `liquid_light` — **look base fuerte**

Oil & water sesentero: blobs de aceite que se dividen y se funden. Metaballs con domain warping, no fbm suelto — el borde definido es lo que lo hace leer como aceite proyectado y no como humo.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_amount` | Amount | 0.0 – 1.0 | 0.70 |
| 2 | `u_speed` | Speed | 0.0 – 1.5 | 0.22 |
| 3 | `u_warp` | Warp | 0.0 – 2.0 | 0.85 |
| 4 | `u_sat` | Sat | 0.0 – 2.0 | 1.15 |
| 5 | `u_blob_scale` | Blobscale | 0.5 – 6.0 | 2.20 |

Extras: `u_edge` (Edge) 0.0–1.0 def 0.35
Colores: ámbar `#F2B33D` · turquesa `#2AA79B` · rosa `#E86A92`
Audio: Warp, `Low`.

### base3 · `niebla_capas` — **fondo atmosférico**

Capas de niebla con paralax y un haz de luz atravesándolas. Penumbra de trip-hop.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_density` | Density | 0.0 – 1.5 | 0.55 |
| 2 | `u_speed` | Speed | 0.0 – 0.60 | 0.10 |
| 3 | `u_paralax` | Paralax | 0.0 – 1.0 | 0.45 |
| 4 | `u_light_mix` | Lightmix | 0.0 – 1.0 | 0.60 |
| 5 | `u_layers` | Layers | 2.0 – 6.0 | 4.0 |

Extras: `u_beam` (Beam) 0.0–1.0 def 0.30
Colores: negro violáceo `#151020` · violeta `#6C4AB6` · crema `#F4EDE4`
Audio: Density, `Low`.

**Nota:** `u_layers` es float en el parámetro pero debe usarse como `int(u_layers)` en el shader con cadena `if / else if` — TD no soporta dynamic array indexing ni loops de longitud variable limpia.

### base4 · `humo_tinta`

Tinta en agua: columnas de fbm advectado que suben y se difunden.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_amount` | Amount | 0.0 – 1.0 | 0.65 |
| 2 | `u_rise` | Rise | 0.0 – 1.0 | 0.25 |
| 3 | `u_turbulence` | Turbulence | 0.0 – 3.0 | 1.20 |
| 4 | `u_ink_mix` | Inkmix | 0.0 – 1.0 | 0.55 |
| 5 | `u_diffusion` | Diffusion | 0.0 – 1.0 | 0.40 |

Extras: `u_octaves` (Octaves) 2.0–6.0 def 4.0 (mismo tratamiento `if/else if`)
Colores: violeta `#6C4AB6` · turquesa `#2AA79B` · crema `#F4EDE4`
Audio: Turbulence, `Mid`.

### base5 · `campo_bokeh`

Círculos desenfocados que entran y salen de foco, respirando. Lo más literalmente dream pop del set.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_amount` | Amount | 0.0 – 1.0 | 0.70 |
| 2 | `u_speed` | Speed | 0.0 – 0.80 | 0.18 |
| 3 | `u_defocus` | Defocus | 0.0 – 1.0 | 0.55 |
| 4 | `u_color_spread` | Colorspread | 0.0 – 1.0 | 0.50 |
| 5 | `u_count` | Count | 4.0 – 48.0 | 18.0 |

Extras: `u_size` (Size) 0.02–0.35 def 0.12
Colores: ámbar `#F2B33D` · rosa `#E86A92` · crema `#F4EDE4`
Audio: Defocus, `High`.

**Implementación:** hash por celda en una rejilla, no un loop sobre `u_count` partículas. Mantiene el costo constante y evita el problema de indexing.

### base6 · `mareas_color`

Dos frentes de color que se invaden mutuamente con un borde iridiscente donde se tocan.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_amount` | Amount | 0.0 – 1.0 | 0.80 |
| 2 | `u_speed` | Speed | 0.0 – 0.80 | 0.15 |
| 3 | `u_turbulence` | Turbulence | 0.0 – 2.0 | 0.70 |
| 4 | `u_iridescence` | Iridescence | 0.0 – 1.0 | 0.50 |
| 5 | `u_front` | Front | 0.0 – 1.0 | 0.50 |

Extras: `u_edge_width` (Edgewidth) 0.005–0.15 def 0.04
Colores: turquesa `#2AA79B` · ámbar `#F2B33D` · rosa `#E86A92`
Audio: Front, `Low`.

### base7 · `eclipse`

Anillo de luz con corona; el disco central respira. Guiño a *Meddle*, geometría simple.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_corona` | Corona | 0.0 – 1.5 | 0.60 |
| 2 | `u_speed` | Speed | 0.0 – 1.0 | 0.20 |
| 3 | `u_wobble` | Wobble | 0.0 – 0.20 | 0.03 |
| 4 | `u_ring_mix` | Ringmix | 0.0 – 1.0 | 0.60 |
| 5 | `u_radius` | Radius | 0.10 – 0.60 | 0.28 |

Extras: `u_thickness` (Thickness) 0.002–0.08 def 0.012
Colores: ámbar `#F2B33D` · negro violáceo `#151020` · rosa `#E86A92`
Audio: Radius, `Low` — el disco respira con el bajo.

### base8 · `cuerdas`

Líneas verticales que vibran con motion blur. Reactivas a agudos: es el visual de los solos con fuzz.

| Slot | Uniform | Parámetro | Rango | Default |
|---|---|---|---|---|
| 1 | `u_amount` | Amount | 0.0 – 1.0 | 0.70 |
| 2 | `u_speed` | Speed | 0.0 – 4.0 | 1.40 |
| 3 | `u_amplitude` | Amplitude | 0.0 – 0.15 | 0.03 |
| 4 | `u_color_shift` | Colorshift | 0.0 – 1.0 | 0.40 |
| 5 | `u_count` | Count | 3.0 – 64.0 | 16.0 |

Extras: `u_blur` (Blur) 0.0–0.05 def 0.012
Colores: crema `#F4EDE4` · violeta `#6C4AB6` · turquesa `#2AA79B`
Audio: Amplitude, `High`.

---

## 10. Orden de construcción

Construir y **verificar en TD** cada tanda antes de pasar a la siguiente. Si el tiempo se acaba, lo construido debe funcionar como show coherente por sí solo.

**Tanda 1 — el show mínimo viable**
1. base18 `nucleo_frio`
2. base19 `soft_halate`
3. base1 `grano_degradado`
4. base2 `liquid_light`

Con estos cuatro ya se puede tocar el show completo: dos efectos de look base y dos visuales (uno de fondo, uno fuerte).

**Tanda 2 — rango expresivo**
5. base24 `breath_zoom`
6. base20 `eco_lento`
7. base3 `niebla_capas`
8. base5 `campo_bokeh`

**Tanda 3 — el resto**
9. base21 `dos_voces`
10. base23 `retrato_focal`
11. base22 `anamorph_ghost`
12. base38 `cortina_franjas`
13. base4 `humo_tinta`
14. base6 `mareas_color`
15. base7 `eclipse`
16. base8 `cuerdas`

## 11. Backlog

No construir salvo que sobre tiempo después de la Tanda 3.

**Efectos:** `fuzz_edge`, `espejo_agua`, `doble_exposicion`, `prisma_suave`, `contraluz`, `cristal_liquido`, `solarize_dulce`, `sangrado_lateral`, `grano_16mm` (sin feedback), `vhs_dulce` (sin feedback)

**Visuales:** `horizonte_fuzz`, `ondas_estanque`, `polvo_estelar`, `rejilla_blanda`, `dos_lunas`, `vitral_liquido`, `espiral_lenta`, `ruido_terciopelo`

**Reusables del set de feedback filters de Sebas** (confirmar con él que no estén quemados del Psych Fest): `Liquid Memory (03)` es el más afín a esta dirección; `Memory Marbling (07)` funciona como acento psicodélico; `RGB Trail Decay (02)` con `uDecay` alto y `uMix` alto queda delicado. `Plasma Currents (05)` y `Spectral Mitosis (06)` sólo como acento breve — subidos disuelven a la banda.

## 12. Checklist de verificación en TD

Por cada base construida:

- [ ] El GLSL TOP compila sin errores en el TextPort
- [ ] Cero warnings de tipo `Uniform 'X' is not assigned`
- [ ] Pixel format = 16-bit float en GLSL TOP **y** Feedback TOP
- [ ] `Bypass` corta a passthrough limpio
- [ ] Los 5 sliders mueven algo visible en todo su rango
- [ ] `Audiotarget` empuja el slider correcto y `Audiomult` a 0 lo desactiva
- [ ] Con el fader de intensidad al máximo, las caras siguen reconocibles
- [ ] El feedback no satura a blanco tras 5 minutos corriendo
- [ ] `bgtop = ./out1` en la pestaña Look del contenedor

Al cerrar el proyecto: anotar en `LEARNINGS.md` qué rangos se sintieron bien en vivo, qué se rompió, y copiar a `library/` los shaders que valga la pena reusar.
