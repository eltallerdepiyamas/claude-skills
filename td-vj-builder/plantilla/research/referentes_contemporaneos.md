# Referentes contemporáneos: el nivel al que apuntan los visuales

Los visuales de cada show tienen que verse como lo que hoy se presenta en festivales de arte audiovisual,
no como presets de VJ. Esta guía es la base común. Cada proyecto suma sus referencias propias en
`research/` (marca, artista y contexto), pero el estándar de oficio sale de aquí.

Revísala antes de proponer visuales nuevos y cuando el usuario pida "algo más chido / más propositivo".
Actualízala cuando aparezca un referente o una técnica que valga la pena (fecha y fuente).

## Dónde mirar

**Festivales.** Sus archivos de AV performances están en Vimeo y YouTube. Busca: `<festival> <año> AV performance`.
- MUTEK: Montreal, México, Barcelona, Japón, San Francisco y otras sedes. Es el referente principal de AV en vivo.
- Sónar+D (Barcelona), CTM (Berlín), Berlin Atonal, Unsound (Cracovia), Ars Electronica (Linz),
  Decibel (Seattle), MIRA (Barcelona), Semibreve (Braga), KIKK (Namur), Scopitone (Nantes).

**Artistas y estudios** (qué mirar de cada uno):
- Ryoji Ikeda (*test pattern*, *data.tron*): datos en blanco y negro sincronizados al frame. Rigor y ritmo.
- Robert Henke (*Lumière*, *CBM 8032*): láser y vector sobre negro. Pocas líneas, mucha precisión.
- Alva Noto / raster-noton: minimalismo gráfico, grids, glitch controlado.
- Joanie Lemercier (*Fuji*, *Edges*): paisajes de líneas, proyección sobre volumen, luz como dibujo.
- NONOTAK (*Daydream*): capas de líneas de luz y profundidad sin cámara 3D.
- Refik Anadol (*Machine Hallucinations*): fluidos y partículas a escala arquitectónica.
- Max Cooper (*Emergence*, *Yearning for the Infinite*) y quienes hacen sus videos: sistemas y procesos naturales.
- Rhizomatiks / Daito Manabe: datos de cuerpo y sonido, precisión técnica.
- Weirdcore: distorsión digital, time glitch y deformación con intención.
- 1024 architecture, Tundra, Ouchhh: escenografía de luz y mapping.

**Técnica en TouchDesigner.** Bileam Tschepe (elekktronaut), Paketa12, Torin Blankensmith, Supermarket Sallad,
el showcase de Derivative y Interactive & Immersive HQ. Para shaders: Shadertoy y los artículos de Inigo Quilez.

## Qué tienen en común (el criterio)

1. **El negro manda.** El fondo respira; la imagen ocupa una parte de la pantalla, no la satura toda.
2. **Una sola tinta** (más un acento) y luz cerca del blanco solo en los núcleos. Va con las paletas de marca.
3. **Líneas finas y antialias limpio.** Lo grueso y borroso se ve barato.
4. **Movimiento lento + golpes exactos.** La base es fluida; el kick cambia algo de forma clara (figura, semilla, corte).
5. **El audio se lee.** Quien ve debe entender qué parte responde a qué banda. Nada de todo-temblando.
6. **Sistemas, no plantillas.** Simulaciones, historia del audio, feedback y tiempo: algo que evoluciona y no se repite.
7. **Profundidad sin túnel.** Perspectiva, paralaje o capas; evita el túnel, el caleidoscopio, el arcoíris y el strobe agresivo.
8. **Presupuesto en vivo.** 1080p a 60 fps en la máquina del show: simulaciones a media resolución, feedback en 16 bits.

## Técnica → cómo se arma aquí → ejemplo en library/

| Look | Técnica en TD | Ejemplo |
|---|---|---|
| Montaña de líneas con el track (ridgeline) | historia del audio en una textura 1×128 con feedback + líneas con oclusión | `visuals/cordillera.glsl` (+ `cordillera_hist.glsl`) |
| Láser en humo | haces analíticos + ruido de humo + feedback de fósforo; el kick cambia la figura (`kick_step`) | `visuals/laser.glsl` |
| Hilos de humo / seda | feedback advectado por curl noise, emisores finos | `visuals/seda.glsl` |
| Coral / laberinto orgánico | Gray-Scott en red propia (6 pasos por cuadro, float32), el kick siembra | `visuals/reaccion.glsl` (+ `reaccion_sim.glsl`) |
| Slit scan / time glitch | Texture 3D (cache) + Time Machine con un mapa de tiempo | `visuals/slit_scan*.glsl` |
| Cortinas de luz / moiré | capas de líneas con paralaje y aberturas que abre el bajo | `visuals/cortinas.glsl` |
| Pixel sort / derretido digital | feedback con umbral: lo brillante gotea por columnas | `visuals/pixel_sort.glsl` |
| Luz a través de líquido | cáusticas: dos capas de voronoi (F2−F1) deformadas, destellos en los nudos | `visuals/ron_liquido_causticas.glsl` |

Siguientes a explorar (no hechos aún): atractores con millones de puntos (POPs / instancing, ver skill `td-pops`),
point clouds de escaneo, campos de partículas con fluido real, raymarching volumétrico de humo, láser vectorial
con Line MAT y bloom.

## Cómo usarla en un show

- En la propuesta, nombra el referente y la técnica de cada visual (una línea): ayuda a vender la idea y a medirla.
- Antes de dar un visual por bueno, revísalo contra los 8 puntos del criterio.
- Las referencias del cliente (marca, ediciones pasadas) mandan en el contenido; esta guía manda en el oficio.
