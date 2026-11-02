# Feedback Filters Set — TouchDesigner GLSL

Set de filtros GLSL para TouchDesigner construidos sobre un sistema de
feedback. Cada filtro explora una dirección estética distinta usando el
mismo esqueleto de red, pensados para **performance VJ en vivo**: 1080p,
60fps, parámetros expuestos para control en tiempo real.

---

## Índice

### Set original (categorías base)

| # | Filtro                                                | Categoría             | Firma visual                                  |
| - | ----------------------------------------------------- | --------------------- | --------------------------------------------- |
| 1 | [Kaleidoscopio Temporal Cinético](01_kaleidoscopio_temporal.md) | Espacial              | Movimiento — pliegue radial + zoom + rotación. |
| 2 | [RGB Trail Decay](02_rgb_trail_decay.md)              | Cromático             | Color — decay y desfase independientes por canal. |
| 3 | [Liquid Memory](03_liquid_memory.md)                  | Distorsión            | Deformación — flujo siguiendo isolíneas de luminancia. |
| 4 | [Echo Fractal](04_echo_fractal.md)                    | Híbrido               | Espiral cromática que respira y responde al contenido. |

### Extensiones (línea Liquid + Echo)

Los 3 siguientes extienden los principios de Liquid Memory y Echo Fractal:
gradiente de luminancia como motor de transformación, modulación por
contenido, mucho feedback con `uMix` bajo. Pensados para sesiones donde
quieres que el feedback DOMINE la imagen, no que la decore.

| # | Filtro                                                | Categoría             | Firma visual                                  |
| - | ----------------------------------------------------- | --------------------- | --------------------------------------------- |
| 5 | [Plasma Currents](05_plasma_currents.md)              | Distorsión avanzada   | Filamentos — corriente + presión, plasma solar. |
| 6 | [Spectral Mitosis](06_spectral_mitosis.md)            | Híbrido content-driven | Mitosis — división cromática SOLO en los bordes. |
| 7 | [Memory Marbling](07_memory_marbling.md)              | Distorsión + cromático | Mármol — domain warping recursivo, espirales. |

### Austin Psych Fest set (shaders externos, integrados al builder)

Set psicodélico provisto en archivos `.frag` separados. Shaders más simples
y estéticamente "vintage" (oil & water, CRT, VHS, solarize). Los preservé
verbatim — el builder los carga y expone sus uniforms igual que los demás.

| #  | Filtro                                                | Archivo fuente                  | Firma visual                                 |
| -- | ----------------------------------------------------- | ------------------------------- | -------------------------------------------- |
| 8  | Liquid Light Show                                     | `01_liquid_light_show.frag`     | Oil & water — desplazamiento por luma.       |
| 9  | CRT Edge Bleed                                        | `02_crt_edge_bleed.frag`        | Fósforo CRT — bleed cromático en bordes brillantes. |
| 10 | Geometric Mandelwarp                                  | `03_geometric_mandelwarp.frag`  | Fractal — rotación + escala infinita + solarize. |
| 11 | Scanline Interference                                 | `04_scanline_interference.frag` | VHS — onda sinusoidal horizontal + ruido.   |
| 12 | Color Cycle Solarize                                  | `05_color_cycle_solarize.frag`  | Hue cycling + solarize por luma.             |

---

## Esqueleto común de red

Todos los filtros comparten exactamente la misma topología:

```
[Source TOP]                          (video / cámara / generador)
     |
     v
   in0
[GLSL TOP: <nombre_filtro>]           (donde vive el shader)
     ^                  |
     |                  |
   in1                  v
     |       [Feedback TOP: fb_<nombre>]
     +----<--+ Target = "<nombre_filtro>"
             |
             v
        [Null TOP: out]
```

**Reglas:**
- `sTD2DInputs[0]` es siempre el **input nuevo** (la fuente).
- `sTD2DInputs[1]` es siempre el **feedback** (frame anterior).
- El Feedback TOP debe apuntar (Target) al GLSL TOP correspondiente.
- Pixel Format **16-bit float (RGBA)** en GLSL TOP y Feedback TOP. 8-bit acumula banding rápido.
- Resolution: 1920 × 1080 (o múltiplo del display de salida).

---

## Convenciones de uniforms

Todos los filtros respetan estos nombres comunes para que sean intercambiables
en una consola de control:

| Uniform   | Significado                            |
| --------- | -------------------------------------- |
| `uDecay`  | Persistencia del feedback (0–1).       |
| `uMix`    | Cantidad de input nuevo inyectado.     |
| `uTime`   | Reloj global (`absTime.seconds`) si aplica. |

Los uniforms específicos de cada filtro están documentados en su propio MD.

---

## Construcción automática

El archivo `feedback_filters_builder.py` (en esta misma carpeta) construye
cualquiera de los 12 filtros como Base COMP con custom parameters expuestos
y uniforms enlazados por expresión.

Uso desde el Textport de TouchDesigner:

```python
mod('builder').build('kaleido')       # 01
mod('builder').build('rgb_trail')     # 02
mod('builder').build('liquid')        # 03
mod('builder').build('echo_fractal')  # 04
mod('builder').build('plasma')        # 05
mod('builder').build('mitosis')       # 06
mod('builder').build('marbling')      # 07
mod('builder').build('liquid_light')  # 08 (psych fest)
mod('builder').build('crt')           # 09 (psych fest)
mod('builder').build('mandelwarp')    # 10 (psych fest)
mod('builder').build('scanline')      # 11 (psych fest)
mod('builder').build('solarize')      # 12 (psych fest)
mod('builder').build_all()            # los 12 de un golpe
```

Cada Base COMP creado expone una página custom con todos los controles
listos para mapear a MIDI/OSC.

---

## Tips generales para VJing

- **Anti-saturación**: ningún filtro tiene `uDecay >= 1.0` por defecto. Mantén siempre <1.0 o el feedback se va a blanco. Si quieres congelar momentáneamente, sube a 0.999 con `uMix = 0`.
- **Mapeo a controlador**: por filtro, identifica 1 knob "estrella" + 1 fader principal + 1 XY pad. Ese trío suele bastar para set entero.
- **Reset rápido**: bind un botón a `uDecay = 0` por un frame; limpia el feedback al instante.
- **Mismo Source, varios filtros**: el Source TOP puede alimentar varios Base COMPs paralelos. Cambiar entre filtros con un Switch TOP a la salida es la forma más limpia de hacer "preset cycling" en vivo.
- **Captura de estados**: si tienes un sweet spot, guarda un Preset COMP de la página custom del Base COMP.

---

## Performance esperado

| Filtro            | Texture fetches | Costo relativo | Notas                                    |
| ----------------- | --------------- | -------------- | ---------------------------------------- |
| 01 Kaleidoscopio  | 2               | Bajo           | Trivial.                                 |
| 02 RGB Trail      | 4               | Bajo           | `pow()` y HSV son baratos.               |
| 03 Liquid Memory  | 5               | Medio          | Gradiente con cruz de 4 muestras.        |
| 04 Echo Fractal   | 7               | Medio-Alto     |                                          |
| 05 Plasma Currents| 7               | Medio-Alto     | Gradiente + 3 canales independientes.    |
| 06 Spectral Mitosis| 7              | Medio-Alto     | Gradiente + split modulado.              |
| 07 Memory Marbling| 5               | Medio          | Sin gradiente; warping recursivo.        |

A 1080p en GPU dedicada moderna (RTX 2060 hacia arriba) los 7 corren con
margen a 60fps. A 4K, los filtros 04 / 05 / 06 son los primeros candidatos
a bajar FPS — en ese caso, reducir el gradiente a 2 fetches recupera mucho.

---

## Sobre exportación a .tox / .toe

TouchDesigner no expone una API offline para construir networks desde fuera
de la app. Las opciones son:

1. **Auto-construir vía script** (recomendado): usar `feedback_filters_builder.py`
   como Text DAT y llamar `build(...)`. Es la forma más rápida.
2. **Empaquetar después**: una vez construido un filtro, seleccionar el
   Base COMP, click derecho → `Save Component .tox`. Lo dejas como módulo
   reutilizable.

---

## Líneas de exploración (para mapa mental)

- **Espacial puro (01)**: la transformación es estática, no depende del contenido.
- **Cromático puro (02)**: cada canal RGB tiene su propia "memoria temporal".
- **Distorsión content-driven (03, 05, 07)**: el propio feedback genera el campo de displacement. La imagen reorganiza la imagen.
- **Híbridos modulados por contenido (04, 06)**: transformaciones espaciales/cromáticas cuya intensidad depende del gradiente — el filtro **responde** a lo que está pasando en pantalla.
