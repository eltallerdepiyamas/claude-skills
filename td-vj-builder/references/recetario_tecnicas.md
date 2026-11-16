# Recetario de técnicas: de "quiero algo como X" a una base del rig

Investigación del 2026-11-16. Complementa `referentes_contemporaneos.md` (el criterio de 8 puntos y el
"dónde mirar"); aquí está el **cómo**: una receta por técnica, armable en un `baseN` de /project2 con el
contrato de 5 sliders y la paleta de 2 colores.

Orden del archivo: **índice → atlas de perfiles** (artistas · síntesis de video · TouchDesigner · instituciones)
**→ recetas 1-44** (A datos · B feedback · C simulaciones · D partículas · E tiempo/glitch · F formas/3D ·
G síntesis de video y emulación LZX) **→ top 10 para el próximo show → fuentes no verificadas**.

Convenciones que usan todas las recetas:
- Uniforms del rig: `u_time`, `u_res`, `u_low/u_mid/u_high`, `u_kick` (envolvente 0-1), `u_step` (contador de kicks),
  `u_color1/u_color2` (paleta sobre negro), `u_tono`.
- **S1** intensidad · **S2** velocidad · **S3** distorsión · **S4** color · **S5** firma (lo que más distingue al visual).
- **Color:** siempre `col = mix(u_color1, u_color2, t) * luz` sobre negro, con `t` saliendo de algo con sentido
  (edad, profundidad, banda, densidad). Blanco solo en los núcleos (`luz > 1` con tonemap suave). Nunca hue ni RGB.
- **Feedback:** Feedback TOP en 16-bit float (`rgba16float`); simulaciones (RD, fluido, physarum) en 32-bit float
  y a media resolución (960×540) con upscale al final.
- **Kick vs. bandas:** el kick cambia algo **discreto** (semilla, figura, corte, inyección) leyendo `u_step`
  (`hash(u_step)`), las bandas mueven cosas **continuas**. Así "el audio se lee".
- Estado: `ya en library: <archivo>` (en `library/visuals/` salvo que diga otra cosa) o `nueva`.

---

## Índice: "Quiero algo como…"

| Quiero algo como… | Receta |
|---|---|
| Ryoji Ikeda, barcodes, datos blanco y negro al frame | [1](#1-data-viz-tipo-ikeda-barcode--test-pattern) |
| Autómata celular, patrón binario que crece línea a línea | [2](#2-autómata-celular-1d2d) |
| Alva Noto / raster-noton, grids y test patterns | [3](#3-grid-de-test-pattern-raster-noton) |
| Estela, eco, memoria de imagen (feedback clásico) | [4](#4-feedback-básico-transform--level) |
| Feedback que se derrite / se pinta solo (feedback con displace) | [5](#5-feedback-con-displacement-feedback-líquido) |
| Contornos que se multiplican (edge feedback) | [6](#6-edge-feedback) |
| Brillo que respira y se acumula (bloom en el loop) | [7](#7-bloom-feedback) |
| Coral, laberinto, piel orgánica | [8](#8-reaction-diffusion-gray-scott) |
| Moho mucilaginoso, redes de transporte vivas | [9](#9-physarum-slime-mold) |
| Humo, tinta, fluido real (Refik Anadol "data pigments") | [10](#10-fluido-navier-stokes-stable-fluids) |
| Hilos de seda, flujos que no se cruzan | [11](#11-campos-de-flujo--curl-noise) |
| Mármol, domain warping, nebulosa lenta | [12](#12-domain-warping-fbm) |
| Millones de partículas, nube que respira | [13](#13-partículas-gpu-con-pops) |
| Atractores extraños (Lorenz, Aizawa, Thomas) | [14](#14-atractores-extraños) |
| Bandada, enjambre, cardumen | [15](#15-boids--flocking) |
| Plexus, red de nodos, constelación | [16](#16-red-de-nodos-plexus) |
| Línea que crece y se pliega (differential growth) | [17](#17-differential-line-growth) |
| Slit scan, tiempo que se estira | [18](#18-slit-scan--time-displacement) |
| Time glitch, bloques que vienen de otro instante (Weirdcore) | [19](#19-time-glitch-por-bloques) |
| Datamosh, la imagen arrastrada por el movimiento | [20](#20-datamosh--optical-flow-warp) |
| Pixel sort, derretido digital | [21](#21-pixel-sort) |
| Formas suaves que se funden, logo que se derrite en metaballs | [22](#22-sdf-2d-y-morph-de-formas) |
| Volumen de humo / objeto raymarcheado | [23](#23-raymarching-3d-y-volumétrico) |
| Cimática, placa de Chladni | [24](#24-cimática--chladni) |
| Láser vectorial, Robert Henke | [25](#25-láser--vector-sobre-negro) |
| Líneas de luz en capas, NONOTAK | [26](#26-capas-de-líneas-con-paralaje-nonotak) |
| Lemercier, paisaje de líneas, montañas | [27](#27-ridgeline--paisaje-de-líneas) |
| Instancing de retícula, tiles cinéticos | [28](#28-instancing-de-retícula-kinetic-tiles) |
| Point cloud / Gaussian splat del logo | [29](#29-point-cloud--gaussian-splats) |
| Max Cooper: matemáticas visibles (espiral de primos, filotaxis) | [30](#30-estructuras-matemáticas-espiral-de-primos-filotaxis) |
| Cáusticas, luz a través de líquido | [31](#31-cáusticas) |
| Oscilloscope, Lissajous, armonógrafo | [32](#32-osciloscopio-xy--lissajous) |
| Voronoi / celdas que se dividen | [33](#33-voronoi--celdas) |
| Moiré e interferencia de líneas finas | [34](#34-moiré--interferencia) |
| **Síntesis de video / LZX** | |
| Un sintetizador LZX dentro de TD, por módulos | [35](#35-módulos-lzx-como-componentes-reutilizables-de-td) |
| Barras, rampas y osciladores de video (patrón analógico) | [36](#36-rampas-y-osciladores-de-video) |
| Wavefolder, escalera, bandas que se doblan | [37](#37-waveshapers-stairs--staircase--arch) |
| Keyers y colorizers (Jones, Paik/Abe, Topogram) | [38](#38-keyers-y-colorizers) |
| Rutt/Etra, líneas de barrido desplazadas por la luz | [39](#39-scan-processor-ruttetra) |
| Feedback analógico de cámara a monitor (Memory Palace, Hypno, Video Waaaves) | [40](#40-feedback-de-video-analógico--frame-buffer) |
| Multiplicador, matriz, lógica de bits (XOR, Castle) | [41](#41-multiplicadores-matriz-y-lógica-de-bits) |
| Formas a partir de rampas, rotación y polar (DSG3, Navigator, Shapechanger) | [42](#42-formas-y-coordenadas-desde-rampas) |
| CRT, scanlines, ancho de banda analógico (Basement Vibes) | [43](#43-crt-scanlines-y-ancho-de-banda-analógico) |
| Reaction-diffusion de scanlines en un solo loop | [44](#44-scanline-reaction-diffusion) |

---

## Atlas de perfiles

Una línea por perfil: la **técnica que define el look** (no biografía) y la receta de este archivo que la aproxima.
Los enlaces marcados con † son el sitio oficial de memoria, sin abrirlo en esta sesión.

### Artistas y estudios de new media

| Perfil | Técnica de fondo | Recetas |
|---|---|---|
| Ryoji Ikeda | dato → barcode/binario sincronizado al cuadro, blanco y negro ([FACT](https://factmag.com/2021/05/04/ryoji-ikeda-presents-test-pattern)) | 1-3 |
| Alva Noto / raster-noton | test patterns alterados en tiempo real; *unitxt/univrs* hecho en TD con Markus Heckmann ([CDM](https://cdm.link/raster-noton-founders-found-visual-inspiration/)) | 3, 34 |
| Refik Anadol Studio | fluidos en GPU + partículas a escala arquitectónica, "data pigments" ([verse](https://verse.works/artworks/f7ce9123-e5c7-4c69-bce0-4c511879fad5/56793674)) | 10, 11, 13 |
| Ouchhh | datos científicos → reducción de dimensión (autoencoder, t-SNE) → esculturas de puntos ([designboom](https://www.designboom.com/art/ouchhh-ai-monolith-sculpture-datamonolith-12-04-2019/)) | 29 |
| Robert Henke | láser blanco vectorial; los datos del dibujo se vuelven sonido ([Gray Area](https://grayarea.org/press/photos-robert-henkes-lumiere-ii/)) | 25, 32 |
| NONOTAK | líneas monocromas proyectadas en capas translúcidas ([My Modern Met](https://mymodernmet.com/nonotak-studio-daydream-audiovisual-installation)) | 26 |
| Joanie Lemercier | líneas y bordes mapeados a mano, paisajes de luz ([Edges](https://joanielemercier.com/edges)) | 6, 27 |
| Max Cooper | sistemas naturales y matemáticas visibles con colaboradores científicos ([Resolume](https://www.resolume.com/blog/16844)) | 30 |
| Andy Lomas | simulaciones de crecimiento celular ([andylomas.com](https://andylomas.com/collaborations.html)) | 17, 33 |
| Kevin y Páraic McGloughlin | repetición, fractal de fotografía y corte rápido ("strata cut" digital) ([Make](https://makezine.com/article/craft/photography-video/trippy-fractal-homage-video-for-father/)) | 19 |
| Weirdcore | deformación 3D y time glitch con presets en vivo; Max/Jitter, QC, VDMX ([Synthtopia](https://www.synthtopia.com/content/2021/02/12/secrets-of-weirdcore-the-visuals-of-aphex-twin/)) | 19, 20 |
| Rhizomatiks / Daito Manabe | data-driven: captura → reducción → imagen en vivo ([research](https://research.rhizomatiks.com/en/works/chains.html)) | 16, 29 |
| Tundra | video como mapa de parámetros de luz, previs en TD ([highlike](https://highlike.org/text/tundra-2/)) | 28 |
| Ryoichi Kurokawa | paisajes y datos fracturados, glitch sobre naturaleza ([ryoichikurokawa.com](https://www.ryoichikurokawa.com/)†) | 19, 12 |
| Quayola | análisis algorítmico de pinturas y paisajes, point clouds ([quayola.com](https://quayola.com/)†) | 29 |
| Memo Akten | redes neuronales y sistemas de partículas como "ver a través de la máquina" ([memo.tv](https://www.memo.tv/)) | 13 |
| Zach Lieberman | línea y forma dibujadas en código, bocetos diarios ([zach.li](https://zach.li/)†) | 17, 22 |
| Kyle McDonald | visión por computadora y datos del cuerpo ([kylemcdonald.net](https://kylemcdonald.net/)) | 20 |
| Universal Everything | personajes y multitudes de partículas en movimiento ([universaleverything.com](https://www.universaleverything.com/)†) | 13, 15 |
| Rafael Lozano-Hemmer | instalaciones de datos biométricos (pulso, voz) ([lozano-hemmer.com](https://www.lozano-hemmer.com/)†) | 1 |
| Christopher Bauder / WHITEvoid | luz cinética y láser espacial; *Deep Web* con Henke ([whitevoid.com](https://www.whitevoid.com/)†) | 25, 26 |
| Maotik (Mathieu Le Sourd) | inmersivo generativo en TD, partículas y domos ([maotik.com](https://www.maotik.com/)†) | 13, 23 |
| MORAKANA | datos atmosféricos (nubes vía NOAA) como obra; Oro Lumen 2025 ([Right Click Save](https://www.rightclicksave.com/article/the-lumen-prize-digital-art-kunstsilo)) | 1, 10 |

### Síntesis de video: historia y escena actual

| Perfil / equipo | Técnica de fondo | Recetas |
|---|---|---|
| Nam June Paik + Shuya Abe | sintetizador Paik/Abe: colorizer + deformación magnética del raster (1969-72) ([Wikipedia: video synthesizer](https://en.wikipedia.org/wiki/Video_synthesizer)†) | 38, 39 |
| Dan Sandin | Sandin Image Processor (1971-74): módulos con rangos estándar, "Moog del video", se copiaba libre ([Wikipedia](https://en.wikipedia.org/wiki/Sandin_Image_Processor)) | 35 |
| Steve Rutt + Bill Etra | Rutt/Etra Scan Processor: la luz desplaza el barrido; posición, brillo y color intercambiables | 39 |
| Steina y Woody Vasulka | feedback + keyer + scan processor; fundaron The Kitchen (1971) ([Furlong / vasulka.org](https://vasulka.org/Kitchen/essays_furlong/K_Furlong_13.html), [Scan Processor Studies](https://visualmusicarchive.org/works/w/scan-processor-studies.html)) | 39, 40 |
| Dave Jones (Experimental Television Center) | Jones Colorizer (1974-75): keyers de niveles de gris → color por canal; frame buffer 64×64 (1977) ([Video History Project](https://videohistoryproject.org/node/6893)) | 38 |
| Eric Siegel | colorizer y EVS, usado por los Vasulka en *Telc* | 38 |
| LZX Industries (Lars Larsen, Ed Leckie) | modular de video Eurorack: rampas, osciladores, keyers, colorizers, frame stores ([módulos](https://lzxindustries.net/modules), [Vice](https://www.vice.com/en/article/modular-synths-lzx-interview)) | 35-42 |
| Sleepy Circuits (Hypno) | dos osciladores de forma + feedback con ganancia positiva/negativa en Raspberry Pi ([Gearnews](https://www.gearnews.com/hypno-trippy-voltage-controlled-visual-oscillator-for-eurorack-or-desktop)) | 40 |
| Critter & Guitari (EYESY) | modos en Python que reaccionan a audio y MIDI ([critterandguitari.com](https://www.critterandguitari.com/eyesy); ver `eyesy-conventions.md`) | 1, 32 |
| Erogenous Tones (Structure) | plataforma GLSL por nodos dentro de un módulo Eurorack, entradas compuesto y LZX 1 V RGB ([Analogue Haven](https://analoguehaven.com/erogenous-tones/structure)) | 35 |
| Andrei Jay (casi seguro el "Andrew Jay" buscado) | feedback de framebuffer con delay: *VIDEO_WAAAVES* y *WAAAVE_POOL* en Raspberry Pi; no usa TD ([guía](https://github.com/rootnotez/WAAAVE_GUIDE), [VIDEO_WAAAVES 2.5](https://github.com/ex-zee-ex/VIDEO_WAAAVES_2.5_suite)) | 40 |
| Jonas Bers | sintetizadores "banana" hechos a mano para scan-processing en vivo con tecnología de los 90 ([hackaday](https://hackaday.io/JonasBers), [Whitehot](https://whitehotmagazine.com/articles/companion-interview-with-jonas-bers/3483)) | 39 |
| wednesdayayay | patches de TD que emulan LZX: FKG3, Topogram, colorizer RGBbander, Memory Palace (VVeb), oscilador cuádruple → rampas ([GitHub](https://github.com/wednesdayayay/Touch-designer/blob/main/README.md)) | 35, 38, 40 |
| Alex Pelly | artista de video synth modular ([Perfect Circuit](https://www.perfectcircuit.com/signal/video-synthesis-alex-pelly)) | 36-40 |
| Noisedeck | video synth de shaders en el navegador ([noisedeck.app](https://noisedeck.app/about/)) | 36 |
| Comunidad | foro y documentación de LZX ([lzxindustries.net](https://lzxindustries.net/docs)); r/videosynthesis (no verificado); lista de links [VJ-RYO/VideoSynth](https://relatedrepos.com/gh/VJ-RYO/VideoSynth) | — |

### Exponentes de TouchDesigner

| Perfil | Lo que enseña / su firma | Recetas |
|---|---|---|
| Bileam Tschepe (elekktronaut) | feedback en todas sus variantes, pixel sort, RD, POPs ([Derivative](https://derivative.ca/community-post/bileam-tschepe-teaching-and-learning-touchdesigner/65419)) | 4, 5, 8, 21 |
| Matthew Ragan | instancing, GLSL, lecciones oficiales de POPs; Rutt/Etra en TD ([instancing](https://mir-lab.github.io/touchdesigner-instancing-examples), [learningGLSL](https://gh.hhj520.top/raganmd/learningGLSL)) | 13, 28, 39 |
| Simon Alexander-Adams (Polyhop) | sistemas complejos: CA, RD, instancing ([tutoriales](https://simon-alexander-adams.squarespace.com/tutorials-articles)) | 2, 8, 28 |
| Torin Blankensmith | Shader Park (SDF), MediaPipe y Depth Anything en TD ([alltd](https://alltd.org/uploader/torinblankensmith)) | 22, 23 |
| Paketa12 | TOPs, texto animado, "RGB math" ([YouTube](https://www.youtube.com/@paketa12)) | 4, 28 |
| Interactive & Immersive HQ (Elburz Sorkhabi, Jack DiLaura) | feedback, datamosh, fluidos desde Shadertoy, estilo Ikeda ([blog](https://interactiveimmersive.io/blog/touchdesigner-lessons/understanding-feedback-loops-in-touchdesigner/)) | 1, 4, 10, 20 |
| Darien Brito | *Mastering GLSL in TouchDesigner*, simulaciones en GLSL ([alltd](https://alltd.org/uploader/darienbrito)) | 8, 10 |
| Noah Norman | fluidos Navier-Stokes en TOPs ([charla](https://alltd.org/?p=2284)) | 10 |
| Dean Cheesman | flocking 3D en POPs ([Derivative](https://derivative.ca/community-post/tutorial/3d-flocking-pops/73049)) | 15 |
| Lake Heckaman | Gaussian splats nativos (GSOPs, TDGS) ([radiancefields](https://radiancefields.com/gsops-brings-native-gaussian-splatting-to-touchdesigner)) | 29 |
| t3kt (RayTK) | raymarching sin escribir GLSL ([RayTK](https://github.com/t3kt/raytk/releases)) | 23 |
| Worldwide Basement Vibes / Basement Vibes | tox de look analógico: *Scanline Reaction Diffusion* (un solo loop de feedback), *ANALOG_TV* (CRT con scanlines por instancing 3D), loops VHS de electrónica real, StreamDiffusion con sensor de profundidad ([Gumroad](https://basementvibes.gumroad.com), [alltd](https://alltd.org/uploader/worldwidebasementvibes)) | 43, 44 |
| Supermarket Sallad | no encontré material verificable más allá de una mención en alltd | — |
| VJ Fader | VJ de Berlín (Resolume + TD + shaders) según [vjstv](https://vjstv.com/artists/vj-fader); sin tutorial propio encontrado | — |
| Derivative (Markus Heckmann, Learn, showcase) | POPs, Time Machine, slit scan ([learn.derivative.ca](https://learn.derivative.ca/courses/200-intermediate/lessons/202-tops-intermediate/topic/slit-scan-using-the-time-machine-top/)) | 13, 18 |

### Museos, festivales e instituciones de new media

| Institución | Qué programa | A quién mirar ahí |
|---|---|---|
| [ZKM Karlsruhe](https://zkm.de/)† | museo de arte y medios; exposiciones de largo aliento sobre arte computacional y sonido | archivo de pioneros del video y el arte por computadora |
| [Ars Electronica](https://ars.electronica.art/)† (Center, Festival, Prix) | arte, tecnología y sociedad en Linz; el Prix premia arte computacional, IA, interactivo | ganadores del Prix (p. ej. Rhizomatiks × ELEVENPLAY *Multiplex*, [calls.ars.electronica.art](https://calls.ars.electronica.art/2023/prix/winners/6445/)) |
| [transmediale](https://transmediale.de/)† | festival de Berlín: cultura digital crítica, más teoría que espectáculo | artistas de medios con discurso |
| [MUTEK](https://mutek.org/)† (Montreal, México, Barcelona, Japón…) | AV en vivo, el referente principal para este rig | Henke, Kurokawa, Maotik, NONOTAK, Tundra |
| [Sónar+D](https://sonar.es/)† | creatividad y tecnología dentro de Sónar Barcelona | estudios de visuales, IA y música |
| [CTM Festival](https://ctm-festival.de/)† | música aventurera y AV en Berlín | Alva Noto ([archivo CTM](https://archive.ctm-festival.de/index.php?id=5787)) |
| [Berlin Atonal](https://berlin-atonal.com/)† / [Unsound](https://unsound.pl/)† | AV oscuro y monumental en Kraftwerk; Cracovia experimental | escenografías de luz y láser |
| [Barbican](https://www.barbican.org.uk/)† | exposiciones grandes de arte y tecnología en Londres | muestras temáticas de IA y juego |
| [Artechouse](https://www.artechouse.com/)† | salas inmersivas de proyección (DC, NY, Houston) | comisiones de artistas generativos |
| [teamLab](https://www.teamlab.art/)† / [Superblue](https://www.superblue.com/)† | mundos inmersivos interactivos; Superblue representa a artistas experienciales | ojo: el look "flores y arcoíris" no va con este cliente |
| [Atelier des Lumières](https://www.atelier-lumieres.com/)† | pintura clásica animada en salas inmersivas (Culturespaces) | sirve para medir escala, no como estética |
| [Rhizome](https://rhizome.org/)† / [Eyebeam](https://www.eyebeam.org/)† | net art, preservación digital (ArtBase); residencias de arte y tecnología | artistas emergentes de medios |
| [LAS Art Foundation](https://las-art.foundation/about) | comisiones grandes en Berlín (Kraftwerk, Halle am Berghain): IA, ciencia, inmersivo | Pierre Huyghe, Laure Prouvost, Jakob Kudsk Steensen, Ian Cheng ([visitberlin](https://www.visitberlin.de/en/las-art-foundation)) |
| [Fondation Cartier](https://www.fondationcartier.com/)† | arte contemporáneo con cruces de ciencia y matemática | no verificado qué artistas de medios tiene hoy |
| [Museum of the Moving Image](https://movingimage.org/)† | imagen en movimiento, videojuego y video arte en Nueva York | historia del video y el sintetizador |
| [Lumen Prize](https://lumenprize.com/categories) | premio de arte y tecnología; 2025 en Kunstsilo (Noruega) | Oro 2025: MORAKANA *Cumulus* ([Creative Boom](https://www.creativeboom.com/inspiration/lumen-awards-2025-this-is-what-computational-art-looks-like-when-its-done-right/)) |
| [Bright Festival](https://brightfestival.com/) | arte digital, diseño de luz y música electrónica (Florencia, Leipzig, Bruselas) | proyecciones 360° y obras de mapping ([Kunstkraftwerk](https://www.kunstkraftwerk-leipzig.com/en/exhibitions/bright-festival-connect)) |
| [Gray Area](https://grayarea.org/)† | arte y tecnología en San Francisco | Henke *Lumière II* |
| [KIKK](https://www.kikk.be/)†, [Scopitone](https://www.stereolux.org/)†, [MIRA](https://mirafestival.com/)†, [Decibel](https://decibelfestival.com/)† | festivales de AV y creatividad digital | el circuito que nombra `referentes_contemporaneos.md` |
| [Laboratorio Arte Alameda](https://artealameda.inba.gob.mx/)† (CDMX) | arte y tecnología en México | escena local de medios |

---

## A. Datos, rigor y ritmo

### 1. Data-viz tipo Ikeda (barcode / test pattern)
**Qué es.** El audio (o cualquier dato) reducido a barras, bits y números, en blanco y negro, sincronizado al cuadro.
El ritmo es la estética: cortes duros, pantalla casi binaria, textos tipográficos diminutos.
**Quién.** Ryoji Ikeda, *test pattern* (convierte señales de audio en barcodes sincronizados en tiempo real)
y *datamatics* — [FACT](https://factmag.com/2021/05/04/ryoji-ikeda-presents-test-pattern), [Film Comment](https://www.filmcomment.com/article/come-together-ryoji-ikeda-traverses-the-transfinite).
Tutorial TD estilo Ikeda con instancing + texturas (Jack DiLaura / Interactive & Immersive HQ):
[derivative.ca](https://derivative.ca/community-post/tutorial/ryoji-ikeda-style-minimalist-digital-art-touchdesigner/66777).
**Cómo en TD.** Pixel shader: dividir la pantalla en `N` filas; cada fila lee una banda o un bloque de la historia del audio
(Audio Spectrum CHOP → CHOP to TOP 1×512 → `texelFetch`). Barras = `step(umbral, valor)` por columna con ancho que cuantiza
`floor(uv.x*cols)`. Una fila de "bits" = `hash(floor(uv.x*cols) + u_step)`. Texto mono: Text TOP con números del Info CHOP
compuesto encima (pocos, chicos).
**Rig.** S1 densidad de barras · S2 velocidad de scroll · S3 jitter horizontal / desfase por fila · S4 mezcla
color1↔color2 (casi todo una tinta, color2 solo en filas marcadas) · S5 **cuantización** (de 8 a 512 columnas).
`u_low` = alto de las barras gruesas, `u_high` = densidad del ruido de bits, `u_kick` = invierte una franja
(un solo cuadro, no strobe de pantalla completa), `u_step` cambia la disposición de filas.
**Rendimiento.** Barato. Evita `texture()` con filtrado: usa `texelFetch` para que las barras sean nítidas.
**Evitar.** Pantalla completa parpadeando a 60 Hz (strobe agresivo); usar el inverso total solo cada 8-16 kicks.
**Estado.** ya en library: `data_barcode.glsl`, `datamatics.glsl`, `dot_matrix.glsl`, `matrix_pulse.glsl`.

### 2. Autómata celular 1D/2D
**Qué es.** Regla local aplicada a cada celda a partir de sus vecinas. En 1D (regla 30, 90, 110) cada cuadro es una fila
nueva y la historia baja por la pantalla: un tejido binario muy Ikeda. En 2D: Life y sus variantes "generations"
con celdas que decaen.
**Quién.** Simon Alexander-Adams (Polyhop), workshop de sistemas complejos con CA en GLSL desde cero:
[workshop](https://simon-alexander-adams.squarespace.com/tutorials/complex-systems-workshop),
[daily practice](https://simon-alexander-adams.squarespace.com/tutorials/daily-practice).
**Cómo en TD.** Red propia en COMP `red`: GLSL TOP (input 0 = Feedback TOP) a resolución de celda (p. ej. 256×144,
filtro nearest). 1D: la fila 0 se calcula con la regla sobre la fila 1 del cuadro anterior; el resto se desplaza una fila
(`texelFetch(prev, ivec2(x, y-1))`). Regla = bits de un entero `u_rule` (0-255). Salida escalada con Fit TOP nearest
+ un GLSL de presentación que dibuja celdas con margen fino.
**Rig.** S1 brillo de celdas vivas · S2 pasos por segundo (dividir con `absTime.frame % k`) · S3 ruido de mutación ·
S4 color por edad (`mix(color1,color2,edad)`) · S5 **regla** (menú de reglas buenas: 30, 45, 73, 90, 110, 150).
`u_kick` siembra una fila aleatoria `hash(u_step)`; `u_high` sube la tasa de mutación; `u_low` ensancha la celda.
**Rendimiento.** Barato; lo caro es upscale con filtrado: usa nearest.
**Evitar.** Life 2D genérico a pantalla completa (se ve a demo de 1990). Mejor 1D como cascada o 2D en una franja.
**Estado.** nueva.

### 3. Grid de test pattern (raster-noton)
**Qué es.** Retículas, test patterns y tipografía de sistema alterados en tiempo real; la pieza muestra su propio mecanismo.
**Quién.** Alva Noto, *unitxt / univrs* — visuales en TouchDesigner con Markus Heckmann según
[CDM](https://cdm.link/raster-noton-founders-found-visual-inspiration/); [Berliner Festspiele](https://www.berlinerfestspiele.de/en/maerzmusik/programm/2011/kalender/unitxt-univrs-alva-noto).
**Cómo en TD.** Shader de retícula con `fract(uv*N)` + `fwidth` para líneas de 1 px; celdas que se encienden por
`hash(celda + u_step)`; marcas de registro, cruces, escalas numéricas. Una sola tinta + un acento.
**Rig.** S1 opacidad de retícula · S2 velocidad de barrido · S3 desplazamiento de filas (shear digital) · S4 acento color2 ·
S5 **subdivisión** (2→64). `u_mid` = cuántas celdas encendidas, `u_kick` = cambia la subdivisión o el patrón.
**Rendimiento.** Trivial.
**Evitar.** Líneas gruesas o con blur; el look depende de 1 px limpio.
**Estado.** ya en library: `industrial_grid.glsl`, `module_grid.glsl`, `scanner.glsl`, `radar_sweep.glsl`.

---

## B. Feedback (la familia que más le gusta al cliente)

### 4. Feedback básico (transform + level)
**Qué es.** El cuadro anterior se reinyecta con una transformación pequeña (escala >1, rotación leve) y se atenúa;
la imagen nueva se compone encima. Da estela, eco y profundidad sin túnel si la escala es mínima.
**Quién.** Base de todo TD. Interactive & Immersive HQ, [Understanding feedback loops](https://interactiveimmersive.io/blog/touchdesigner-lessons/understanding-feedback-loops-in-touchdesigner/)
y [tutorial 085](https://derivative.ca/community-post/tutorial/secret-feedback-loops-touchdesigner-tutorial/66168);
Derivative Learn, [Creating a Feedback](https://learn.derivative.ca/courses/100-fundamentals/lessons/102-tops-working-with-images/topic/creating-a-feedback/);
curso de Bileam Tschepe [Generative Art with Feedback Systems](https://musichackspace.org/courses/generative-art-with-feedback-systems-in-touchdesigner).
**Cómo en TD.** `fuente → Composite (Over/Add) ← Transform ← Level ← Feedback TOP (target = composite)`.
En un solo GLSL TOP: input 1 = feedback, `prev = texture(fb, (uv-0.5)/zoom + 0.5) * decay`.
**Rig.** S1 mezcla de la fuente nueva · S2 rotación por cuadro · S3 zoom del loop · S4 deriva de color hacia color2
según la edad (multiplicar por `mix(1, color2/color1, k)` en cada pasada) · S5 **decay** (0.80-0.995).
`u_low` = zoom, `u_kick` = un golpe de escala 1 cuadro, `u_high` = ruido fino en la fuente.
**Rendimiento.** 16-bit float; en 8-bit el decay deja bandas y residuos que no se borran.
**Evitar.** Zoom constante >1.02 (túnel); decay ≥1 (satura: es lo que le pasó a Cinta Feedback). Botón RESET FEEDBACK existe.
**Estado.** ya en library: `estela.glsl`, `effects/rgb_trail_decay.frag`, `effects/liquid_memory.frag`, `effects/eco_lento.frag`.

### 5. Feedback con displacement (feedback líquido)
**Qué es.** El loop se desplaza con un campo (ruido, gradiente de la propia imagen o curl): la imagen se pinta, se
derrite y genera "falsas partículas" sin partículas.
**Quién.** Derivative, [Feedback flowfield, fake particle look](https://derivative.ca/community-post/tutorial/touchdesigner-beginner-tutorial-feedback-flowfield-fake-particle-look/71665);
[Displaced noise (tutorial 15)](https://derivative.ca/community-post/tutorial/displaced-noise-touchdesigner-tutorial-15/71162).
**Cómo en TD.** `Noise TOP (o GLSL de curl) → Displace TOP (input 2) ← Feedback`. En shader:
`vec2 v = curl(uv*f, t); prev = texture(fb, uv - v*amt)`. Agregar fuente fina (líneas, puntos) que el campo arrastra.
**Rig.** S1 brillo de emisores · S2 velocidad de evolución del campo · S3 **fuerza del desplazamiento** · S4 color por velocidad local
· S5 escala del campo (detalle). `u_mid` = fuerza, `u_kick` = re-siembra emisores en `hash(u_step)`.
**Rendimiento.** Un Noise TOP a media resolución basta; el campo puede ser 1/4 de la salida.
**Evitar.** Fuerza alta + decay alto = pantalla gris uniforme. Mantener 60-70 % de negro.
**Estado.** ya en library: `seda.glsl`, `flow_field.glsl`, `humo_tinta.glsl`, `effects/memory_marbling.frag`.

### 6. Edge feedback
**Qué es.** Se detecta el borde de la imagen dentro del loop: cada pasada genera contornos de contornos, como ondas
de nivel que se alejan de la forma.
**Quién.** Derivative, [Create edge feedback concert visuals](https://derivative.ca/community-post/tutorial/create-edge-feedback-concert-visuals/75058).
**Cómo en TD.** `forma (logo, SDF) → Composite ← Edge TOP ← Transform ← Level ← Feedback`. En shader: magnitud del
gradiente con 4 muestras de `prev`.
**Rig.** S1 grosor del borde · S2 expansión por cuadro · S3 ruido en el borde · S4 color alterno por generación (anillos
color1/color2 alternados: muy de sello) · S5 **número de generaciones visibles** (decay). `u_kick` = re-dibuja la forma
semilla; `u_low` = escala de la forma.
**Rendimiento.** Edge TOP es barato; cuidado con encadenar varios blur.
**Evitar.** Formas complejas como semilla (se vuelve ruido). Círculo o logo simple.
**Estado.** nueva (encaja con el sello circular: anillos concéntricos que nacen del logo).

### 7. Bloom feedback
**Qué es.** Bloom dentro del loop: los núcleos brillantes se esparcen y se acumulan, se ve "lumínico" y premium.
**Quién.** Derivative, [Feedback effects with the Bloom TOP](https://derivative.ca/community-post/tutorial/feedback-effects-bloom-top-touchdesigner/69971).
**Cómo en TD.** Bloom TOP entre Level y Composite del loop; umbral alto para que solo crezcan los núcleos.
**Rig.** S1 intensidad de bloom · S2 velocidad · S3 desplazamiento leve · S4 color del halo (color2) vs núcleo (color1→blanco) ·
S5 **umbral de bloom**. `u_kick` = pico de intensidad 150 ms.
**Rendimiento.** Bloom es multipasada: a media resolución.
**Evitar.** Todo brilla = nada brilla. Umbral alto.
**Estado.** nueva como receta; se puede sumar a cualquier visual con feedback existente.

---

## C. Simulaciones (sistemas, no plantillas)

### 8. Reaction-diffusion (Gray-Scott)
**Qué es.** Dos químicos A/B que se difunden y reaccionan; según `feed` y `kill` aparecen manchas, laberintos, corales, mitosis.
**Quién.** Derivative, [Reaction Diffusion, tutorial 19](https://derivative.ca/community-post/tutorial/reaction-diffusion-touchdesigner-tutorial-19/71701)
y [Reaction-Diffusion feedback effects](https://derivative.ca/community-post/tutorial/reaction-diffusion-feedback-effects-touchdesigner-tutorial/66191);
Simon Alexander-Adams ([workshop](https://simon-alexander-adams.squarespace.com/tutorials/complex-systems-workshop)).
**Cómo en TD.** GLSL TOP 32-bit float RG, input = Feedback, varios pasos por cuadro (encadenar GLSL o loop interno).
Input Extend Mode en Repeat para evitar bordes ([foro](https://forum.derivative.ca/t/convertion-of-shaders-based-on-reaction-diffusion/129347)).
Presentación aparte: `B` → mapa de luz, gradiente de `B` → sombreado de relieve.
**Rig.** S1 contraste de presentación · S2 pasos por cuadro · S3 anisotropía / advección por curl · S4 color por concentración ·
S5 **feed/kill** (un slider que recorre una curva de pares buenos). `u_kick` siembra B en un anillo; `u_low` = feed.
**Rendimiento.** 960×540, 6 pasos por cuadro ya probado; float32 obligatorio.
**Evitar.** Arrancar sin semilla (pantalla vacía); dejar que llene toda la pantalla: máscara circular o decay de B.
**Estado.** ya en library: `reaccion.glsl` + `reaccion_sim.glsl` (builder `setup_base46_reaccion.py`).

### 9. Physarum (slime mold)
**Qué es.** Agentes que sienten un rastro con tres sensores (izq., frente, der.), giran hacia el más fuerte, avanzan
y depositan; el rastro se difunde (3×3) y decae. Salen redes de transporte filamentosas, vivas, muy "red de nodos orgánica".
**Quién.** Sage Jenson, [Physarum](https://cargocollective.com/sagejenson/physarum) (parámetros: distancia/ángulo de sensor,
paso, giro, depósito, decay); implementación GLSL en TD en el [foro de Derivative](https://forum.derivative.ca/t/physarum-transport-network-in-glsl/9962)
(TD viejo); demo GPU de [Amanda Ghassaei](https://apps.amandaghassaei.com/gpu-io/examples/physarum/).
**Cómo en TD.** Dos estados: agentes en una textura (cada píxel = un agente: xy + ángulo, 32-bit float, p. ej. 512×512 = 262k)
o en un GLSL POP / GLSL Advanced POP (ver skill `td-pops`); rastro en un TOP. Paso 1: GLSL de agentes lee rastro, actualiza.
Paso 2: depósito = render de puntos (Render TOP con los agentes como instancias de punto, blend Add) o GLSL POP → POP to TOP.
Paso 3: GLSL de difusión + decay sobre el rastro (Feedback).
**Rig.** S1 brillo del rastro · S2 tamaño de paso · S3 ángulo de giro · S4 color por densidad (filamentos color1, nudos → color2/blanco) ·
S5 **ángulo de sensor** (cambia de redes finas a vórtices). `u_low` = depósito, `u_high` = jitter angular, `u_kick` = empuja
todos los agentes hacia afuera desde el centro (respira el sello) o re-siembra en anillo.
**Rendimiento.** 250k-1M agentes es viable en GPU actual; el cuello es el depósito (usar POPs o atomics si hay compute).
**Evitar.** Dejar que llene la pantalla: decay alto + máscara del círculo del sello.
**Estado.** nueva. Candidata fuerte: cumple "red de nodos con feedback" y se ve a MUTEK.

### 10. Fluido Navier-Stokes (stable fluids)
**Qué es.** Advección semi-lagrangiana de velocidad y tinta + proyección de presión (Jacobi) + vorticidad. Humo y tinta
de verdad, no ruido que parece humo.
**Quién.** Refik Anadol: la dinámica de fluidos es su inspiración principal y sus "data pigments" se renderizan con
solvers en GPU ([verse.works](https://verse.works/artworks/f7ce9123-e5c7-4c69-bce0-4c511879fad5/56793674), [refikanadol.com](https://refikanadol.com/works/machine-hallucinations-sphere/)).
En TD: [touchFluid](https://github.com/kamindustries/touchFluid) (solver 2D con vorticidad, MIT), charla de Noah Norman
[GLSL Fluids](https://alltd.org/?p=2284), [Generative Liquid Paintings](https://derivative.ca/community-post/tutorial/generative-liquid-paintings-touchdesigner/68643),
y [Refik Anadol particles en TD](https://derivative.ca/community-post/tutorial/refik-anadol-particles-touchdesigner-part-one-tutorial/67084).
**Cómo en TD.** Partir de touchFluid (.tox) dentro de `red`. Pasos: advect(vel) → splat de fuerzas → divergencia →
20-40 iteraciones Jacobi de presión → restar gradiente → advect(tinta). Todo float16/32 a 1/2 o 1/4 de resolución.
Presentación: tinta → `mix(color1,color2, velocidad)` + un poco de bloom.
**Rig.** S1 cantidad de tinta · S2 dt · S3 vorticidad · S4 color por velocidad · S5 **disipación** (humo que dura vs. pinceladas).
`u_low` = fuerza de los emisores (en anillo alrededor del sello), `u_kick` = splat radial grande, `u_high` = turbulencia fina.
**Rendimiento.** Iteraciones de presión son el costo: 20 a 480×270 se ve bien escalado.
**Evitar.** Emisores en arcoíris, mouse-trails genéricos. Emisores con forma (contorno del logo) y una tinta.
**Estado.** nueva (`liquid_light.glsl` y `humo_tinta.glsl` son imitaciones con ruido, no simulación).

### 11. Campos de flujo / curl noise
**Qué es.** Un ruido cuyo rotacional da un campo sin divergencia: las cosas fluyen sin amontonarse ni cruzarse. Sirve
para mover partículas, advectar feedback u orientar trazos.
**Quién.** Derivative, [curl noise tag](https://derivative.ca/tags/curl-noise), [Particle paths](https://derivative.ca/community-post/tutorial/particle-paths/67892);
look de Anadol (partículas que siguen flujos).
**Cómo en TD.** GLSL que calcula `curl = vec2(dN/dy, -dN/dx)` por diferencias finitas sobre simplex/fbm; o Noise POP /
Force en POPs. Uso: (a) desplazar feedback (receta 5), (b) velocidad de partículas (13), (c) orientar trazos por celda.
**Rig.** S1 densidad · S2 velocidad de evolución · S3 fuerza · S4 color por ángulo del flujo (dos tintas, no hue) · S5 **escala del campo**.
`u_mid` = fuerza, `u_kick` = cambia la semilla del ruido con fundido.
**Rendimiento.** Un fbm de 3-4 octavas a 1/4 de resolución en un TOP aparte, leído por todos.
**Evitar.** Ángulo → hue (arcoíris).
**Estado.** ya en library: `campo.glsl`, `flow_field.glsl`, `seda.glsl`.

### 12. Domain warping (fbm)
**Qué es.** `fbm(p + fbm(p + fbm(p)))`: mármol, nebulosa, tejido orgánico; muy barato y muy fluido.
**Quién.** Inigo Quilez (artículos de warping y [distance functions](https://iquilezles.org/articles/distfunctions)).
**Cómo en TD.** Un solo pixel shader. Iluminar con el gradiente para relieve; umbral para dejar negro.
**Rig.** S1 umbral (cuánto negro) · S2 velocidad · S3 **profundidad del warp** (S5 si es el rasgo) · S4 mezcla de tintas por capa de warp ·
S5 número de capas de warp. `u_low` = amplitud del warp, `u_high` = octavas altas.
**Rendimiento.** 3×fbm de 5 octavas a 1080p está bien; no subir a 8 octavas.
**Evitar.** Llenar toda la pantalla de "plasma" (es el look VJ 2005). Umbral alto, líneas de nivel finas.
**Estado.** parcial: `mareas_color.glsl`, `niebla_capas.glsl`, `effects/plasma_currents.frag`.

---

## D. Partículas, puntos e instancing

### 13. Partículas GPU con POPs
**Qué es.** Desde TD 2025 los POPs procesan puntos en GPU (Particle POP, Math Mix, Noise, Force, GLSL POP) sin pasar por CHOPs:
millones de puntos con fuerzas y memoria.
**Quién.** Derivative: [serie de lecciones POPs](https://derivative.ca/community-post/new-pops-lessons-learnderivativeca/74561)
(Matthew Ragan + Sudo Magic), [Working with particles in POPs](https://learn.derivative.ca/courses/review/lessons/109-pops-working-with-points/topic/working-with-particles-in-pops/),
[Wavy particle systems](https://derivative.ca/community-post/tutorial/wavy-particle-systems-touchdesigner-using-pops/73315),
[Surface trails](https://derivative.ca/community-post/tutorial/surface-trails-any-geometry-using-touchdesigner-pops/73881),
[3D particles from 2D textures](https://derivative.ca/community-post/tutorial/touchdesigner-3d-particles-2d-textures/73861).
**Cómo en TD.** `Particle POP (emisor: puntos del logo con Ray/Sample) → Noise/Force POP (curl) → Render (Geo COMP + Point Sprite/Line MAT) →
Render TOP → Feedback ligero`. Skill `td-pops` para el GLSL POP.
**Rig.** S1 tasa de emisión · S2 velocidad/arrastre · S3 fuerza del campo · S4 color por edad (`mix(color1,color2,age)`) ·
S5 **vida de la partícula** (estela corta vs. nube). `u_low` = fuerza radial, `u_kick` = burst de emisión, `u_high` = jitter.
**Rendimiento.** Point sprites de 1-2 px con blend Add, sin sombreado; 1M puntos ok en una RTX. Render TOP a 1080p con antialias 4x.
**Evitar.** Puntos gordos y difusos (se ve barato); explosiones de confeti multicolor.
**Estado.** nueva (no hay visual POPs en library).

### 14. Atractores extraños
**Qué es.** Integrar una EDO caótica (Lorenz, Aizawa, Thomas, Halvorsen) para millones de puntos: una escultura de hilos
que nunca se repite.
**Quién.** Derivative, [Strange attractors (POPs), tutorial 06](https://derivative.ca/community-post/tutorial/touchdesigner-tutorial-06-strange-attractors-pops/72620).
Look cercano a Max Cooper (sistemas naturales) y a Anadol (nubes de puntos).
**Cómo en TD.** GLSL POP que en cada cuadro integra `p += f(p)*dt` para todos los puntos (estado persistente); render con
Line/Point MAT + Render TOP + feedback mínimo para el trazo. Cámara orbitando lento (Camera COMP con LFO).
**Rig.** S1 brillo · S2 dt · S3 parámetro de caos (σ/ρ/β o a/b) · S4 color por velocidad · S5 **tipo de atractor / parámetro principal**.
`u_low` = dt, `u_mid` = parámetro b, `u_kick` = re-siembra el 10 % de puntos en una esfera chica (destello que se dispersa).
**Rendimiento.** 500k-2M puntos con blend Add; sin profundidad.
**Evitar.** Cámara que gira rápido (mareo); dt alto (explota a NaN: clamp).
**Estado.** nueva (`referentes_contemporaneos.md` lo lista como "siguiente a explorar").

### 15. Boids / flocking
**Qué es.** Separación + alineación + cohesión: bandadas que se parten y se juntan, muy leíbles con audio.
**Quién.** Dean Cheesman, [3D flocking with POPs](https://derivative.ca/community-post/tutorial/3d-flocking-pops/73049); [tag boids](https://derivative.ca/tags/boids).
**Cómo en TD.** Neighbor POP para vecinos + GLSL POP con las tres reglas; instanciar un trazo corto orientado a la velocidad.
**Rig.** S1 número visible · S2 velocidad máxima · S3 separación · S4 color por densidad local · S5 **cohesión** (cardumen vs. dispersión).
`u_kick` = depredador puntual (repulsión radial), `u_low` = cohesión, `u_high` = ruido.
**Rendimiento.** Neighbor POP es lo caro: limitar vecinos (8-16) y puntos (20-100k).
**Evitar.** Pájaros/peces literales: trazos abstractos de 1 px.
**Estado.** nueva.

### 16. Red de nodos (plexus)
**Qué es.** Puntos que se unen con segmentos cuando están cerca; la opacidad de la línea cae con la distancia.
**Quién.** El estilo "Pal Norte" que pidió el cliente. En POPs: [Proximity POP](https://derivative.ca/UserGuide/Proximity_POP) emite líneas entre vecinos
y [Neighbor POP](https://derivative.ca/UserGuide/Neighbor_POP).
**Cómo en TD.** Variante 2D en shader: nodos en rejilla suelta, revisar 3×3 celdas vecinas, segmento con `sdSegment` y `fwidth`.
Variante 3D: `Point Generator POP → Noise POP → Proximity POP (lines) → Line MAT → Render TOP → feedback`.
**Rig.** S1 opacidad de líneas · S2 deriva de nodos · S3 ruido de posición · S4 color por longitud (corto = color1, largo = color2) ·
S5 **radio de conexión**. `u_kick` abre el radio, `u_high` = paquetes de luz que viajan por las aristas.
**Rendimiento.** Proximity POP con límite de líneas por punto; en shader no pasar de 3×3 vecinos.
**Evitar.** Malla densa uniforme (cliché de "tecnología"); dejar huecos negros.
**Estado.** ya en library: `red_nodos.glsl` (builder `setup_base18_red_nodos.py`), `envios_network.glsl`, `tile_constellation.glsl`.

### 17. Differential line growth
**Qué es.** Una curva cerrada de puntos que se repelen y se mantienen unidos a sus vecinos; al insertar puntos donde
se estira, se pliega como coral o cerebro. Empieza como un círculo: perfecto para el sello.
**Quién.** [Differential Line Growth in TouchDesigner](https://alltd.org/?p=63580); Brendan Dawes, [organic lines](https://brendandawes.com/blog/1264-organic-lines).
**Cómo en TD.** POPs: Line/Circle POP → GLSL POP (atracción a vecinos de índice, repulsión con Neighbor POP, suavizado) →
Resample/subdivide cuando un segmento supera largo máximo (cada N cuadros). Render con Line MAT de 1-2 px + feedback suave.
Reiniciar al círculo cuando hay demasiados puntos.
**Rig.** S1 grosor/brillo · S2 velocidad de crecimiento · S3 repulsión · S4 color por edad del punto · S5 **largo máximo de segmento**
(controla la escala del pliegue). `u_kick` = reinicio al círculo con fundido cada X kicks (`u_step % 32`), `u_low` = repulsión.
**Rendimiento.** Crece sin límite: tope de puntos (p. ej. 20k) y reinicio.
**Evitar.** Dejar que salga de la pantalla; máscara circular.
**Estado.** nueva.

Instancing de retícula y point clouds: recetas 28 y 29, en la sección F.

---

## E. Tiempo y distorsión digital

### 18. Slit scan / time displacement
**Qué es.** Cada píxel muestra un instante distinto del pasado según un mapa (gradiente, ruido, círculo). El tiempo se estira.
**Quién.** Derivative Learn, [Slit scan con Time Machine TOP](https://learn.derivative.ca/courses/200-intermediate/lessons/202-tops-intermediate/topic/slit-scan-using-the-time-machine-top/);
[Time Machine TOP](https://derivative.ca/UserGuide/Time_Machine_TOP), [Texture 3D TOP](https://derivative.ca/UserGuide/Texture_3D_TOP) (buffer circular);
Derivative, [Slitscan](https://derivative.ca/community-post/tutorial/slitscan).
**Cómo en TD.** `fuente generativa → Texture 3D TOP (cache 64-128) → Time Machine TOP (input 2 = mapa de tiempo)`. Mapa radial
(distancia al centro) = anillos de tiempo, ideal para el sello.
**Rig.** S1 mezcla con la fuente actual · S2 velocidad de la fuente · S3 forma del mapa (lineal → radial → ruido) · S4 color por retardo ·
S5 **profundidad de tiempo** (cuántos cuadros atrás). `u_kick` cambia el mapa; `u_low` = profundidad.
**Rendimiento.** La cache cuesta VRAM: 128 × 1080p × rgba8 ≈ 1 GB. Usar 960×540 o 64 cuadros.
**Evitar.** Mapa lineal fijo (look de tutorial). Cambiar el mapa con el kick.
**Estado.** ya en library: `slit_scan.glsl`, `slit_scan_mapa.glsl`, `slit_scan_src.glsl` (builder `setup_base47_slit_scan.py`).

### 19. Time glitch por bloques
**Qué es.** La imagen se divide en bloques (macroblocks) y cada bloque se toma de un instante distinto o se congela,
con desplazamientos cuantizados. Distorsión digital con intención.
**Quién.** Weirdcore (Aphex Twin): presets de distorsión controlados en vivo, mapeo de caras y deformación
([Synthtopia](https://www.synthtopia.com/content/2021/02/12/secrets-of-weirdcore-the-visuals-of-aphex-twin/),
[It's Nice That](https://www.itsnicethat.com/features/weirdcore-aphex-twin-field-day-050617-miscellaneous)). Sus herramientas
históricas son Max/Jitter, QC y VDMX, no TD.
**Cómo en TD.** Texture 3D de la fuente + GLSL que, por bloque `floor(uv*grid)`, elige capa `hash(bloque + u_step) * profundidad`
y suma un offset horizontal cuantizado. Opcional: separar canales con 1-2 px de offset (no RGB arcoíris: offset de la luminancia
y tintar con las dos tintas).
**Rig.** S1 porcentaje de bloques afectados · S2 frecuencia de re-sorteo · S3 desplazamiento · S4 tinta del bloque glitch (color2) ·
S5 **tamaño de bloque**. `u_kick` = re-sorteo, `u_high` = bloques pequeños extra.
**Rendimiento.** Igual que 18; el re-sorteo es gratis.
**Evitar.** Glitch permanente al 100 %: la base debe ser legible, el glitch es el golpe.
**Estado.** nueva como visual autónomo (Time Glitch del canal 11 existe en el show; no hay archivo en library).

### 20. Datamosh / optical flow warp
**Qué es.** Se mide el movimiento (optical flow) y se usa para desplazar el cuadro anterior en un loop: la imagen
"arrastra" su pasado, como un P-frame sin I-frame.
**Quién.** Derivative, [Optical flow warp con NVIDIA Optical Flow TOP](https://derivative.ca/community-post/asset/optical-flow-warp-setup-nvidia-optical-flow-top-and-blender-scenes/68940);
[Palette: opticalFlow](https://derivative.ca/UserGuide/Palette:opticalFlow) (x en rojo, y en verde);
Interactive & Immersive HQ, [Datamoshing in TouchDesigner part 2](https://interactiveimmersive.io/blog/touchdesigner-resources/datamoshing-in-touchdesigner-part-2/);
explicación paso a paso en [diffusionpilot](https://diffusionpilot.blogspot.com/2024/01/opticalflow-warp.html).
**Cómo en TD.** `fuente → opticalFlow (o Nvidia Flow TOP) → Displace TOP (input 2) ← Feedback ← (Composite con fuente cuando `u_kick`)`.
En generativo puro: el flujo sale de la propia fuente animada (logo girando, partículas) o de un curl noise.
El "I-frame" = cada kick refresca con la fuente limpia; entre kicks todo se arrastra.
**Rig.** S1 mezcla de refresco · S2 velocidad de la fuente · S3 **ganancia del flujo** · S4 tinta en zonas de mucho movimiento ·
S5 cada cuántos kicks entra el I-frame (1, 2, 4, 8). `u_low` = ganancia.
**Rendimiento.** El Optical Flow TOP de NVIDIA es solo para GPUs NVIDIA nuevas; el palette clásico es más barato pero más tosco.
**Evitar.** Fuente estática (no hay flujo, no pasa nada).
**Estado.** nueva.

### 21. Pixel sort
**Qué es.** Lo brillante "gotea" por columnas o filas; versión TD = pseudo-sort con feedback y umbral.
**Quién.** Bileam Tschepe (elekktronaut), [Pixel sorting](https://derivative.ca/community-post/tutorial/pixel-sorting/62656) — solo TOPs y feedback
(Difference, Displace, Level, Subtract).
**Cómo en TD.** Máscara de umbral → Displace vertical del feedback solo donde la máscara es 1 → composite con la fuente.
**Rig.** S1 umbral · S2 velocidad del goteo · S3 dirección/ángulo · S4 tinta del goteo · S5 **largo del goteo** (decay).
`u_kick` corta y reinicia el goteo; `u_high` = umbral.
**Rendimiento.** Barato.
**Evitar.** Goteo sobre toda la pantalla; restringir a la forma.
**Estado.** ya en library: `pixel_sort.glsl`.

---

## F. Formas, SDF, 3D

### 22. SDF 2D y morph de formas
**Qué es.** Formas descritas por su distancia con signo: se unen con `smin` (metaballs), se redondean, se hacen anillos
(`abs(d) - w`) y bandas concéntricas (`fract(d*k)`), todo con antialias perfecto vía `fwidth`.
**Quién.** Inigo Quilez, [distance functions](https://iquilezles.org/articles/distfunctions) (combinaciones, redondeo, anillos);
su página de primitivas 2D (`/articles/distfunctions2d`) no la pude abrir. Torin Blankensmith / Shader Park para SDF accesibles en TD
([workshop](https://derivative.ca/workshop/audio-reactive-shaders-shader-park-touchdesigner-live-session/64913)).
**Cómo en TD.** Logo → SDF: `logo_murcielago.png` → Threshold → GLSL de Jump Flooding (o Blur + Level como aproximación barata)
a un TOP de distancia; o reconstruir el sello con primitivas (círculos + anillos). Luego, en shader: bandas concéntricas desde
la distancia, `smin` con círculos que orbitan, ondas que viajan por `d`.
**Rig.** S1 grosor de línea · S2 velocidad de ondas · S3 ruido en la distancia · S4 tinta por banda (alternar) · S5 **suavidad del smin**
(formas separadas ↔ masa líquida). `u_kick` = onda que sale del sello (anillo que viaja por `d`), `u_low` = radio de las gotas.
**Rendimiento.** JFA del logo se calcula una vez (no cada cuadro).
**Evitar.** SDF geométrico genérico (el cliente ya rechazó "shaders geométricos genéricos"): siempre partir del sello.
**Estado.** parcial: `eclipse.glsl`, `ring_chase.glsl`, `ring_matrix.glsl`; nueva la versión "logo → SDF".

### 23. Raymarching 3D y volumétrico
**Qué es.** Escenas 3D descritas por SDF y dibujadas marchando rayos; o volumen (humo) acumulando densidad a lo largo del rayo.
**Quién.** [Raymarching in TouchDesigner, serie](https://derivative.ca/community-post/tutorial/raymarching-touchdesigner-tutorial-series/62745);
[RayTK](https://github.com/t3kt/raytk/releases) (raymarching sin escribir GLSL); [RayTK fractal column](https://derivative.ca/community-post/tutorial/raytk-fractal-column-tutorial/68316).
**Cómo en TD.** Pixel shader con `for 64 pasos`, normales por gradiente, luz rim con color1/color2. Volumen: 32-48 pasos acumulando
`densidad(fbm)` con absorción; luz desde atrás (contraluz) para que el negro mande.
**Rig.** S1 densidad/exposición · S2 velocidad de cámara · S3 deformación (twist, ruido) · S4 color de luz vs sombra · S5 **forma/umbral de densidad**.
`u_low` = densidad, `u_kick` = destello de luz interna.
**Rendimiento.** Caro: renderizar a 1/2 y escalar; limitar pasos; mantener <8 ms.
**Evitar.** Cámaras que avanzan por un túnel; fractales mandelbulb de screensaver.
**Estado.** nueva (solo `op_sphere.glsl`, `esferas.glsl` como SDF simples).

### 24. Cimática / Chladni
**Qué es.** Patrones nodales de una placa vibrando: `cos(nπx)cos(mπy) - cos(mπx)cos(nπy) = 0`; partículas o arena se acumulan en las líneas nodales.
En polar (placa circular) se usan Bessel × cos(mθ): anillos y radios, perfecto para el sello.
**Quién.** Derivative, [Audioreactive particles with Chladni cymatics](https://derivative.ca/community-post/tutorial/audioreactive-particles-chladni-cymatics/67877);
[Cymatics in TouchDesigner](https://alltd.org/?p=36183) (ecuaciones en GLSL + partículas).
**Cómo en TD.** Shader directo (`exp(-abs(f)*k)` para líneas) o partículas (POPs) cuya velocidad es `-grad(|f|)` + ruido: se juntan en los nodos.
**Rig.** S1 brillo · S2 velocidad de transición entre modos · S3 ruido/vibración · S4 tinta por amplitud · S5 **modo (n,m)**.
`u_kick` = salta al siguiente modo (`u_step`), `u_low` = vibración que dispersa la arena.
**Rendimiento.** Shader barato; partículas según receta 13.
**Evitar.** Cambiar de modo continuamente: el modo se queda y el kick lo cambia.
**Estado.** existe en el show Corona Capital (Cimática, base26); no hay archivo en library: copiarlo.

### 25. Láser / vector sobre negro
**Qué es.** Pocas líneas, precisas, muy brillantes en el centro y con halo, sobre negro total; fósforo que persiste.
**Quién.** Robert Henke, *Lumière*: tres láseres blancos que dibujan objetos efímeros; los datos de las formas se vuelven sonido
([Gray Area](https://grayarea.org/press/photos-robert-henkes-lumiere-ii/), [Exclaim](https://exclaim.ca/music/article/robert_henke-mutek_august_24_montreal_qc)).
**Cómo en TD.** Shader de haces analíticos (`exp(-d²/w²)` núcleo + `1/d` halo) o geometría real: SOP/POP de curva → Line MAT → Render TOP →
Bloom + feedback de fósforo.
**Rig.** S1 brillo · S2 velocidad de dibujo · S3 jitter de galvo · S4 núcleo blanco vs halo color · S5 **figura** (la cambia el kick).
**Rendimiento.** Barato.
**Evitar.** Muchos haces a la vez; humo que cubre todo.
**Estado.** ya en library: `laser.glsl` (builder `setup_base44_laser.py`).

### 26. Capas de líneas con paralaje (NONOTAK)
**Qué es.** Líneas proyectadas sobre capas translúcidas: una línea vertical se vuelve pared, un círculo se vuelve volumen; monocromo.
**Quién.** NONOTAK, *Daydream*: varias capas de tela y proyectores, proyecciones monocromas
([projection-mapping.org](https://projection-mapping.org/daydream-infinite-light-tunnels), [My Modern Met](https://mymodernmet.com/nonotak-studio-daydream-audiovisual-installation)).
**Cómo en TD.** Shader con N capas: cada capa dibuja líneas finas con escala `1/(1+z*k)` y desplazamiento por paralaje; suma aditiva.
**Rig.** S1 brillo · S2 velocidad · S3 separación entre capas · S4 tinta por profundidad · S5 **número de líneas por capa**. `u_kick` = cambia el patrón
(barras ↔ círculos concéntricos).
**Rendimiento.** Barato.
**Evitar.** Que las capas formen un túnel con zoom continuo.
**Estado.** ya en library: `cortinas.glsl` (builder `setup_base48_cortinas.py`), `shingle_wall.glsl`.

### 27. Ridgeline / paisaje de líneas
**Qué es.** Líneas horizontales desplazadas por altura con oclusión (estilo *Unknown Pleasures*) o paisajes de líneas proyectadas.
**Quién.** Joanie Lemercier: vocabulario de líneas y formas geométricas que juega con la percepción del espacio
([joanielemercier.com/edges](https://joanielemercier.com/edges), [Hackster sobre Paper and Light](https://www.hackster.io/news/projection-mapping-turns-folded-paper-into-an-ever-shifting-art-installation-81cb0e081cba)).
**Cómo en TD.** Historia del espectro en una textura 1×128 con feedback; shader dibuja N líneas con oclusión (máximo acumulado de abajo arriba).
**Rig.** S1 altura · S2 velocidad de scroll · S3 perspectiva · S4 tinta por antigüedad · S5 **número de líneas**.
**Estado.** ya en library: `cordillera.glsl` + `cordillera_hist.glsl`; versión polar en el show (Anillos de Tiempo, base40).

### 28. Instancing de retícula (kinetic tiles)
**Qué es.** Miles de copias de una forma mínima (barra, punto, cuadro) en una retícula, cuya escala/rotación/color vienen de una textura.
**Quién.** Matthew Ragan, [Instant instancing](https://derivative.ca/community-post/tutorial/instancing-geometry/62084) y
[40+ ejemplos de instancing](https://mir-lab.github.io/touchdesigner-instancing-examples); Simon Alexander-Adams, [instancing](https://simon-alexander-adams.squarespace.com/tutorials/instancing);
el tutorial Ikeda de DiLaura usa la misma idea.
**Cómo en TD.** `Grid POP/SOP → Geometry COMP (instancing desde un TOP: r=escala, g=rotación, b=t de color) → Render TOP ortográfico`.
El TOP de control es un shader barato (ondas desde el centro, historia del audio).
**Rig.** S1 escala máxima · S2 velocidad de la onda · S3 rotación · S4 t de color · S5 **resolución de la retícula**.
`u_kick` = onda radial; `u_low/mid/high` = anillos distintos (bajo al centro, agudos afuera: el audio se lee).
**Rendimiento.** 100k instancias de un quad es barato; evitar sombras.
**Evitar.** Cubos 3D girando con sombras (look de 2015).
**Estado.** parcial: `cuadritos.glsl`, `dot_wave.glsl`, `kick_blocks.glsl` (en shader); nueva la versión con instancing real.

### 29. Point cloud / Gaussian splats
**Qué es.** El logo o un objeto como nube de puntos (o splats gaussianos) que se disuelve, se reagrupa y responde a fuerzas.
**Quién.** Refik Anadol / Ouchhh (esculturas de datos, [designboom](https://www.designboom.com/art/ouchhh-ai-monolith-sculpture-datamonolith-12-04-2019/));
GSOPs, splats nativos en TD sobre POPs (requiere TD 2025.32820+) [radiancefields](https://radiancefields.com/gsops-brings-native-gaussian-splatting-to-touchdesigner);
[point cloud de modelo 3D con POPs](https://lab.arts.ac.uk/books/touchdesigner/page/pops-point-cloud-from-3d-model).
**Cómo en TD.** Logo PNG → TOP to POP (un punto por píxel con alfa) con z por luminancia/ruido → Noise POP + Force (receta 13) →
GLSL MAT de splat (sprite gaussiano, blend Add). "Disolver y reagrupar": mezclar posición original ↔ simulada con S5.
**Rig.** S1 brillo · S2 velocidad · S3 fuerza del ruido · S4 tinta por profundidad · S5 **disolución** (0 logo, 1 nube).
`u_kick` = explosión radial que vuelve con resorte; `u_low` = respiración en z.
**Rendimiento.** 200k-500k puntos con splats pequeños; cuidar overdraw.
**Evitar.** Rotación 3D del logo tipo "intro de canal".
**Estado.** nueva. Encaja en canal 11 (logos).

### 30. Estructuras matemáticas (espiral de primos, filotaxis)
**Qué es.** Mostrar una estructura matemática con precisión: la espiral de Sacks (primos sobre `r = √n, θ = 2π√n`), filotaxis
(ángulo áureo), cuadrículas de Ulam. Se ve "científico" y circular por naturaleza.
**Quién.** Max Cooper, *Emergence*: imágenes de la espiral de Sacks y simetrías, con matemáticos y animadores como Andy Lomas
([Resolume](https://www.resolume.com/blog/16844), [Ableton](https://www.ableton.com/en/blog/composing-infinity-max-cooper-his-new-album/),
[Andy Lomas](https://andylomas.com/collaborations.html)).
**Cómo en TD.** Shader: para cada píxel, convertir a (r,θ), estimar `n` cercano y probar si es primo (tabla de primos en un TOP 1D precalculado
con Script/Python una sola vez) o dibujar filotaxis con `n = r²`. O instancing de puntos (receta 28).
**Rig.** S1 tamaño de punto · S2 velocidad de rotación/crecimiento · S3 desviación del ángulo (de 137.5° a otros: aparecen brazos) · S4 primos color1, compuestos color2 tenue ·
S5 **ángulo de divergencia**. `u_kick` = ilumina un brazo/una congruencia distinta (`u_step % m`); `u_low` = radio.
**Rendimiento.** Instancing o shader con búsqueda local: barato.
**Evitar.** Girasol literal; mantener puntos finos y negro dominante.
**Estado.** nueva. Circular por diseño: respeta la forma del sello.

### 31. Cáusticas
**Qué es.** Patrón de luz concentrada por una superficie de agua; se simula con voronoi F2−F1 deformado o con refracción de una malla.
**Quién.** Look de "luz a través de líquido" (ron). Mismo principio que los shaders de agua de Shadertoy.
**Rig.** S1 brillo de nudos · S2 velocidad · S3 deformación · S4 tinta · S5 **escala de celda**. `u_kick` = ola que pasa.
**Estado.** ya en library: `ron_liquido_causticas.glsl`.

### 32. Osciloscopio XY / Lissajous
**Qué es.** Dibujar la señal estéreo o sumas de senos como curva XY con fósforo; armonógrafo = péndulos amortiguados.
**Quién.** Tradición oscilloscope music; Henke usa los datos de dibujo como sonido (receta 25).
**Cómo en TD.** Audio CHOP → (Shuffle) → CHOP to SOP/POP como curva → Line MAT → Render → feedback de fósforo. O shader con suma de péndulos.
**Rig.** S1 brillo · S2 velocidad · S3 desfase · S4 tinta del trazo vs fósforo · S5 **razón de frecuencias**. `u_kick` cambia la razón.
**Estado.** ya en library: `armonografo.glsl` (builder `setup_base24_armonografo.py`), `pulso_neon_v2.glsl`.

### 33. Voronoi / celdas
**Qué es.** Partición del plano en celdas por punto más cercano; bordes = F2−F1. Celdas que se dividen (mitosis) con el kick.
**Quién.** Inigo Quilez (artículos de voronoi y bordes); Andy Lomas (crecimiento celular, Max Cooper).
**Cómo en TD.** Shader 3×3 vecinos; semillas animadas por ruido; `u_step` agrega una semilla (división).
**Rig.** S1 grosor de borde · S2 velocidad · S3 jitter de semillas · S4 tinta por tamaño de celda · S5 **número de celdas**.
**Evitar.** Rellenar celdas con colores distintos (vitral). Solo bordes finos.
**Estado.** parcial: `effects/spectral_mitosis.frag`, `tile_constellation.glsl`.

### 34. Moiré / interferencia
**Qué es.** Dos o más familias de líneas finas superpuestas con pequeña diferencia de escala o ángulo: aparecen ondas gigantes.
Rigor óptico, muy raster-noton.
**Cómo en TD.** Shader: `sin(d1*k1) * sin(d2*k2)` con `d` = distancia a dos centros (anillos) o coordenada rotada; antialias con `fwidth` y supersampling 2×2.
**Rig.** S1 contraste · S2 velocidad de deriva de centros · S3 diferencia de ángulo · S4 tinta por familia (color1 una, color2 otra) · S5 **diferencia de frecuencia**.
`u_low` separa los centros, `u_kick` cambia la frecuencia base.
**Rendimiento.** Barato; el aliasing es el enemigo (en LED y proyección hay que probar en sitio).
**Evitar.** Moiré a pantalla completa con alto contraste a 60 Hz (puede ser molesto, cercano a strobe).
**Estado.** parcial: `cortinas.glsl`; nueva la versión de anillos concéntricos (sello).

---

## G. Síntesis de video y emulación LZX

La idea de fondo del sintetizador de video analógico (Sandin, Rutt/Etra, LZX): **todo es una señal de 0 a 1 V que
recorre la pantalla al ritmo del barrido**. Una rampa horizontal es "la coordenada x"; un oscilador es un seno de esa
coordenada; una forma es una combinación de rampas que pasa por un keyer; el color sale al final, de un colorizer.
Como todas las señales tienen el mismo rango, cualquier salida puede modular cualquier entrada.

En TD eso se traduce limpio: **una señal = un TOP monocromo 32-bit float (canal R) con valores 0-1**; un cable de
patch = un cable de TOP; una perilla = un uniform o un parámetro; el CV externo = CHOP (audio, LFO). Y el colorizer final
es justo donde entra la paleta de dos tintas del rig.

### 35. Módulos LZX como componentes reutilizables de TD
**Qué es.** Una librería de `.tox` (uno por tipo de módulo) con la misma interfaz: entradas TOP mono 0-1, salida TOP mono
0-1 (o RGB al final), parámetros con nombre de perilla. Con eso, un visual nuevo es "un patch": se arma en el COMP `red` de la
base cableando módulos, y `build_visual(source=...)` le pone el contrato de 5 sliders y audio.
**Quién.** LZX Industries, catálogo de funciones por módulo ([lzxindustries.net/modules](https://lzxindustries.net/modules));
el usuario ya tiene patches que recrean sintes LZX; ejemplo público de emulaciones en TD:
[wednesdayayay/Touch-designer](https://github.com/wednesdayayay/Touch-designer/blob/main/README.md) (FKG3, Topogram, colorizer, Memory Palace,
oscilador cuádruple → creador de rampas → efector de rampas). Antecedente: Sandin Image Processor, módulos con rangos estándar.
**Mapa módulo → TD** (nombre LZX: función según LZX → cómo en TD):

| Tipo | Módulos LZX | Operadores TD / esquema GLSL |
|---|---|---|
| Rampas | Cadet IV Dual Ramp, Scrolls (motion controlled), Angles (360°), Video Ramps | Ramp TOP, o GLSL `uv.x`, `uv.y`, rotadas por ángulo (`dot(uv-0.5, dir)+0.5`), desplazadas en el tiempo (Scrolls). Ver 36 |
| Osciladores | Prismatic Ray, DWO3 (dual wideband), Cadet IX VCO, Video Waveform Generator | GLSL `0.5+0.5*sin(2π(freq*rampa + fase))`; la rampa de entrada define la orientación; FM = sumar otra señal a la fase. Ver 36 |
| Formas | DSG3 (dual shape), Visual Cortex, Stacker (quadrilateral keys) | combinar rampas centradas: círculo `length`, diamante `|h|+|v|`, cuadro `max(|h|,|v|)`; luego keyer. Ver 42 |
| Waveshapers | Stairs (6-stage wavefolder), Staircase (five step), Arch (nonlinear), Doubler | `fract(x*n)`, plegado `1-abs(1-2*fract(x*n/2))`, `floor(x*n)/n`, `pow`, `smoothstep`; o Lookup TOP con una rampa dibujada. Ver 37 |
| Procesadores | Proc (triple), Cadet VII, Bridge (scaler/fader/mixer), Passage, PGO, Sum/Dist, Matte (offset) | Math TOP (gain, offset, invert), Composite TOP (add, subtract, max, min, difference), Level TOP |
| Multiplicadores | Factors (triple four-quadrant), Cadet X, PRM | GLSL `0.5+2*(a-0.5)*(b-0.5)` (cuatro cuadrantes, ring mod visual); Composite Multiply = dos cuadrantes. Ver 41 |
| Mezcladores | SMX3 (3×3 matrix), Color Chords (4-channel summing), Video Blending Matrix, Switcher, Pendulum (crossfader) | GLSL con `mat3` por píxel; Cross TOP; Switch TOP |
| Keyers | Cadet VIII Hard Key, Keychain (triple hard), Doorway (linear key), FKG3 (luma & chroma), Polar Fringe (chroma), Topogram (sequential soft key) | `step`/`smoothstep`; FKG3 = `mix(bg, fg, key)`; Topogram = cascada de keys suaves = bandas de nivel. Ver 38 |
| Color | Swatch (colorspace), Mapper (HSB → composite), Color Chords, Cadet II/ESG3 encoders, Jones Colorizer | Lookup TOP con rampa de paleta (`negro → color1 → color2 → blanco`); **nunca HSB libre en este rig**. Ver 38 |
| Coordenadas | Navigator (position & rotation), Shapechanger (coordinate transform), Marble Index (perspective & depth) | rotar/escalar rampas, polar (`atan`, `length`), división de perspectiva `uv/(1+z*k)`. Ver 42 |
| Filtros / bordes | Contour (VC high pass), Curtain (edge), Visionary Multimode Filter | `x - blur_h(x)` (pasa altos horizontal, como en analógico), Edge TOP, Blur TOP solo en x. Ver 43 |
| Digital / lógica | Castle (ADC, DAC, shift register, counter, logic gates), Ribbons (3-bit digitizer), Video Logic, Fortress (low-res graphics) | GLSL con enteros: `int(x*15.0) ^ int(y*15.0)`, `>>`, `&`; cuantizar a bits; Resolution TOP a baja resolución + nearest. Ver 41 |
| Memoria | Memory Palace (frame buffer & sampling), Diver (waveform sampler), TBC2 (video input) | Feedback TOP, Cache TOP, Texture 3D TOP; entrada: Video Device In / NDI In. Ver 40 |
| Ruido y CV | War of the Ants (static generator), Sensory Translator (5-ch envelope follower), Pendulum (animator) | Noise TOP; Audio Analysis / `u_low/u_mid/u_high`; LFO CHOP |

**Cómo en TD (convenciones).** Carpeta `library/lzx/` con un `.tox` por fila de la tabla; parámetros con el nombre de la perilla del módulo;
todos los TOPs internos `r32float` mono y a la resolución del rig; salida final por un único `colorizer` que lee `u_color1/u_color2`.
Cada patch de visual guarda un `.json` con su cableado para que un builder lo reconstruya (como `_lib/red_nodos.py`).
**Rig.** En un patch los 5 sliders se eligen entre las perillas: S1 nivel de salida del colorizer · S2 velocidad de scroll de rampas/fase de osciladores ·
S3 profundidad de modulación (FM o cantidad del multiplicador) · S4 punto de cruce color1↔color2 en el colorizer · S5 **la perilla que hace el patch**
(frecuencia del oscilador principal, umbral del keyer, pasos del wavefolder). Audio como CV: `u_low` a la frecuencia o al umbral, `u_kick` a un
trigger que cambia la fase o la rampa (cambio discreto), `u_high` a la ganancia del pasa altos.
**Rendimiento.** Cada módulo es un pase de pantalla: un patch de 10-15 módulos a 1080p sigue siendo barato; agrupar en un solo GLSL los que no
necesitan vecinos (rampas + oscilador + waveshaper + keyer caben en uno).
**Evitar.** Arcoíris de HSB (lo típico de video synth); patches que tiemblan enteros: dejar una señal lenta de base y una sola modulada por audio.
**Estado.** nueva (la librería). Partir de los patches LZX del usuario.

### 36. Rampas y osciladores de video
**Qué es.** El abecedario: una rampa es un gradiente; un oscilador a frecuencia de línea da barras verticales, a frecuencia de cuadro barras horizontales;
con la rampa rotada salen diagonales y con una rampa radial anillos. Dos osciladores multiplicados o sumados = moiré, tableros, interferencia.
**Quién.** LZX (Prismatic Ray, DWO3, Scrolls, Angles); Hypno (dos osciladores de forma con escala, rotación, color) ([Gearnews](https://www.gearnews.com/hypno-trippy-voltage-controlled-visual-oscillator-for-eurorack-or-desktop));
demo histórica del oscilador Visionary ([Synthtopia](https://www.synthtopia.com/content/2010/11/24/lzx-visionary-video-oscillator-demo/)).
**Cómo en TD.** GLSL de "voz": `r = rampa(ángulo)`; `o1 = osc(r*f1 + fase1 + fm*o2)`; `o2 = osc(r2*f2)`; salida mono. Rampa radial (`length(uv-0.5)`)
para respetar el sello: los osciladores dan anillos concéntricos.
**Rig.** S1 amplitud · S2 velocidad de fase · S3 profundidad FM · S4 cruce de tintas · S5 **frecuencia** (cantidad de bandas). `u_low` = FM, `u_kick` = salto de fase de 180°.
**Rendimiento.** Trivial.
**Evitar.** Frecuencias que generan aliasing a 1080p (más de ~300 ciclos por pantalla): limitar o antialias con `fwidth`.
**Estado.** parcial: `ring_chase.glsl`, `ring_matrix.glsl`, `ondas.glsl`; nueva como voz LZX.

### 37. Waveshapers (Stairs / Staircase / Arch)
**Qué es.** Una función no lineal aplicada a la señal: plegar (wavefolder) multiplica las bandas, escalonar (staircase) cuantiza en terrazas,
curvas (arch) cambian el perfil. Aplicado a una rampa radial convierte un degradado en N anillos nítidos.
**Quién.** LZX Stairs (6 stage wavefolder), Staircase (five step), Arch (nonlinear functions) ([módulos](https://lzxindustries.net/modules)).
**Cómo en TD.** GLSL o Lookup TOP. Plegado: `y = abs(fract(x*n*0.5)*2-1)`; escalera: `floor(x*n)/n` mezclada con la señal original;
arch: `pow(x, k)` o `smoothstep`.
**Rig.** S1 mezcla seco/procesado · S2 deriva de offset (la rampa entra desplazada, los pliegues "caminan") · S3 curvatura · S4 tinta por pliegue
(pares color1, impares color2) · S5 **número de pliegues/pasos**. `u_mid` = offset, `u_kick` = +1 paso.
**Estado.** nueva como módulo; el efecto aparece dentro de `contornos.glsl`.

### 38. Keyers y colorizers
**Qué es.** Un keyer convierte una señal en máscara por umbral (duro o suave); un colorizer asigna color por niveles de gris con varios keyers.
Es el corazón del look de los 70: cada banda de brillo de la imagen recibe una tinta plana.
**Quién.** Dave Jones Colorizer (keyers de gris por canal, Experimental Television Center, 1974-75) ([Video History Project](https://videohistoryproject.org/node/6893));
colorizer Paik/Abe; LZX Keychain, FKG3, Topogram, Doorway ([módulos](https://lzxindustries.net/modules)); emulación de FKG3 y Topogram en TD de
[wednesdayayay](https://github.com/wednesdayayay/Touch-designer/blob/main/README.md).
**Cómo en TD.** Keyer: `k = smoothstep(th - s, th + s, x)`. FKG3: `mix(bg, fg, k)`. Topogram: cascada `for i<N: k_i = smoothstep(th_i...)`, suma con pesos.
Colorizer del rig: `col = mix(negro, color1, k1)`, luego `mix(col, color2, k2)`, núcleos `k3` → blanco suave. Así el "video synth" queda dentro de la paleta.
**Rig.** S1 ganancia de entrada · S2 deriva de umbrales · S3 suavidad (duro ↔ suave) · S4 dónde cae color2 en la escala · S5 **número de bandas** (Topogram).
`u_kick` desplaza todos los umbrales un paso (las bandas "saltan").
**Rendimiento.** Trivial.
**Evitar.** Más de 3 tintas: el rig solo tiene dos más negro y blanco.
**Estado.** parcial: el post `post_pal_norte.glsl` y la pestaña Paleta ya hacen el mapeo a 2 tintas; nueva como módulo genérico.

### 39. Scan processor (Rutt/Etra)
**Qué es.** La imagen se dibuja como líneas de barrido horizontales cuya altura se desplaza según el brillo: el cuadro se vuelve relieve,
"paisaje fantasma". Posición, brillo y color se pueden modular entre sí.
**Quién.** Rutt/Etra Scan Processor (1972-73); los Vasulka lo usaron desde 1974 para reestructurar el cuadro (*Reminiscence*, *Golden Voyage*)
([Furlong](https://vasulka.org/Kitchen/essays_furlong/K_Furlong_13.html)); Jonas Bers hoy con instrumentos propios
([hackaday](https://hackaday.io/JonasBers)); Matthew Ragan, Rutt/Etra en TD ([post](https://d3nc4x5w0tphxs.cloudfront.net/blog/2014-04-27-td-rutt-etra)).
**Cómo en TD.** Opción 3D: Grid SOP/POP de N líneas (filas) × M puntos → desplazar z/y por la luminancia de un TOP (instancing o GLSL MAT
de vértice, skill `td-glsl-vertex`) → Line MAT fino → Render TOP con cámara levemente inclinada → bloom + feedback de fósforo.
Opción 2D en pixel shader: para cada fila `i`, `y_i = base_i + h*lum(x, base_i)`; dibujar con distancia a la curva y oclusión como en `cordillera.glsl`.
Fuente: cualquier visual del rig (el logo, un oscilador, el slit scan).
**Rig.** S1 brillo de línea · S2 velocidad de la fuente · S3 **altura del desplazamiento** · S4 tinta por altura · S5 número de líneas.
`u_low` = altura, `u_high` = jitter horizontal (ruido de deflexión), `u_kick` = rota la "cámara" del scan 90°.
**Rendimiento.** 200 líneas × 1000 puntos = 200k vértices: barato.
**Evitar.** Líneas gruesas; cámara 3D que gira mucho.
**Estado.** parcial: `cordillera.glsl` es un ridgeline de audio; nueva la versión que escanea una imagen (el sello).

### 40. Feedback de video analógico / frame buffer
**Qué es.** Lo que hace una cámara apuntada a su propio monitor, pero controlado: el cuadro anterior vuelve con zoom, rotación, desplazamiento
y ganancia positiva o negativa (invertir en cada vuelta da patrones que alternan). Con delay de varios cuadros (framebuffer delay) aparecen
ecos y espirales que tardan en cerrarse.
**Quién.** Vasulka, *Elements* (1971): feedback por keyer y switcher; LZX Memory Palace (frame buffer & video sampling); Hypno: la ganancia central
lleva la señal hasta que se retroalimenta y a la izquierda la invierte ([Gearnews](https://www.gearnews.com/hypno-trippy-voltage-controlled-visual-oscillator-for-eurorack-or-desktop));
Andrei Jay, *VIDEO_WAAAVES* y *WAAAVE_POOL* (framebuffer delay + feedback en Raspberry Pi) ([VIDEO_WAAAVES 2.5](https://github.com/ex-zee-ex/VIDEO_WAAAVES_2.5_suite),
[WAAAVE_GUIDE](https://github.com/rootnotez/WAAAVE_GUIDE)); emulación de Memory Palace en TD (VVeb, [wednesdayayay](https://github.com/wednesdayayay/Touch-designer/blob/main/README.md)).
**Cómo en TD.** `fuente → GLSL mezcla ← Cache TOP (delay N cuadros) ← Transform ← Feedback`. En el GLSL: `fb = texture(prev, T(uv))`;
`fb = mix(fb, 1-fb, neg)` (ganancia negativa); `out = keyer(fuente) ? fuente : fb*gain`. Delay variable: Cache TOP con `Output Index` animado
o Texture 3D + índice. Agregar un pasa-bajos horizontal mínimo en el loop para que "sangre" como analógico.
**Rig.** S1 ganancia (debajo de 1; la saturación queda en 0.98) · S2 rotación por vuelta · S3 zoom/desplazamiento · S4 cruce de tintas con la edad ·
S5 **delay en cuadros** (1 → 30). `u_kick` = invierte el signo de la ganancia una vuelta (destello negativo sin strobe), `u_low` = zoom.
**Rendimiento.** Cache de 30 cuadros a 1080p rgba16 ≈ 500 MB: usar mono o media resolución.
**Evitar.** Túnel por zoom continuo; ganancia ≥ 1 (pantalla blanca: RESET FEEDBACK).
**Estado.** parcial: `effects/echo_fractal.frag`, `effects/rgb_trail_decay.frag`; nueva la versión con delay y ganancia negativa.

### 41. Multiplicadores, matriz y lógica de bits
**Qué es.** Multiplicar dos señales centradas (cuatro cuadrantes) da modulación en anillo: dos osciladores se vuelven tablero o moiré.
La lógica de bits (XOR, AND, shift register) sobre rampas cuantizadas da los patrones "digitales de 8 bits" de los sintes Castle y de los primeros frame buffers.
**Quién.** LZX Factors, Cadet X, SMX3; serie Castle (ADC, compuertas, contador, shift register) y Ribbons (3-bit digitizer) ([módulos](https://lzxindustries.net/modules));
frame buffer 64×64 de Dave Jones (1977).
**Cómo en TD.** Multiplicador: `0.5 + 2*(a-0.5)*(b-0.5)`. Matriz: `vec3 out = M * vec3(a,b,c)` con M de uniforms. Lógica: `int A = int(a*15.0), B = int(b*15.0);
float o = float((A ^ B) & mask)/15.0;` shift register = desplazar bits con `u_step` (cada kick avanza el registro).
**Rig.** S1 nivel · S2 velocidad de las rampas · S3 cantidad de modulación · S4 tinta por bit · S5 **operación/máscara** (XOR, AND, OR, número de bits).
`u_kick` avanza el shift register; `u_high` = bit menos significativo con ruido.
**Rendimiento.** Trivial; usar `texelFetch`/nearest para que los bits sean nítidos.
**Evitar.** Pantalla completa de XOR (look demoscene de 1990): usarlo dentro de la máscara del sello o como textura de una forma.
**Estado.** nueva. Combina bien con 1 y 2 (línea Ikeda).

### 42. Formas y coordenadas desde rampas
**Qué es.** En un synth de video no se "dibujan" formas: se derivan de rampas. Dos rampas centradas dan círculo, diamante o cuadro según cómo se
combinen; rotar las rampas gira la forma; pasar a polar convierte barras en rayos y anillos; una división da perspectiva.
**Quién.** LZX DSG3 (dual shape generator), Navigator (position & rotation), Shapechanger (coordinate transformation), Marble Index (perspective & depth),
Stacker ([módulos](https://lzxindustries.net/modules)).
**Cómo en TD.** GLSL: `h = uv.x-0.5, v = uv.y-0.5` rotadas por `R(θ)`; `círculo = length(vec2(h,v))`, `diamante = abs(h)+abs(v)`, `cuadro = max(abs(h),abs(v))`;
morph entre normas con `pow(pow(|h|,p)+pow(|v|,p), 1/p)` (p de 1 a ∞). Polar: `(atan(v,h)/2π+0.5, length)`. Después, keyer (38) o waveshaper (37).
**Rig.** S1 tamaño · S2 rotación · S3 perspectiva/deformación · S4 tinta dentro/fuera · S5 **norma p** (diamante → círculo → cuadro).
`u_kick` = salto de forma, `u_low` = tamaño.
**Evitar.** Formas geométricas solas (el cliente ya rechazó lo geométrico genérico): usar como máscara del sello o fuente de un feedback (40).
**Estado.** parcial: `eclipse.glsl`, `op_sphere.glsl`; nueva como módulo.

### 43. CRT, scanlines y ancho de banda analógico
**Qué es.** El acabado que hace creíble un look analógico: scanlines, máscara de fósforo, sangrado horizontal por ancho de banda limitado,
un pasa altos que marca bordes (como el "enhance" de los monitores), ruido de sincronía leve.
**Quién.** Basement Vibes, *ANALOG_TV* (CRT con scanlines vía instancing 3D) y *Perfect Scanlines* ([Gumroad](https://basementvibes.gumroad.com/l/analogtv));
LZX Contour (VC high pass) y Curtain (edge processor).
**Cómo en TD.** Post GLSL: blur solo horizontal (5-9 taps) → `x + k*(x - blur_h(x))` (pasa altos) → scanlines `0.75+0.25*cos(uv.y*res.y*π)` →
máscara de fósforo sutil → bloom leve. Barato si va al final de un patch.
**Rig.** Va como post de otros visuales: S3 sangrado, S5 intensidad de scanlines. No como visual por sí mismo.
**Evitar.** VHS de filtro barato (bandas de colores que ruedan); el cliente es premium: CRT sutil.
**Estado.** ya en library: `effects/crt_pvm.frag`, `effects/crt_edge_bleed.frag`, `effects/04_scanline_interference.frag`.

### 44. Scanline reaction-diffusion
**Qué es.** Un solo loop de feedback que aplica "difusión" con un blur y "reacción" con un realce fuerte (sharpen + umbral), pero con el blur
y el realce **solo en horizontal**: salen patrones de RD alineados a las líneas de barrido, entre coral y señal de video.
**Quién.** Basement Vibes, *Scanline Reaction Diffusion* ("un solo loop de feedback con potencial de estilo video analógico")
([Gumroad](https://basementvibes.gumroad.com/l/abpumk)). La técnica de RD por blur + sharpen es la misma de
[Reaction-Diffusion feedback effects](https://derivative.ca/community-post/tutorial/reaction-diffusion-feedback-effects-touchdesigner-tutorial/66191).
Mi descripción del interior es una reconstrucción, no el contenido del tox (no lo abrí).
**Cómo en TD.** `Feedback → Blur TOP (solo x, o anisotrópico) → GLSL: x + k*(x - blur) → Level (contraste alto, umbral) → Feedback`; sembrar con la
fuente (el sello o un oscilador 36) mezclada al 5-10 %. A media resolución y float16.
**Rig.** S1 mezcla de semilla · S2 pasos por cuadro · S3 anisotropía (x ↔ x+y) · S4 tinta por densidad · S5 **realce (k)**: de manchas a laberinto.
`u_kick` re-siembra, `u_low` = cantidad de blur.
**Evitar.** Que llene todo: decay o máscara circular.
**Estado.** nueva (variante rápida de 8 sin simulación química).

---

## Top 10 de visuales nuevos para el próximo show

1. **Physarum en el sello** (receta 9): red de nodos viva con feedback, lo más cercano a "Pal Norte" pero con un sistema real; el kick hace respirar la red.
2. **Patch LZX "anillos del sello"** (35-38): rampa radial → oscilador → wavefolder → Topogram → colorizer de dos tintas; estrena la librería LZX del usuario y respeta las bandas concéntricas que pidió el cliente.
3. **Datamosh del logo** (20): time glitch y distorsión digital con intención; el kick es el I-frame que limpia y entre kicks todo se arrastra.
4. **Feedback analógico con delay y ganancia negativa** (40): el look Hypno / Video Waaaves dentro de la paleta; el kick invierte una vuelta sin hacer strobe.
5. **Atractor extraño en POPs** (14): millones de puntos finos sobre negro, nivel MUTEK, y estrena POPs en el rig.
6. **Scan processor del sello** (39): Rutt/Etra en TD, el logo como relieve de líneas que el bajo levanta; historia del video synth con acabado premium.
7. **Fluido real con emisores en el contorno del sello** (10): el "data pigment" de Anadol en dos tintas; el bajo empuja, el kick hace splat radial.
8. **Espiral de primos / filotaxis** (30): circular por naturaleza, matemática visible tipo Max Cooper; el kick ilumina brazos.
9. **Edge feedback del logo** (6): anillos concéntricos que nacen del sello alternando las dos tintas; barato y directo para el canal 11.
10. **Autómata celular 1D + lógica de bits** (2 + 41): la línea Ikeda más rigurosa; regla u operación en el slot 5, el kick siembra o avanza el registro.

Si hay tiempo: differential line growth desde un círculo (17), logo en point cloud que se disuelve (29) y scanline reaction-diffusion (44).

## Fuentes que no pude verificar del todo

- **"Andrew Jay"**: no apareció con ese nombre; lo que coincide (video synthesis, no usa TD) es **Andrei Jay**, autor de VIDEO_WAAAVES / WAAAVE_POOL.
  Los repos los vi en agregadores y en la guía `rootnotez/WAAAVE_GUIDE`; no abrí su canal de YouTube.
- **"World Wide Basement"**: lo más cercano es **Worldwide Basement Vibes / Basement Vibes** (tox en Gumroad y proyectos en alltd). No abrí los tox:
  la descripción técnica de las recetas 43-44 es reconstrucción a partir de sus textos de venta.
- **Ryan Carlile** y **Brown Noise Generator**: sin resultados que los relacionen con video synthesis. No los incluí como perfiles.
- **Supermarket Sallad**: sin material verificable. **VJ Fader**: solo el perfil de vjstv.
- **r/videosynthesis** y el foro de la comunidad LZX: no logré confirmar las páginas; la documentación de LZX está en lzxindustries.net.
- Los enlaces con † (sitios oficiales de artistas e instituciones) son de memoria y no los abrí en esta sesión.
- `iquilezles.org/articles/distfunctions2d` (primitivas 2D) devolvió 404/redirección al pedirlo; se cita la página general de distance functions.
- Fechas del Paik/Abe (1969 vs. 1972) varían entre fuentes; número de canales del Jones Colorizer (4 o 6) también.
- Detalles técnicos de Anadol y Ouchhh vienen de páginas de los estudios y prensa (autodeclarados). La autoría TD de *unitxt/univrs*
  (Markus Heckmann) viene de CDM, no de una fuente primaria.
- El post de Rutt/Etra en TD de Matthew Ragan lo encontré en un espejo (cloudfront), no en matthewragan.com.
- El hilo de Physarum del foro de Derivative es de un TD antiguo; puede no abrir en 2025.
- Qué artistas de medios programa hoy Fondation Cartier: no verificado.
