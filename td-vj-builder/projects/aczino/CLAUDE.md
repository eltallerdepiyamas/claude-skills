# PROYECTO: ACZINO — Batalla de Freestyle (Explanada de la Delegación)

Generado por td-vj-builder. Contexto en disco para este show.

## Rutas
- Proyecto .toe: `E:/tiani/Documents/Touch Designer Projects/01. EDITABLES/ACZINO/`
- Brief: `ACZINO.md` (mismo folder)
- Shaders de efectos:  `effects_glsl/shaders/`
- Builders de efectos: `effects_glsl/builders/`
- Shaders de visuales: `visuals_glsl/shaders/`
- Builders de visuales: `visuals_glsl/builders/`
- Audio canónico (audio_in): `../../project1/null4`  (canales: low mid high)

## Rig (fijo — no renombrar bases)
- Visuales:  base1–base16
- base17:    host de cámaras / escena_modular / layouts (layout_*)
- Efectos:   base18–base24, luego base38–base45

## CONVENCIONES ESPECÍFICAS DE ESTE SHOW

### Cámaras
- **1 sola cámara.** Los efectos siguen funcionando idénticos (1 input al GLSL).
  Los layouts multi-cam (cara_a_cara, triángulo, etc.) NO aplican literalmente
  — solo `plano_plaza` queda nativo; el resto se convierte en efectos de
  duplicación/espejo (Mirror VS, etc.).

### Resolución de los GLSL TOP (visuales)
- **Output Resolution = Custom** en la página Common.
- **`resolutionw`** ligado a `parent(2).op('constant45')['resX']`
- **`resolutionh`** ligado a `parent(2).op('constant45')['resY']`
- `parent(2)` desde `/project2/baseN` = raíz `/`. El CHOP `constant45` vive en
  raíz y publica los canales `resX` y `resY` (notación con corchetes = lee
  el valor del channel del CHOP).
- En los EFECTOS (base18–24) seguimos con `outputresolution = useinput`: el
  efecto hereda el tamaño del video que le entra (cámara). Si el usuario
  quiere también ligarlos a `/constant45`, se cambia a Custom con la misma
  expresión.

### Uniforms en visuales
- `u_res` sigue ligado a `me.width`/`me.height` del GLSL TOP — como el TOP ya
  está ligado a `/constant45`, el uniform refleja automáticamente esa resolución.

## Bases ocupadas en este show

### Efectos
| Base | Nombre | Shader | Feedback | Audio default | Notas |
|------|--------|--------|----------|---------------|-------|
| base18 | RGBSplit ACZINO | `rgb_split.frag` | no | LOW → Splitamount (×1.5) | Tints VS (sangre R / cian neón B), tear bars random |
| base19 | EdgeContorno | `edge_contorno.frag` | no | MID → Edgestrength | Look base diurno (Sobel + pre-blur espacial) |
| base20 | StencilNeza | `stencil_neza.frag` | no | LOW → Stencilstrength | Aerosol + concreto procedural + drips |
| base21 | FeedbackTrails | `feedback_trails.frag` | **sí** (16f) | LOW → Feedbackamt | Nocturno. Decay exponencial |
| base22 | Datamosh | `datamosh.frag` | **sí** (16f) | MID → Motionthreshold | No sostener en retrato. Voz = freeze |
| base23 | CartelBoxeo | `cartel_boxeo.frag` | no | HIGH → Halftonedensity | Poster fight night CMYK + bordes despegados |
| base24 | GlifoPrehispanico | `glifo_prehispanico.frag` | no | LOW → Pulserate | Grecas polares + glitch tech (Onionlab homenaje) |

### Visuales
| Base | Nombre | Shader | Tipo | Audio default |
|------|--------|--------|------|---------------|
| base1  | MuroNeza         | `01_muro_neza.glsl`         | generativo puro    | LOW → Tagdensity |
| base2  | VersusCartel     | `02_versus_cartel.glsl`     | generativo puro    | LOW → Vsscale |
| base3  | GlifoFuturista   | `03_glifo_futurista.glsl`   | generativo puro    | LOW → Glyphdepth |
| base4  | OroGOAT          | `04_oro_goat.glsl`          | generativo puro    | LOW → Particledensity |
| base5  | SangreEnTinta    | `05_sangre_en_tinta.glsl`   | generativo puro    | LOW → Inkamount |
| base6  | Vinilo50         | `06_vinilo_50.glsl`         | generativo puro    | HIGH → Grainamount |
| base7  | HumoDeBarrio     | `07_humo_de_barrio.glsl`    | generativo puro    | LOW → Smokedensity |
| base8  | ReticulaSonidera | `08_reticula_sonidera.glsl` | generativo puro    | LOW → Cellbright |
| base9  | SiluetaEspejo*   | `09_silueta_espejo.glsl`    | mezcla con cam     | LOW → Silhouette |
| base10 | ContornoVivo     | `10_contorno_vivo.glsl`     | mezcla con cam     | MID → Edgestrength |
| base11 | DuotonoCalle     | `11_duotono_calle.glsl`     | mezcla con cam     | LOW → Halftonescale |
| base12 | EcoPunchline     | `12_eco_punchline.glsl`     | mezcla con cam     | LOW → Echodepth |
| base13 | MosaicoMC*       | `13_mosaico_mc.glsl`        | mezcla con cam     | LOW → Pulserate |
| base14 | AuraCampeon      | `14_aura_campeon.glsl`      | mezcla con cam     | LOW → Auraintensity |

\* adaptados a 1 cámara (originales del brief eran multi-cam)

### Convenciones por tipo
- **Visuales generativos puros (base1–8):** outputresolution=Custom, `resolutionw/h` ligados a `parent(2).op('constant45')['resX'/'resY']`.
- **Visuales mezcla con cam (base9–14):** outputresolution=useinput (heredan tamaño del feed). NO ligan a `/constant45`.
- **Efectos (base18–24):** outputresolution=useinput (idem).

## Layouts en este show (dentro de base17/escena_modular)
| Nombre | Cámaras | Notas |
|--------|---------|-------|
| (ninguno aún — pendiente con 1-cam) | | |

## Contrato de parámetros
- 5 sliders por rol fijo: intensidad, velocidad, distorsión, color, firma.
- Bypass aparte. Página Audio: Audioreact + Low/Mid/High + Audiotarget + Audiomult.
- Audio se suma en la expresión del uniform (clamp), no en el slider.
- **RGBA en slot 4:** no acepta inyección de audio (audio es escalar, color es vec3).
  El binding asigna los 3 componentes RGB directos del Custom Parameter, sin
  audio. Si querés audio en slot 4, usa float ahí y mete RGBA como extra.

## Decisiones creativas confirmadas
- Tints VS en RGB Split (R=sangre, B=cian neón) — lectura cara-a-cara instantánea.
- Stencil Neza reemplaza al Duotono genérico (raíz graffiti).
- Cartel Boxeo reemplaza al Scanline VHS (poster fight night CMYK).
- Glifo Prehispánico reemplaza al Mirror VS (Onionlab homenaje).
- Visuales priorizan identidad Aczino (Neza, prehispánico, GOAT, paleta sangre/oro/jade)
  sobre conceptos genéricos.

## Cómo correr un builder
Pegar el `setup_baseXX_<name>.py` en un Text DAT dentro de `/project2/baseXX` → Run.
(O `exec(open(...).read())` desde el Textport.)

## Notas del show (libre — el skill no borra esto)
- 
