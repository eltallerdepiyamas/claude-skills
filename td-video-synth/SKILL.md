---
name: td-video-synth
description: Recrea sintetizadores de video (LZX Videomancer y modulos LZX Eurorack, Chroma Cauldron Mainbow, Memory Palace, Rutt/Etra, colorizers Jones, Hypno, WAAAVES) dentro de TouchDesigner como "patches" de GLSL con la convencion de senal 0-1 de LZX, y los monta como visual o FX del rig del usuario. Usalo SIEMPRE que el usuario pida un video synth, "algo como LZX", "como el Videomancer", "como el Mainbow", rampas/osciladores/keyers/colorizers/wavefolders de video, look analogico de video synthesis, emular un modulo, o recrear un program de Videomancer — aunque no diga "shader". Para construir la base del rig se combina con td-vj-builder (contrato de 5 sliders) y td-glsl.
---

# TD Video Synth

Recrear sintes de video como patches en TouchDesigner. Todo sale como **un shader GLSL + un builder `setup_baseN_*.py`** del rig (ver skill `td-vj-builder`), o como `.tox` de modulo en `library/lzx/` si es pieza reutilizable.

## 1. La idea que manda (LZX)
- **Toda senal es 0..1** (0-1 V en LZX). Rampa, oscilador, key, CV de audio: todo se puede conectar a todo.
- **Una senal = un float por pixel.** En TD: TOP mono `r32float` (o un `float` dentro del mismo GLSL).
- Orden clasico de un patch: **rampas → osciladores/formas → waveshaper → proceso/mezcla → keyer → colorizer**. El color va AL FINAL.
- Coordenadas = rampas. Nunca "dibujar": derivar formas combinando rampas (`length`, `abs+abs`, `max`).
- **CV** = audio y LFO: `u_bass` (Energy del rig), LFO CHOP, S&H. Un parametro modulado = `base + depth*(cv-0.5)`.

## 2. Libreria
`templates/vsynth_core.glsl` trae los modulos como funciones (rampas, osc, fold/stairs/arch, mul4q, keyers, topogram, formas por norma p, logica de bits, ruido, colorizer de paleta). **Copiar las funciones que se usen dentro del shader del visual** (TD no tiene `#include`). Mapa completo modulo LZX → TD: `research/recetario_tecnicas.md` seccion G (recetas 35-44) del proyecto.

## 3. Equipos de referencia
- **LZX Videomancer** (FPGA, programs): `references/videomancer.md` — cada program con su algoritmo y receta en TD.
- **Chroma Cauldron Mainbow** (4 generadores de funcion + encoder con wavefold, HSL + alpha): `references/mainbow.md`.
- Investigacion larga con fuentes: `research/lzx_videomancer.md` y `research/mainbow.md` del proyecto BOILERPLATE_TD.
- Patches de TD del usuario que emulan LZX (DreamWeaver, FKG3, Topogram, RGBbander, VVeb/Memory Palace): `_referencia/LZX/`. VVeb ya es modulo del rig (`modulos/lzx_vveb`).

## 4. Como construir un patch en el rig
1. Elegir 3-6 modulos y escribir el cableado como comentario arriba del shader (`// ramp(ang) -> oscFM -> fold -> keySoft -> colorize2`).
2. Un solo GLSL si ningun modulo necesita vecinos ni memoria. Separar en TOPs solo para: blur/filtro (Contour, pasa altos), **feedback / frame buffer** (`build_visual(feedback=True)` o Cache TOP para delay de N cuadros), o entrada de video (`source=`).
3. Contrato de 5 sliders (rig): S1 nivel/intensidad · S2 velocidad (scroll de rampas, fase) · S3 profundidad de modulacion (FM, multiplicador, distorsion) · S4 color = punto de cruce en el colorizer · **S5 firma = la perilla que hace el patch** (frecuencia, pasos del fold, umbral, norma p, bits). Lo demas va como `signature_extras` (aparece en la UI) con el nombre de la perilla original.
4. Audio: `u_bass` a frecuencia/umbral/zoom (continuo); un kick a salto de fase o +1 paso (discreto). Nunca todo el patch temblando: una senal lenta de base y una modulada.
5. Color: **siempre de la paleta** (`u_color1..3` del rig) con `colorize2` o Lookup TOP; nunca HSB libre ni arcoiris, aunque el original lo haga (el hue del Mainbow/Videomancer se traduce a "posicion en la paleta").
6. Acabado opcional: CRT sutil (`effects/crt_pvm.frag`), pasa altos horizontal para el borde analogico.
7. Correr el builder por el MCP de TouchDesigner (`correr_script`) y ver con `ver_salida`; revisar `errores`.

## 5. Reglas
- Nombrar los uniforms y extras como la perilla del equipo original (`u_fold`, `u_keythresh`), en la UI en espanol.
- Frecuencias altas: limitar (< ~300 ciclos por pantalla a 1080p) o antialias con `fwidth`.
- Feedback: ganancia < 1 (0.98 tope), siempre con RESET FEEDBACK funcionando.
- Logica de bits: `texelFetch`/nearest para bits nitidos.
- Lo que no se verifico en fuente primaria (ver `references/`) se dice como "reconstruccion", no como "asi lo hace el equipo".
