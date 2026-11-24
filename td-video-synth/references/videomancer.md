# LZX Videomancer — resumen para recrearlo

Fuente primaria: VHDL en github.com/lzxindustries/videomancer-sdk y github.com/lzxindustries/videomancer-community-programs (GPL-3.0), + manual oficial. Investigacion larga en `research/lzx_videomancer.md` del proyecto.

## Arquitectura
- **FPGA Lattice iCE40 HX4K** (~128 kbit BRAM), MCU RP2040, chips ADV7181C/7611/7513/7393.
- **Senal: YUV 4:4:4 a 10 bit**, U/V centrados en 512, espacio BT.601. Latencia 50 ns - 1.5 µs.
- **No tiene frame store** — todo el "feedback" es por **linea** con buffers de 2048 px o diminutos (128x64 a 4 bit, 256x128 a 1 bit, 64x36 Shadebob).
- Registros se **cargan en cada HSYNC**: hay modulacion por scanline (clave del look).

## Controles (ABI de program)
- 12 parametros por program: **P1-P6 perillas, S7-S11 switches, F12 fader** (casi siempre Mix o key a negro).
- 23 operadores de modulacion (LFO, Turing, Logistic, Euclidean...) + CV/audio 4 canales + MIDI.

## Programs embebidos (27) + biblioteca LZX (6)
Lo que esta en el VHDL del SDK (formula exacta) vs lo reconstruido del manual:

### Con codigo fuente leido (SDK)
- **Howler** (feedback por linea, buffer 2048 px). Pseudo: `out[x] = mix(in[x], prev_line[warp(x)], fb)` con warp controlado por P1-P2.
- **Sabattier** (solarizacion): curvas S y W; formula Mackie: `y = y < th ? 2*(th-y)+off : y`. S/W switch cambia de polaridad.
- **STIC** (quantize retro): paleta YUV fija de 16 colores + ditcher; LUT publicada en el VHDL.
- **Pong, Colorbars, Mycelium, Kintsugi, Perlin, YUV Amplifier**: codigo en SDK.

### Reconstruidos del manual (sin VHDL publico)
- **Elastica** (Scanimate Warp): warp senoidal por linea, `uv.x += amp*sin(uv.y*freq + phase)`.
- **Glorious** (Technicolor Film): tres separaciones YUV con registros corridos (misreg color).
- **Isotherm** (Thermal False Color): LUT de 8 bandas en Y mapeadas a colores calidos.
- **Scramble** (Signal Scramble): barajar segmentos horizontales con permutacion por linea.
- **Stipple** (Pop Art Posterize): quantize + dither Bayer.
- **Corollas, Pinwheel**: osciladores radiales con `atan2`.
- **Lumarian, Delirium, Faultplane, Fauxtress, Bitcullis, YUV Phaser, Teletect (x6)**: ver investigacion larga.

### Nombres comerciales -> internos
- Pop Art Posterize = **stipple**, Technicolor Film = **glorious**, Signal Scramble = **scramble**, Scanimate Warp = **elastica**, Thermal False Color = **isotherm**, Retro Color Quantize = **stic**.

### Community programs (~110)
Casi todos de czartroniks. Cada uno con VHDL + TOML. Tipos: feedback lineal, LUT YUV, warp, counter/logic, mini-framebuffer, ritmo.

## Receta general en TouchDesigner
1. **Trabajar en YUV** dentro del shader (`rgb2yuv_bt601`, procesar, `yuv2rgb_bt601` al final). No HSB.
2. Para programs **con feedback por linea**: usar un **Feedback TOP** o un buffer 1D leido por `texture(prev, vec2(x, line-1))`; la clave es que el feedback es **1 linea atras**, no el cuadro entero.
3. Para programs con **mini-framebuffer** (128x64 etc.): correr el GLSL a esa resolucion baja, luego `Resolution TOP` nearest a 1080p; eso da el look pixelado real.
4. **Modulacion por HSYNC**: declarar los uniforms del program (P1-P6, S7-S11, F12) y mezclarlos con una **rampa de linea** (`floor(uv.y*res.y)`) y los operadores (LFO, Turing...). Un LFO en TD = un `absTime.seconds` o un `LFO CHOP` aplicado al uniform **por linea**, no por cuadro: eso solo se hace dentro del shader.
5. Color: igual que Mainbow, mapear al colorizer de paleta del rig al final, NO sacar YUV crudo.

## Mapa a los 5 sliders del rig (por tipo de program)
Como hay 27 programs, la receta es: elegir **un program por visual** (una base por program). El contrato queda:
- S1 Intensidad (= amplitud/mix) · S2 Velocidad (= modulacion por linea, LFO rate) · S3 **la perilla principal** del program · S4 Cruce de paleta · S5 **la perilla de firma** (P1 o el switch que mas cambia el look).
- Las otras P2-P6 y los switches pasan a `signature_extras` (aparecen en la UI con el nombre del VHDL).

## Que programar primero
1. **Howler** (feedback por linea con buffer 2048 px) — el mas distintivo del Videomancer y no se parece a nada de VVeb.
2. **Sabattier** (solarizacion con curvas S/W) — barato y muy "LZX".
3. **STIC** — paleta YUV fija, bonito con el mapeo a paleta del rig.
4. **Elastica** — warp senoidal, trivial.
5. **Glorious** — misreg triple, muy cinematografico.

Luego: ir eligiendo community programs del repo czartroniks por su TOML + preview.
