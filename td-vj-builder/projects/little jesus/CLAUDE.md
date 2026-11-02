# CLAUDE.md — Little Jesus VJ Project
## TouchDesigner 2023 | escena_modular | Live VJing System

---

## Estructura Real del Proyecto

```
/project2
  └── escena_modular (Base COMP)
        ├── CAM_1 ... CAM_5        ← Video Device In TOPs
        ├── base17                 ← LAYOUT DE CÁMARAS (switch interno de layouts)
        ├── base18 – base24        ← EFECTOS post-layout
        ├── base38 – base45        ← EFECTOS FUTUROS
        └── switch_FINAL           ← routing por "Modo escena"
```

### Cadena de señal
```
CAM_1..5 → base17 (layout activo) → baseXX (efecto) → switch_FINAL → OUT
```

---

## Custom Parameters de `escena_modular` (NO recrear)

### Pestaña **Camaras**

| Parameter | Tipo | Descripción |
|-----------|------|-------------|
| `Modo escena` | Menu | Efecto activo → `switch_FINAL` |
| `Camaras en multicam` | Int (2–5) | Cámaras simultáneas. Mínimo 2, máximo 5 |
| `Modelayout` | Menu | Layout activo dentro de `base17` |
| `Index` | Int | Cámara hero |
| `Cam` | Menu | Cámara en modo full single |
| `Camfit` | Int | 0=Fill (default), 1=Fit, 2=Stretch |

### Pestaña **Resolucion**

| Parameter | Tipo |
|-----------|------|
| `ResW` | Int |
| `ResH` | Int |

> Siempre: `op('escena_modular').par.ResW` / `.par.ResH`. Nunca hardcodear.

---

## ⚠️ CORRECCIONES PENDIENTES — Leer y aplicar antes de cualquier otra tarea

### FIX 1 — `layout_split_asimetrico.frag`
El shader tiene uniforms con nombres incorrectos (`uSplitAmt`, `uSplitSpeed`). Los nombres correctos que el script asigna son:
`uTime`, `uResolution`, `uCamCount`, `uSplitRatio`, `uOrientation`, `uGap`, `uCamfit`, `uCamAspect`, `uBgColor`.
**Acción:** Abrir `layout_split_asimetrico.frag` y renombrar/eliminar uniforms para que coincidan exactamente con esa lista. Nada más, nada menos.

### FIX 2 — `layout_gridwall_drift.frag`
El shader tiene `uSpread` que no le corresponde. Los uniforms correctos son:
`uTime`, `uResolution`, `uCamCount`, `uSpeed`, `uDirection`, `uSizeVariance`, `uCamfit`, `uCamAspect`, `uBgColor`.
**Acción:** Eliminar `uSpread` del shader.

### FIX 3 — `layout_pip.frag` — bordes negros
En modo Fill (0), reemplazar black fallback por clamp:
```glsl
if (uCamfit != 1) fitUV = clamp(fitUV, 0.0, 1.0);
else if (fitUV.x < 0.0 || fitUV.x > 1.0 || fitUV.y < 0.0 || fitUV.y > 1.0) return vec4(0.0);
```

### FIX 4 — `layout_orbit_dance` — uniforms faltantes
Warnings: `uBgScale` y `uHeroMode` no están asignados en Vectors del GLSL TOP `glsl_layout`.

**Acción en el GLSL TOP (Vectors page):**
- `uBgScale` → expression: `parent().par.Bgscale`
- `uHeroMode` → expression: `0` (fijo)

**Si `Bgscale` no existe como Custom Parameter en `layout_orbit_dance`:** crearlo como float, default 1.0, rango 0.5–3.0. Exponerlo en `escena_modular` página `Orbit` como `OrbitBgscale` con BIND a `parent().par.Bgscale`.

**En el shader `layout_orbit_dance.frag`:** aplicar `uBgScale` al UV de la cámara de fondo:
```glsl
uniform float uBgScale;
uniform int   uHeroMode;  // reservado, usar 0
// Al samplear fondo:
vec2 bgUV = (uv - 0.5) / uBgScale + 0.5;
bgUV = clamp(bgUV, 0.0, 1.0);
vec4 bg = texture(sTD2DInputs[heroIdx], bgUV);
```

### FIX 5 — `layout_ripple_grid.frag` — reemplazar completamente
El shader actual no es atractivo visualmente. Reescribir completamente con este concepto:

**Nuevo efecto — Zoom Pulse Grid:** grid de cámaras donde cada celda hace zoom in/out con una onda sinusoidal desfasada por índice. Como si cada cámara respirara a distinto tiempo pero más dramático. El zoom escala el UV desde el centro de la celda.

**Guardar como `layout_ripple_grid.frag`** (mismo nombre, el script ya lo referencia).

**Uniforms** (mismos que ya asigna el script — no cambiar nombres):
`uTime`, `uResolution`, `uCamCount`, `uSpeed`, `uRippleAmt`, `uRippleFreq`, `uCamfit`, `uCamAspect`, `uBgColor`

**Lógica del zoom en el shader:**
```glsl
// Por cada celda índice idx:
float phase = float(idx) * uRippleFreq;
float zoom = 1.0 + sin(uTime * uSpeed + phase) * uRippleAmt;
// Aplicar zoom al UV local desde el centro:
vec2 zoomedUV = (localUV - 0.5) / zoom + 0.5;
// Luego pasar zoomedUV a sampleCam()
```

**Regla:** usar siempre `sTD2DInputs[index]` — NUNCA `uniform sampler2D`.

### Después de aplicar todos los fixes:
Correr `setup_all_layouts` para que `escena_modular` se actualice con los nuevos parámetros.

---

## ⚠️ PENDIENTE — Modo escena y navegación por pestañas

### 1. Agregar todos los layouts al Menu `Modo escena`
El Menu Parameter `Modo escena` en la pestaña `Camaras` de `escena_modular` debe tener estas opciones (en orden):
```
Multicam 4
Hero Central
Grid Dinamico
Full Solo
layout_gridwall
layout_pip
layout_split_asimetrico
layout_gridwall_drift
layout_float_chaos
layout_wave_scroll
layout_magnetic_pull
layout_pendulum
layout_floating_pieces
layout_orbit_dance
layout_ripple_grid
layout_breathing_grid
layout_swarm
```
**Acción:** Editar el Menu Parameter `Modo escena` en `escena_modular` y agregar las opciones faltantes (de `layout_gridwall` en adelante). Los Labels pueden ser el nombre limpio, los Values deben ser el nombre exacto del Base COMP.

### 2. Parámetro `Escena activa` en cada pestaña de layout
En cada pestaña de layout (Gridwall, Pip, Splitasim, Griddrift, Floatchaos, Wavescroll, Magnetic, Pendulum, Floating, Orbit, Ripple, Breathe, Swarm), agregar un parámetro que refleje y permita cambiar `Modo escena`.

**Implementación:** En `_expose_to_scene()` del setup script, al crear la página de cada layout en `escena_modular`, agregar al inicio de la página un parámetro tipo `String` o `Menu` llamado `Escenaactiva` con BIND bidireccional a `op('escena_modular').par.Modoescena`.

Así desde cualquier pestaña se puede ver en qué escena se está y cambiarla sin ir a la pestaña Camaras.

---

## Reglas Fundamentales

1. **Mínimo 2 cámaras siempre.**
2. **Resolución siempre desde `escena_modular`.**
3. **GLSL TOPs: NUNCA `uniform sampler2D sCamX`.** Usar `sTD2DInputs[index]`.
4. **Todos los uniforms asignados en página Vectors del GLSL TOP.**
5. **Todos los layouts son GLSL TOPs** — no Containers, no Python setup scripts.
6. **`uCamfit` en todos los layouts** — controla el modo de ajuste de aspecto de cámara dentro del shader.
7. **Movimiento: siempre con funciones sinusoidales + `uLag` o lag en expressions.** Nunca saltos.
8. **Todo layout nuevo → agregar a Switch interno de base17 + Menu `Modelayout`.**

---

## ⚠️ CONVENCIÓN CRÍTICA: SAMPLERS EN GLSL

```glsl
// ❌ MAL — genera warnings en TD:
uniform sampler2D sCam0;

// ✅ BIEN — convención nativa TouchDesigner:
texture(sTD2DInputs[0], uv)  // CAM_1 (input 0 del GLSL TOP)
texture(sTD2DInputs[1], uv)  // CAM_2 (input 1)
texture(sTD2DInputs[2], uv)  // CAM_3 (input 2)
texture(sTD2DInputs[3], uv)  // CAM_4 (input 3)
texture(sTD2DInputs[4], uv)  // CAM_5 (input 4)
// NO se declaran — TouchDesigner los provee automáticamente.
```

---

## Función de Fit — Incluir en TODOS los shaders de layout

Esta función resuelve el ajuste de aspecto de cada cámara dentro de su celda. Se llama por cada cámara antes de hacer el `texture()`.

```glsl
// Ajusta el UV de una cámara a su celda según el modo de fit
// cellUV: UV local dentro de la celda (0..1, 0..1)
// camAspect: aspecto de la cámara fuente (ej. 16.0/9.0)
// cellAspect: aspecto de la celda destino (cellW/cellH en píxeles)
// fitMode: 0=Fill, 1=Fit, 2=Stretch
vec2 applyCamFit(vec2 cellUV, float camAspect, float cellAspect, int fitMode) {
    if (fitMode == 2) {
        // Stretch: sin cambios, usa el UV tal cual
        return cellUV;
    }

    float scaleX = 1.0;
    float scaleY = 1.0;
    float ratio = cellAspect / camAspect;

    if (fitMode == 0) {
        // Fill: escala para cubrir toda la celda, puede recortar
        if (ratio > 1.0) { scaleY = ratio; }
        else             { scaleX = 1.0 / ratio; }
    } else {
        // Fit: escala para que quepa todo, puede haber barras negras
        if (ratio > 1.0) { scaleX = 1.0 / ratio; }
        else             { scaleY = ratio; }
    }

    vec2 centered = cellUV - 0.5;
    centered.x /= scaleX;
    centered.y /= scaleY;
    return centered + 0.5;
}

// Uso:
// vec2 fittedUV = applyCamFit(localUV, 16.0/9.0, cellW/cellH, uCamfit);
// vec4 col = texture(sTD2DInputs[0], fittedUV);
// if (fittedUV.x < 0.0 || fittedUV.x > 1.0 || fittedUV.y < 0.0 || fittedUV.y > 1.0)
//     col = vec4(0.0); // negro fuera del área (solo en Fit mode)
```

---

## Uniforms Comunes — TODOS los layouts deben tenerlos

### Declaración en el shader
```glsl
uniform float uTime;       // absTime.seconds
uniform vec2  uResolution; // vec2(ResW, ResH)
uniform int   uCamCount;   // Camaras en multicam (2–5)
uniform int   uCamfit;     // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;  // aspecto de la cámara fuente (default 1.777 = 16/9)
// + uniforms propios del layout (Speed, Lag, etc.)
```

### Asignación en página Vectors del GLSL TOP

| Uniform | Tipo | Expression en TD |
|---------|------|-----------------|
| `uTime` | float | `absTime.seconds` |
| `uResolution` | vec2 | W: `op('escena_modular').par.ResW` / H: `op('escena_modular').par.ResH` |
| `uCamCount` | int | `op('escena_modular').par.Camerarasenmulticam` |
| `uCamfit` | int | `op('escena_modular').par.Camfit` |
| `uCamAspect` | float | `1.7778` (16/9 fijo, o conectar a un par si varía) |
| `uSpeed` | float | `parent().par.Speed` |
| `uLag` | float | `parent().par.Lag` |
| uniforms propios | — | `parent().par.NombreDelParam` |

---

## Template de Shader — Base para Todo Layout

```glsl
// layout_XX.glsl
// Descripción: [qué hace este layout]
// Inputs: CAM_1..5 en sTD2DInputs[0..4]

uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;
uniform float uCamAspect;
// [uniforms propios]

out vec4 fragColor;

// --- Función de fit (SIEMPRE incluir) ---
vec2 applyCamFit(vec2 cellUV, float camAspect, float cellAspect, int fitMode) {
    if (fitMode == 2) return cellUV;
    float scaleX = 1.0, scaleY = 1.0;
    float ratio = cellAspect / camAspect;
    if (fitMode == 0) {
        if (ratio > 1.0) scaleY = ratio;
        else scaleX = 1.0 / ratio;
    } else {
        if (ratio > 1.0) scaleX = 1.0 / ratio;
        else scaleY = ratio;
    }
    vec2 c = cellUV - 0.5;
    c.x /= scaleX;
    c.y /= scaleY;
    return c + 0.5;
}

// --- Helper: sample cámara por índice con fit aplicado ---
vec4 sampleCam(int idx, vec2 localUV, float cellW, float cellH) {
    float cellAspect = cellW / cellH;
    vec2 fitUV = applyCamFit(localUV, uCamAspect, cellAspect, uCamfit);
    // fuera del área → negro (solo visible en Fit mode)
    if (fitUV.x < 0.0 || fitUV.x > 1.0 || fitUV.y < 0.0 || fitUV.y > 1.0)
        return vec4(0.0);
    if (idx == 0) return texture(sTD2DInputs[0], fitUV);
    if (idx == 1) return texture(sTD2DInputs[1], fitUV);
    if (idx == 2) return texture(sTD2DInputs[2], fitUV);
    if (idx == 3) return texture(sTD2DInputs[3], fitUV);
    if (idx == 4) return texture(sTD2DInputs[4], fitUV);
    return vec4(0.0);
}

void main() {
    vec2 uv = vUV.st;
    // [lógica del layout usando sampleCam()]
    fragColor = vec4(0.0);
}
```

---

## Estructura Interna de Cada Layout (GLSL)

```
layout_XX (Base COMP, dentro de base17)
│
├── glsl_layout (GLSL TOP)
│     ├── inputs[0..4]: Select TOPs → CAM_1..5
│     ├── Resolution W: op('escena_modular').par.ResW
│     ├── Resolution H: op('escena_modular').par.ResH
│     ├── DAT: layout_XX.glsl
│     └── Vectors page: todos los uniforms asignados
│
└── out1 (Out TOP) → Switch interno de base17
```

### Select TOPs de input (dentro del layout, antes del GLSL TOP)
```
select_cam1 → TOP path: op('escena_modular').op('CAM_1')  (o parent(2).op('CAM_1'))
select_cam2 → TOP path: op('escena_modular').op('CAM_2')
select_cam3 → TOP path: op('escena_modular').op('CAM_3')
select_cam4 → TOP path: op('escena_modular').op('CAM_4')
select_cam5 → TOP path: op('escena_modular').op('CAM_5')
```
> Conectar en orden como inputs 0..4 del GLSL TOP.

---

## Catálogo de Layouts — base17

### Layouts existentes (NO tocar)
| # | Nombre | Descripción |
|---|--------|-------------|
| L1 | `layout_nodo` | Estático puro |
| L2 | `layout_hero` | Hero grande + secundarias |
| L3 | `layout_grid_dinamico` | Grid con movimiento smooth y lag |

### Layouts activos

---

#### L4 — `layout_gridwall_drift`
**Concepto:** Grid que cubre toda la pantalla con celdas de tamaño desproporcionado (unas más grandes que otras). El grid se desplaza continuamente en X o Y en loop. Hay variación intencional de tamaño entre celdas.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.05 | Velocidad del drift |
| `uDirection` | 0 | 0=horizontal, 1=vertical |
| `uSizeVariance` | 0.35 | Variación de tamaño entre celdas (0=igual, 1=muy distinto) |

**Lógica:** offset de UV que avanza con `uTime * uSpeed`, hace `mod()` para el loop. Anchos de celda distintos calculados con `uSizeVariance`.

---

#### L5 — `layout_pip`
**Concepto:** Hero ocupa ~75% de la pantalla. Las demás cámaras flotan como PIPs en las esquinas.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uPipSize` | 0.22 | Tamaño relativo de los PIPs |
| `uPipPadding` | 0.02 | Margen desde los bordes |
| `uHeroIndex` | 0 | Qué cámara es la hero (conectar a `op('escena_modular').par.Index`) |

---

#### L6 — `layout_split_asimetrico`
**Concepto:** División asimétrica. Hay jerarquía de tamaño entre cámaras.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSplitRatio` | 0.6 | Ratio de la cam principal (0.5–0.8) |
| `uOrientation` | 0 | 0=vertical, 1=horizontal |

---

#### L7 — `layout_orbit_dance`
**Concepto:** Las cámaras orbitan alrededor del centro en trayectorias circulares/elípticas con velocidades distintas.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.2 | Velocidad orbital base |
| `uOrbitRadius` | 0.3 | Radio de la órbita (fracción de resolución) |
| `uCamSize` | 0.4 | Tamaño de cada cam |

---

#### L8 — `layout_breathing_grid`
**Concepto:** Grid cuyas celdas pulsan en escala con desfase de fase por índice. Efecto de respiración hipnótica.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.3 | Velocidad de la pulsación |
| `uBreathAmt` | 0.12 | Amplitud del pulso (fracción del tamaño) |
| `uPhaseOffset` | 1.0 | Desfase de fase entre celdas |

---

#### L9 — `layout_float_chaos`
**Concepto:** Cada cámara tiene su propia trayectoria sinusoidal independiente en X e Y. Se superponen. Nunca para. Hipnótico y orgánico.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.2 | Velocidad base |
| `uSpread` | 0.5 | Qué tanto se alejan del centro |
| `uCamSize` | 0.45 | Tamaño de cada cam |

**Posiciones (en el shader, por índice i):**
```glsl
// cam i:
float px = sin(uTime * uSpeed * freqs[i] + phases_x[i]) * uResolution.x * uSpread * 0.5;
float py = cos(uTime * uSpeed * freqs[i+5] + phases_y[i]) * uResolution.y * uSpread * 0.5;
// freqs[] y phases[] son arrays de constantes distintas por cam, definidas en el shader
```

---

#### L10 — `layout_wave_scroll`
**Concepto:** Cámaras en fila con scroll continuo + ola sinusoidal en Y. Como una serpiente de cámaras que ondula y avanza.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.15 | Velocidad del scroll |
| `uWaveAmt` | 0.15 | Amplitud de la ola (fracción de ResH) |
| `uWaveFreq` | 1.0 | Frecuencia de la ola |
| `uCamSize` | 0.35 | Tamaño relativo de cada cam |

---

#### L11 — `layout_magnetic_pull`
**Concepto:** Un punto de atracción se mueve en figura de Lissajous. Las cámaras cercanas son atraídas hacia él, las lejanas se alejan. Muy orgánico.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.15 | Velocidad del punto de atracción |
| `uPullStrength` | 0.4 | Fuerza de atracción |
| `uPullRadius` | 0.5 | Radio de influencia |
| `uCamSize` | 0.4 | Tamaño de cada cam |

---

#### L12 — `layout_pendulum`
**Concepto:** Cámaras que se balancean como péndulos desde el tope de la pantalla. Cada una con frecuencia distinta.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.25 | Velocidad base del balanceo |
| `uAmplitude` | 0.3 | Amplitud del swing |
| `uCamSize` | 0.4 | Tamaño de cada cam |

**Posición X cam i:**
```glsl
float x = sin(uTime * uSpeed * (1.0 + float(i) * 0.15) + float(i) * 1.257) 
          * uResolution.x * uAmplitude;
```

---

#### L13 — `layout_swarm`
**Concepto:** Las cámaras forman un enjambre orbital. El centro del enjambre traza una Lissajous lenta. Cada cam orbita el centro con radio y velocidad distintos.

**Uniforms propios:**
| Uniform | Default | Descripción |
|---------|---------|-------------|
| `uSpeed` | 0.2 | Velocidad orbital |
| `uSwarmRadius` | 0.25 | Radio del enjambre |
| `uCenterSpeed` | 0.08 | Velocidad del centro |
| `uCamSize` | 0.38 | Tamaño de cada cam |

**Posición cam i:**
```glsl
float cx = sin(uTime * uCenterSpeed * 1.3) * uResolution.x * 0.3;
float cy = cos(uTime * uCenterSpeed * 1.0) * uResolution.y * 0.3;
float x = cx + cos(uTime * uSpeed * (1.0 + float(i)*0.2) + float(i)*1.257) 
              * uResolution.x * uSwarmRadius;
float y = cy + sin(uTime * uSpeed * (1.0 + float(i)*0.15) + float(i)*0.9)  
              * uResolution.y * uSwarmRadius;
```

---

## Pasos: Crear Layout Nuevo

1. Crear `layout_XX` (Base COMP) dentro de `base17`
2. Agregar Custom Parameters al Base COMP: `Speed`, `Lag`, y los específicos del layout
3. Dentro, crear `select_cam1..5` (Select TOPs) → `op('escena_modular').op('CAM_X')`
4. Crear `glsl_layout` (GLSL TOP):
   - Conectar los 5 Select TOPs como inputs en orden
   - Resolution W/H: `op('escena_modular').par.ResW` / `ResH`
   - DAT: archivo `.glsl` externo con el shader
   - Vectors: asignar TODOS los uniforms de la tabla
5. Crear `out1` (Out TOP)
6. Conectar al Switch interno de `base17`
7. Agregar al Menu `Modelayout` de `escena_modular`

---

## Template Base de Efecto (base18–45)

```
baseXX (Base COMP)
├── in1 (In TOP) ← output de base17
├── glsl_fx (GLSL TOP)
│     ├── Res W/H desde escena_modular
│     └── Vectors: uniforms asignados
└── out1 (Out TOP) → switch_FINAL
```

```glsl
// baseXX_fx.glsl
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec4 col = texture(sTD2DInputs[0], uv);
    // [efecto]
    fragColor = col;
}
```

---

## Performance Live

- Layouts inactivos: **Cook: Off**
- GLSL activo: **Cook: Always**
- Movimiento: funciones sinusoidales en el shader — nunca saltos
- `uCamfit = 0` (Fill) por default — el usuario lo cambia desde `escena_modular`

---

*Little Jesus — Live VJ System | TD 2023 + GLSL + Claude Code*
*Path: /project2/escena_modular/base17*

---

## Control en vivo — Stream Deck + MIDImix (`control/`)

| Archivo | Qué hace |
|---|---|
| `escenas_td_streamdeck.companionconfig` | Config de Companion 5.1.1 (Stream Deck MK.2): páginas ESCENAS, RAND 1, RAND 2, CAMARAS, FX 1, FX 2. Importar en Companion → Import/Export |
| `gen_companion.py` | Regenera el `.companionconfig` a partir de `companion_base_export.companionconfig` |
| `fix_blend_switch.py` | Alinea `master_switch` y `blend_switch` con el orden del menú `Modoescena` (correr sin `APPLY` para revisar) |
| `oscin1_callbacks.py` | Contenido del callback del OSC In DAT `oscin1` (router de Companion) |
| `setup_companion_feedback.py` | TD → Companion (OSC 127.0.0.1:12320): manda `Int`, `Modoescena`, `Menu2` e `Index` a las custom variables `cams`, `escena`, `cam`, `hero` |
| `setup_scene_faders.py` | Faders 4–8 + MASTER del MIDImix (CC 32, 50, 54, 58, 62, 63) mueven los params Float de la escena activa, con takeover |

- Companion manda OSC a `127.0.0.1:7010` (el 7000 lo usa Resolume Arena) → OSC In DAT `oscin1` en `escena_modular`. Rutas: `/td/<Par> valor`, `/td/inc/<Par> delta` y `/td/fx indice` (→ `/project2/switch23`).
- Los botones mandan el **label** de la escena (`Floating Pieces`), no el índice: reordenar el menú no rompe el Stream Deck, pero **sí** hay que volver a correr `fix_blend_switch.py`.
- MIDImix en canal 1. Patrón de CC por columna: 3 knobs consecutivos y luego el fader.

### Nombres de los FX (`switch23`, en `gen_companion.py` → `FX_NAMES`)

| Entrada | Base | FX |
|---|---|---|
| 0 | base17 | Sin FX (cámara limpia) |
| 1 | base18 | Time Machine 4 Glitch |
| 2 | base19 | Slitscan |
| 3 | base20 | Feedback RGB Delay |
| 4 | base21 | Optical Flow |
| 5 | base22 | Liquid Feedback |
| 6 | base23 | Pixel Sort |
| 7 | base24 | ASCII |
| 8–15 | base38–45 | (sin nombre todavía) |

### Mapa de salidas de `/project2` (pads del Beatstep)

```
VISUALES    pads 1–16          → switch1 / switch3 → switch2  → fit1
CÁMARAS+FX  pads 17–24, 41–48  → switch23 → fit2               (entrada 0 = base17 limpio; switch4 ya no se usa)
switch5     pads 25–32,35,38,39 → switch5 → null42             (13 opciones, por identificar)
```

Cada pad = `logicN` → `chopexecN` (`onOffToOn` cambia índices). Pendientes de arreglo:
- ~~Pads 19–24 ponían `switch2=2`~~ → arreglado en fase 1 (2026-11-01).
- `switch6`–`21` (vidN vs nullN) tienen índices 1–16 con solo 2 entradas → siempre generativo.
- ~~`black` ponía `switch2=4`~~ → ahora va a `black_out` (entrada 2 de `switch2`), fase 1.
- Pad 40 duplica al 9. Pads 33, 34, 36, 37 vacíos (pendiente: definir qué hacen).
- `switch6`–`21` tienen el index por expresión (1–16) con solo 2 entradas → siempre generativo; revisar con los videos `vid`.

### Roadmap de limpieza (acordado 2026-11-01)
1. **Fase 1 — arreglos seguros** (`control/fase1_arreglos.py`): pads 19–24 sin `switch2=2`, pad `black` → `black_out`, `switch6`–`21` en rango.
2. **Fase 2 — contrato de 5** en todas las bases (visuales y FX): 5 sliders por rol + Bypass + pestaña Audio → todo audioreactivo.
3. **Fase 3 — MIDI estándar (MIDImix)**: fila de arriba knobs 1–5 = visual activo, fila de abajo knobs 1–5 = FX activo (siguen a lo activo, con takeover). Sección fija de **corrección de color** (brillo, contraste, saturación, hue, temperatura) sobre la salida, use o no cámaras.
4. **Fase 4 — limpiar `/project1`**: un solo MIDI In; decidir qué FX de ahí se quedan.
5. **Fase 5 — boilerplate**: `.toe` plantilla + `proyecto.json` + scripts de armado.
- Futuro: Stream Deck XL y Stream Deck + (knobs y pantalla táctil) — el generador de Companion se extiende a esos modelos.
