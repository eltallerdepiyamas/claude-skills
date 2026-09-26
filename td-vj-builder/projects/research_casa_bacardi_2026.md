# PROYECTO: CASA BACARDI — Booth Interactivo / Festivales 2026

> Brief de dirección creativa para td-vj-builder.
> Edición 3. Pantalla LED 16:9 agregada esta temporada.

---

## 1. Meta del show

- **Contexto:** Booth interactivo itinerante en festivales de música, México 2026.
  Tres ediciones acumuladas. Esta temporada incorpora pantalla LED independiente
  como superficie de experiencia interactiva.
- **Duración:** Continuo durante el festival (horas). Los efectos deben funcionar
  solos sin intervención constante y aguantar fatiga visual.
- **Luz ambiente:** Variable — mezcla de luz de día, penumbra de carpa/booth, y
  luz de escenario. Los efectos deben funcionar legibles en condiciones mixtas.
- **Tono emocional:** Festivo, energético, premium, sensorial. Fiesta de verdad,
  no rave. Movimiento continuo sin agresividad.
- **Interacción:** La cámara/YOLO detecta al visitante frente a la pantalla.
  El efecto reacciona a su presencia, posición o movimiento corporal.
  No requiere instrucciones — debe ser intuitivo e inmediato.

---

## 2. Dirección visual

### Paleta (oficial — Pantone confirmado)
| Rol            | Color                  | Hex       | Pantone     | CMYK              | RGB (lin.)         |
|----------------|------------------------|-----------|-------------|-------------------|--------------------|
| **Primario**   | Rojo Bacardi           | #FF1F3A   | 185 C       | C:0 M:100 Y:82 K:0 | 1.0, 0.12, 0.22   |
| **Secundario** | Verde menta Bacardi    | #6DC49A   | 346 C       | C:58 M:0 Y:52 K:0  | 0.43, 0.77, 0.60  |
| **Neutro luz** | Blanco cálido          | #F5F0E8   | —           | —                 | 0.96, 0.94, 0.91   |
| **Neutro oscuro** | Negro profundo      | #0A0A0A   | —           | —                 | 0.04, 0.04, 0.04   |

> Estos son los únicos colores de marca. En los shaders, `uColorA` = rojo, `uColorB` = verde menta.
> Todos los efectos exponen sus colores como RGBA pickers en la página Filter para poder ajustarlos en vivo.

### Referencias estéticas
1. **Ron del Caribe / tropical premium** — movimiento de agua, luz filtrada,
   calor húmedo. Extraer: refracción, ondas lentas, brillo difuso.
2. **Carnaval latinoamericano** — energía colectiva, color saturado, ritmo.
   Extraer: pulso de beat, destellos, presencia de multitud.
3. **Fotografía de fiesta nocturna** — bokeh, luz de flash, halos.
   Extraer: glow suave, aberración cromática controlada, grain analógico.
4. **Motion graphics de marca premium** — limpieza, legibilidad, tipografía en
   movimiento. Extraer: no saturar la pantalla, dejar respirar el espacio.

### Evitar
- Efectos de festival genérico (kaleidoscopio, tunnel warp, arcoíris random)
- Abstracción total — el visitante debe verse reconocible en todo momento
- Strobe agresivo (es un espacio público con visitantes de todas las edades)
- Paleta fría o desaturada (no encaja con la marca)

---

## 3. Contexto de cámara y tracking

- **Fuente:** Webcam única frente al booth (plano medio-frontal del visitante)
- **YOLO disponible:** face tracking, object tracking, pose estimation
  (keypoints: hombros, codos, muñecas, caderas, rodillas)
- **Datos útiles para shaders:**
  - Posición del rostro (centro x/y normalizado) → atracción/repulsión de efectos
  - Bounding box del cuerpo → máscara dinámica de intensidad
  - Velocidad de movimiento (diferencia frame a frame del bbox) → trigger de energía
- **Legibilidad:** El visitante SIEMPRE debe reconocerse. El efecto vive en
  capas alrededor/encima del feed, nunca lo reemplaza por completo.
- **Plano:** Retrato / plano medio. El rostro ocupa el tercio superior de la imagen.

---

## 4. Audio

- **Banda dominante:** Low (bass) — la música en festivales es predominantemente
  bass-forward (electrónica, reggaeton, latin pop).
- **Carácter de reactividad:** Pulso de beat suave — los efectos "respiran" con
  el bajo, no disparan de forma abrupta. El visitante está en el booth, no en el
  dancefloor principal; la experiencia debe sentirse íntima, no agresiva.
- **Recomendación de Audiotarget por defecto:** slot 1 (intensidad) para la mayoría
  de efectos. El slot 2 (velocidad) como segunda opción para efectos con movimiento.

---

## 5. Qué crear

### Efectos de cámara (filtros sobre el feed de webcam)

> base18 ya existe — empezar desde base19.
> Todos usan `sTD2DInputs[0]` para el feed de cámara.
> Feedback opcional en `sTD2DInputs[1]`.
> La posición del rostro/cuerpo de YOLO puede pasarse como uniform adicional (vec2 uFacePos, float uPresence).

---

**Efecto 1 — `liquid_gold`** (base19)
*Feed de cámara bañado en distorsión fluida dorada. Como ver tu reflejo en ron derramado.*
Feedback: sí.

| Slot | Rol         | Uniform          | Parámetro      | Rango         |
|------|-------------|------------------|----------------|---------------|
| 1    | Intensidad  | uWarpAmount      | Warpamount     | 0.0 – 0.08   |
| 2    | Velocidad   | uFlowSpeed       | Flowspeed      | 0.1 – 2.0    |
| 3    | Distorsión  | uNoiseScale      | Noisescale     | 2.0 – 20.0   |
| 4    | Color       | uColorA / uColorB | Colora / Colorb | RGBA picker — default: rojo #FF1F3A / verde menta #6DC49A |
| 5    | Firma       | uFeedbackDecay   | Feedbackdecay  | 0.80 – 0.97  |

Audio: Low → slot 1 (intensidad del warp). uPresence (YOLO) amplifica el warp cerca del rostro.

---

**Efecto 2 — `halo_glow`** (base20)
*Halo luminoso que rodea la silueta del visitante. Como luz de flash congelada.*
Feedback: no.

| Slot | Rol         | Uniform          | Parámetro      | Rango         |
|------|-------------|------------------|----------------|---------------|
| 1    | Intensidad  | uGlowRadius      | Glowradius     | 0.001 – 0.05 |
| 2    | Velocidad   | uPulseSpeed      | Pulsespeed     | 0.2 – 3.0    |
| 3    | Distorsión  | uEdgeSoftness    | Edgesoftness   | 0.0 – 1.0    |
| 4    | Color       | uHaloColor       | Halocolor      | RGBA picker — default: rojo #FF1F3A |
| 5    | Firma       | uChromaSplit     | Chromasplit    | 0.0 – 0.015  |

Audio: Low → slot 1 (radio del halo). uFacePos (YOLO) centra el halo en el rostro.

---

**Efecto 3 — `echo_trails`** (base21)
*Estela de movimiento que sigue al cuerpo — como exposición múltiple en movimiento.*
Feedback: sí.

| Slot | Rol         | Uniform          | Parámetro      | Rango         |
|------|-------------|------------------|----------------|---------------|
| 1    | Intensidad  | uTrailOpacity    | Trailopacity   | 0.0 – 1.0    |
| 2    | Velocidad   | uDecayRate       | Decayrate      | 0.80 – 0.98  |
| 3    | Distorsión  | uDriftAmount     | Driftamount    | 0.0 – 0.012  |
| 4    | Color       | uTintColor       | Tintcolor      | RGBA picker — default: verde menta #6DC49A |
| 5    | Firma       | uMotionBlur      | Motionblur     | 0.0 – 1.0    |

Audio: Low → slot 2 (velocidad de decay — más bass, estela más larga). uPresence → amplifica opacidad.

---

**Efecto 4 — `tropical_refract`** (base22)
*Refracción de luz como a través de agua o vidrio de botella. Premium y físico.*
Feedback: no.

| Slot | Rol         | Uniform          | Parámetro      | Rango         |
|------|-------------|------------------|----------------|---------------|
| 1    | Intensidad  | uRefractStrength | Refractstrength| 0.0 – 0.06   |
| 2    | Velocidad   | uWaveSpeed       | Wavespeed      | 0.1 – 1.5    |
| 3    | Distorsión  | uWaveFreq        | Wavefreq       | 1.0 – 12.0   |
| 4    | Color       | uChromaticAb     | Chromaticab    | 0.0 – 0.01   |
| 5    | Firma       | uCausticAmt      | Causticamt     | 0.0 – 1.0    |

Audio: Low → slot 1 (fuerza de refracción). Sin YOLO en este efecto — funciona bien como fondo continuo.

---

**Efecto 5 — `body_displacement`** (base23)
*El cuerpo del visitante deforma el espacio a su alrededor — campo de distorsión orgánica.*
Feedback: sí. Uso intensivo de YOLO (pose keypoints como fuente del campo de distorsión).

| Slot | Rol         | Uniform           | Parámetro       | Rango         |
|------|-------------|-------------------|-----------------|---------------|
| 1    | Intensidad  | uDispStrength     | Dispstrength    | 0.0 – 0.1    |
| 2    | Velocidad   | uFieldSpeed       | Fieldspeed      | 0.1 – 2.0    |
| 3    | Distorsión  | uFieldRadius      | Fieldradius     | 0.05 – 0.5   |
| 4    | Color       | uDistortTint      | Distorttint     | 0.0 – 1.0    |
| 5    | Firma       | uFeedbackMix      | Feedbackmix     | 0.0 – 0.9    |

Audio: Low → slot 1. uFacePos + uBodyCenter (YOLO) → origen del campo de distorsión.

---

### Convención de color en los builders

Todo efecto que tenga slot 4 = color expone **dos RGBA pickers** en la página Filter:
- `Colora` → color primario (default: rojo Bacardi `1.0, 0.122, 0.227, 1.0`)
- `Colorb` → color secundario (default: verde menta `0.427, 0.769, 0.604, 1.0`)

Se bindan como uniforms vec3 en la página Vectors:
```python
COLOR_UNIFORMS = [
    ('uColorA', 'Colora', (1.0,  0.122, 0.227, 1.0)),   # #FF1F3A Rojo Bacardi
    ('uColorB', 'Colorb', (0.427, 0.769, 0.604, 1.0)),  # #6DC49A Verde menta
]
```

Esto garantiza que Sebas pueda ajustar cualquier color en vivo desde la UI de TD
sin tocar el shader. El shader usa `uColorA` y `uColorB` como `uniform vec3`.

---

### Uniforms de YOLO (adicionales al contrato de 5 — declarar en SIGNATURE_EXTRAS)

Estos uniforms se alimentan desde CHOPs de YOLO vía expresiones en la página Vectors.
No forman parte de los 5 macros, pero se exponen en la página Filter del base.

```
uFaceX     float  op('yolo_in')['x']              — posición horizontal (0=izq, 1=der)
uFaceY     float  1.0 - op('yolo_in')['y']        — posición vertical invertida para GLSL
uPresence  float  op('yolo_in')['width']           — 0=nadie, >0.1=persona detectada
uScore     float  op('yolo_in')['score']           — confianza; gate si < 0.4
```

Sebas conecta manualmente los CHOPs de YOLO a las expresiones — los builders
dejan los uniforms declarados con valor default `0.5` como fallback.

---

## 6. Prioridad de uso

### Look base (correr continuamente)
- `liquid_gold` (base19) — efecto de bienvenida, siempre activo
- `tropical_refract` (base22) — fondo cuando no hay interacción intensa

### Acentos (activar en momento de mayor energía)
- `halo_glow` (base20) — cuando hay rostro detectado claramente
- `echo_trails` (base21) — cuando hay movimiento sostenido
- `body_displacement` (base23) — efecto wow, para momentos pico

### Flujo sugerido durante la sesión de un visitante
```
Visitante se acerca  → liquid_gold (bienvenida suave)
Visitante se detiene → halo_glow se activa (rostro detectado)
Visitante se mueve   → echo_trails (estela de movimiento)
Momento pico / bass  → body_displacement (máxima interacción)
Visitante se va      → fade back a liquid_gold
```
