# Mainbow — resumen para recrearlo

Fuente primaria: `OwnersManual.pdf` (v1, github.com/RussellKramer/Mainbow). Investigacion larga en `research/mainbow.md` del proyecto.

## Arquitectura
- **Analogico**, no MCU. Un PIC16F15344 solo hace sync, resets X/Y, subportadora NTSC (3.579 MHz) / PAL (17.734 MHz), genlock y filtro de audio.
- Senal LZX 0-1 V en todo el patchbay. Salida compuesta (luma + croma cuadrada), mezclador final por 2 JFET J113 (alpha).
- Bloques: 4 **function generators** -> wavefolders HUE/SAT/LUMA/ALPHA -> encoder de color -> mezcla con video externo.

## 4 function generators (identicos)
- Rampa por carga de capacitor con fuente de corriente (555 + J113 + TL974). **FM multiplica la frecuencia** (no suma a la fase). **PM se muestrea al inicio de linea (X) o cuadro (Y)**, no por pixel — por eso PM solo trabaja en modos X/Y.
- 4 modos (switch 2P4T, elige el capacitor):
  - **X** (1 nF): ~1-11 ciclos por linea. Barras verticales.
  - **Y** (200 nF): barras horizontales.
  - **S** (Scroll, 200 nF libre): corre libre en tiempo de raster.
  - **LFO** (100 µF): ~0.16-1.7 Hz.
- 7 formas (selector 1P7T): rampa, triangulo, seno(ish), cuadrada (pulso fijo del 555), y variantes. **Pulse = ancho fijo en tiempo** (no en fase).
- Entradas por FG (todas con splitter): **MIX** (suma 50 %), **AM** (multiplica amplitud), **FM** (multiplica frecuencia), **PM** (fase, solo X/Y). Perillas AMP y FREQ.
- Salida 0-1 V y RCA monocromo con sync sumado (preview por FG).

## Wavefolder (HUE, LUMA, SAT, ALPHA)
- **No es triangle folder.** Es cadena residuo de 3 bits (gain 4, luego 3 etapas HC4050 + op-amp: `r = 2r - bit`).
- **Soft**: `fract(8*u)`, diente de sierra con 8 wraps (coincide con "hasta ocho veces" del manual).
- **Hard**: `floor(8*u) mod 2`, cuadradas duras.
- Cada seccion tiene 2 jacks (splitter), perilla FOLD y boton hard/soft.

## Codificador de color (hue, sat, luma)
- **Hue = fase de la subportadora**, armada con dos 74HC123 (monoestables): delay por hue CV -> delay de hue limit -> shift delay con feedback (glitches) -> pulso fijo. Boton +180° intercambia Q/Q̄.
- **Chroma rectangular**, no sinusoidal (cuadrada montada en la subportadora).
- Saturacion = amplitud de la chroma. HUE SHIFT tope CW = **monocromo** (chroma a 0).
- **Glitch A/B**: error de frecuencia del genlock -> rayas horizontales de arcoiris; recuento ~ `Δf * tiempo_de_linea`. Para recrearlo: hacer el color en **YUV** (mas cercano al hardware) y agregar una fase extra `Δf*t_h` modulada por el switch.

## Alpha + video externo
- Alpha wavefolder -> dos JFET cruzados hacen crossfade entre croma sintetica y luma externa. Sin video externo, se desvanece a negro.
- **BLUR**: pasa-bajos de un polo a lo largo de la linea de barrido (smear horizontal solo a la derecha). No es blur 2D.

## Audio
- El PIC muestrea el audio y saca CV lento (cutoff ~80 Hz). 4 modos (switch FILTER): grafico entrelazado, beat con decay, scrolling, centrado. Algoritmo exacto no publicado.

## v1 vs v2
- v1: 48 HP, DIY, descontinuada, trimmers de hue y alpha manuales, placa expansion PAL opcional.
- v2: 52 HP, 18 mm fondo, $220, NTSC+PAL automatico [NV], genlock automatico [NV], panel aluminio [NV]. Mismo principio analogico.

## Receta de recreacion en TouchDesigner
Red con 5 TOPs:
1. **Audio CHOP** -> history/decay/scroll segun el modo -> CV uniform.
2. **Video externo** (NDI In / Video Device In) -> Luma (`dot(rgb, vec3(.299,.587,.114))`) -> blur horizontal 1-pole.
3. **GLSL `mb_fg`**: rinde los 4 FG como RGBA (R=FG1, G=FG2, B=FG3, A=FG4). Dentro del shader: cada canal corre el nucleo
   (mode X/Y/S/LFO -> `fract(freq*coord + phase)` -> forma seleccionada por un `int`), aplica MIX/AM/FM y PM solo en X/Y
   (muestrear PM al reset de linea/cuadro, es decir usar `uv.y` cuantizado).
4. **GLSL `mb_enc`**: toma los 4 FG + luma externa + alpha y devuelve color. Wavefolders como `fract(8*x)` o `floor(8*x) mod 2`
   segun el switch. Color en **YUV**: `U = SAT*cos(hue*TAU + glitch*uv.y*k)`, `V = SAT*sin(...)`, luego YUV->RGB. Alpha JFET
   se simula como `mix(externa, sintetica, smoothstep(0.1,0.9,alpha))`, con "gap" dejando 0.45..0.55 oscuro cuando ALPHA TUNING
   esta mal.
5. **Opcional NTSC emulado**: encode a compuesto a 754 px (227.5*4 muestras/linea) con la subportadora cuadrada, luego decode, para
   recuperar dot crawl y rainbowing real.

Feedback / pases: historia de audio, decay del beat, patches ciclicos (AM->FM->PM entre FG), integracion FM a lo largo de la
linea, y el blur horizontal.

## Mapa a los 5 sliders del rig
- S1 AMP del FG principal · S2 Scroll · S3 profundidad FM · S4 HUE SHIFT (cruce de paleta) · S5 FOLD (la firma del Mainbow).
- Extras en la UI: modo X/Y/S/LFO, forma (0-6), hard/soft, GLITCH (A/OFF/B), ALPHA.
- **Color SIEMPRE por la paleta del rig**: en vez de `hue -> RGB`, usar `hue -> t` para `colorize2(t, bg, c1, c2, cross)`.
