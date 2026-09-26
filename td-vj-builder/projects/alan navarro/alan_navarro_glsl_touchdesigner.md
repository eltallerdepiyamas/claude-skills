# TouchDesigner: 8 Filtros GLSL — Alan Navarro / CD9 VJ Set

## Contexto del proyecto

Crear 8 filtros GLSL para uso en vivo como VJ en un show de Alan Navarro (ex-CD9). Cada filtro debe vivir dentro de su propio **Base COMP** en TouchDesigner, con todos los parámetros expuestos como **Custom Parameters** en el Base, para control en vivo vía MIDI o interfaz.

---

## Instrucciones para Claude Code

Genera un script Python completo (`.py`) que se ejecute en la **TextPort de TouchDesigner** (Alt+T) y construya automáticamente toda la estructura de red.

### Requisitos de arquitectura

- **TouchDesigner versión:** 2023.11 o superior
- **Lenguaje del script:** Python 3 (ejecutable desde TextPort de TD)
- **Estructura raíz:** Todo dentro de `/project1/`

---

## Estructura general a crear

```
/project1/
└── ALAN_NAVARRO_VJ/          ← Base COMP contenedor principal
    ├── AUDIO_ANALYSIS/        ← Base COMP con análisis de audio
    ├── PALETTE_SYSTEM/        ← Base COMP con sistema de paletas
    ├── FILTER_01_CRT_VHS/     ← Base COMP filtro 1
    ├── FILTER_02_NEON_GRID/   ← Base COMP filtro 2
    ├── FILTER_03_LIQUID/      ← Base COMP filtro 3
    ├── FILTER_04_STARFIELD/   ← Base COMP filtro 4
    ├── FILTER_05_CINEMATIC/   ← Base COMP filtro 5
    ├── FILTER_06_SPLATTER/    ← Base COMP filtro 6
    ├── FILTER_07_BOKEH/       ← Base COMP filtro 7
    ├── FILTER_08_CHROME/      ← Base COMP filtro 8
    └── MIX_OUTPUT/            ← Base COMP mezclador final
```

---

## Módulo AUDIO_ANALYSIS

El usuario conecta manualmente su propio `select` CHOP con el canal de audio ya procesado. El módulo AUDIO_ANALYSIS solo recibe ese canal, lo acondiciona y lo distribuye.

Crear dentro de `AUDIO_ANALYSIS`:
- 1x `in` CHOP llamado `AUDIO_IN` → **punto de entrada manual** donde el usuario conecta su `select` CHOP externo (canal único de bajo/bass ya procesado, normalizado 0-1)
- 1x `math` CHOP → multiplicar por `Gain` (escalado en vivo)
- 1x `lag` CHOP → suavizado de ataque/caída (`Attack` y `Release`)
- 1x `null` CHOP llamado `AUDIO_OUT` con canal renombrado: `bass`

**Flujo esperado del usuario:**
```
[Tu select CHOP externo] ──→ [AUDIO_IN] ──→ math (gain) ──→ lag (smooth) ──→ AUDIO_OUT
```

**Custom Parameters en Base AUDIO_ANALYSIS:**
- `Gain` (Float, 0-4, default 1.0) → amplifica la señal entrante
- `Attack` (Float, 0-1, default 0.01) → qué tan rápido sube la reactividad
- `Release` (Float, 0-1, default 0.15) → qué tan rápido cae (más alto = más suave)
- `Threshold` (Float, 0-1, default 0.0) → corta señal por debajo de este valor (elimina ruido de piso)

---

## Módulo PALETTE_SYSTEM

Crear 3 paletas como `constant` CHOPs con los valores:

| Paleta | Nombre | Color 1 | Color 2 | Color 3 |
|--------|--------|---------|---------|---------|
| 0 | `NEON_URBAN` | #FF1B8D (magenta) | #00E5FF (cyan) | #0A0A0A (negro) |
| 1 | `COASTAL_WARM` | #FF9A5A (ámbar) | #1F4E5F (teal) | #FFF8F0 (blanco cálido) |
| 2 | `ASTRAL_DEEP` | #8B00FF (púrpura) | #FFFFFF (blanco) | #000014 (negro azul) |

- 1x `switch` CHOP para seleccionar paleta activa
- 1x `null` CHOP llamado `PALETTE_OUT`

**Custom Parameters en Base PALETTE_SYSTEM:**
- `ActivePalette` (Menu: NEON_URBAN / COASTAL_WARM / ASTRAL_DEEP, default 0)
- `BlendAmount` (Float, 0-1, default 0.0) → para interpolar entre paletas
- `Saturation` (Float, 0-2, default 1.0)
- `Brightness` (Float, 0-2, default 1.0)

---

## Especificación de cada filtro (Base COMP)

Cada Base COMP debe contener:
- 1x `glsl` TOP (el shader principal)
- 1x `in` TOP llamado `INPUT` (imagen/video de entrada)
- 1x `out` TOP llamado `OUTPUT`
- 1x `constant` CHOP para parámetros que se alimentan al GLSL
- Conexiones de `AUDIO_OUT` y `PALETTE_OUT` como inputs del GLSL

### Convención de uniforms globales (aplicar en TODOS los shaders):

```glsl
// Uniforms globales — disponibles en todos los shaders
uniform float u_bass;       // canal de audio único, bajo/bass 0-1 (viene de select CHOP del usuario)
uniform float u_time;       // tiempo en segundos
uniform vec2  u_res;        // resolución en píxeles
uniform vec3  u_color1;     // color 1 de paleta activa
uniform vec3  u_color2;     // color 2 de paleta activa
uniform vec3  u_color3;     // color 3 de paleta activa
uniform sampler2D u_input;  // textura de entrada
```

> **Nota para Claude Code:** `u_bass` es el único driver de audio. Eliminar toda referencia a `u_kick`, `u_mid`, `u_high`, `u_bpm` en todos los shaders. Reemplazar cualquier aparición de esas variables por `u_bass`.

> **Conexión en TouchDesigner:** El GLSL TOP de cada filtro recibe el `AUDIO_OUT` CHOP como **CHOP input**. En el DAT de uniforms del GLSL TOP declarar: `bass` → canal 0 del CHOP input.

---

## FILTER_01: CRT_SYNC_VHS

**Descripción:** Scanlines densas, estática CRT, rolling bar, aberración cromática RGB. Evoca la entrada de sintonización de televisor de los shows de CD9.

**Código GLSL fragment shader:**

```glsl
uniform float u_scanline_density;   // 100-2000, default 800
uniform float u_noise_amount;       // 0-1, default 0.3
uniform float u_chroma_shift;       // 0-0.05, default 0.008
uniform float u_rolling_speed;      // 0-2, default 0.4
uniform float u_vignette;           // 0-1, default 0.5
uniform float u_static_amount;      // 0-1, default 0.2
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec2 uv = vUV.st;
    
    // Aberración cromática reactiva al bass
    float shift = u_chroma_shift + u_bass * 0.02;
    vec4 colorR = texture(u_input, uv + vec2(shift, 0.0));
    vec4 colorG = texture(u_input, uv);
    vec4 colorB = texture(u_input, uv - vec2(shift, 0.0));
    vec4 color = vec4(colorR.r, colorG.g, colorB.b, 1.0);
    
    // Scanlines
    float scanline = sin(uv.y * u_scanline_density) * 0.5 + 0.5;
    scanline = pow(scanline, 0.3);
    color.rgb *= mix(1.0, scanline, 0.4);
    
    // Rolling bar — velocidad patea con el bass
    float bar = fract(uv.y - u_time * u_rolling_speed * (1.0 + u_bass));
    float barMask = smoothstep(0.97, 1.0, bar) * 0.3;
    color.rgb += barMask;
    
    // Estática noise reactiva al bass
    float noise = rand(uv + vec2(u_time * 0.1)) * u_noise_amount;
    noise *= (1.0 + u_bass * 2.0);
    color.rgb += noise * 0.15;
    
    // Static blocks — explotan en golpes de bass
    float staticBlock = step(0.98 - u_static_amount * 0.1, rand(vec2(floor(uv.y * 30.0), floor(u_time * 10.0))));
    color.rgb = mix(color.rgb, vec3(rand(uv + u_time)), staticBlock * u_bass);
    
    // Viñeta
    vec2 vigUV = uv * 2.0 - 1.0;
    float vig = 1.0 - dot(vigUV, vigUV) * u_vignette;
    color.rgb *= clamp(vig, 0.0, 1.0);
    
    fragColor = color;
}
```

**Custom Parameters en Base FILTER_01:**
- `ScanlineDensity` (Float, 100-2000, default 800)
- `NoiseAmount` (Float, 0-1, default 0.3)
- `ChromaShift` (Float, 0-0.05, default 0.008)
- `RollingSpeed` (Float, 0-2, default 0.4)
- `Vignette` (Float, 0-1, default 0.5)
- `StaticAmount` (Float, 0-1, default 0.2)
- `MixAmount` (Float, 0-1, default 1.0) → blend con input original

---

## FILTER_02: NEON_GRID_URBAN

**Descripción:** Grid infinito en perspectiva synthwave, neón magenta/cyan, horizon line, glow bloom. Era .5 / 3/4 / 1.0 de CD9.

**Código GLSL fragment shader:**

```glsl
uniform float u_grid_scale;     // 1-20, default 8
uniform float u_speed;          // 0-5, default 1.5
uniform float u_glow_radius;    // 0.001-0.05, default 0.01
uniform float u_horizon;        // 0-1, default 0.5
uniform float u_fog_density;    // 0-3, default 1.5
uniform float u_sun_size;       // 0-0.3, default 0.08
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_res.x / u_res.y;
    
    vec3 col = u_color3; // fondo negro
    
    // Perspectiva del grid — velocidad y escala reactivas al bass
    if (uv.y < u_horizon) {
        vec2 gridUV;
        float depth = u_horizon - uv.y;
        gridUV.x = p.x / (depth + 0.001) * 0.5;
        gridUV.y = u_time * u_speed * (1.0 + u_bass * 2.0) / (depth + 0.001);
        
        vec2 grid = abs(fract(gridUV * u_grid_scale) - 0.5);
        float gridLine = min(grid.x, grid.y);
        float glowLine = smoothstep(u_glow_radius * 2.0, 0.0, gridLine);
        
        // Fog por profundidad
        float fog = exp(-depth * u_fog_density);
        
        // Color neón — saturación reactiva al bass
        vec3 neonColor = mix(u_color1, u_color2, sin(gridUV.x * 3.14) * 0.5 + 0.5);
        neonColor *= 1.0 + u_bass * 1.5;
        
        col = mix(col, neonColor, glowLine * fog);
        
        // Bloom extra en golpe de bass
        col += neonColor * glowLine * u_bass * 0.5;
    }
    
    // Sol / horizon
    float sunDist = length(vec2(uv.x - 0.5, uv.y - u_horizon));
    float sun = smoothstep(u_sun_size, u_sun_size * 0.5, sunDist);
    float sunLines = step(0.6, sin(uv.y * 120.0 - u_horizon * 120.0));
    sun *= mix(1.0, sunLines, step(uv.y, u_horizon + u_sun_size));
    
    vec3 sunColor = mix(u_color1, vec3(1.0, 0.8, 0.2), 0.4);
    col = mix(col, sunColor, sun);
    
    // Glow horizon line — pulsa con el bass
    float horizonGlow = smoothstep(0.05, 0.0, abs(uv.y - u_horizon));
    col += mix(u_color1, u_color2, uv.x) * horizonGlow * (0.5 + u_bass);
    
    fragColor = vec4(col, 1.0);
}
```

**Custom Parameters en Base FILTER_02:**
- `GridScale` (Float, 1-20, default 8)
- `Speed` (Float, 0-5, default 1.5)
- `GlowRadius` (Float, 0.001-0.05, default 0.01)
- `HorizonPosition` (Float, 0-1, default 0.5)
- `FogDensity` (Float, 0-3, default 1.5)
- `SunSize` (Float, 0-0.3, default 0.08)
- `MixAmount` (Float, 0-1, default 1.0)

---

## FILTER_03: LIQUID_SHOWER

**Descripción:** Distorsión por noise multi-octava tipo agua/regadera con refracción cromática. *Me Ahogo* — Alan Navarro solista.

**Código GLSL fragment shader:**

```glsl
uniform float u_distortion;     // 0-0.2, default 0.05
uniform float u_flow_speed;     // 0-3, default 0.8
uniform float u_drop_density;   // 1-20, default 8
uniform float u_caustics;       // 0-1, default 0.4
uniform float u_tint_strength;  // 0-1, default 0.5
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

vec2 hash2(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(dot(hash2(i), f),
                   dot(hash2(i + vec2(1,0)), f - vec2(1,0)), u.x),
               mix(dot(hash2(i + vec2(0,1)), f - vec2(0,1)),
                   dot(hash2(i + vec2(1,1)), f - vec2(1,1)), u.x), u.y);
}

void main() {
    vec2 uv = vUV.st;
    float t = u_time * u_flow_speed * (1.0 + u_bass * 0.5);
    
    // Distorsión tipo flujo de agua — amplitud reactiva al bass
    float n1 = noise(uv * u_drop_density + vec2(0.0, t));
    float n2 = noise(uv * u_drop_density * 1.7 + vec2(t * 0.3, 0.0));
    float n3 = noise(uv * u_drop_density * 0.5 + vec2(-t * 0.2, t * 0.1));
    float flow = (n1 + n2 * 0.5 + n3 * 0.25) / 1.75;
    
    vec2 distort = vec2(
        noise(uv * 6.0 + vec2(t, 0.0)),
        noise(uv * 6.0 + vec2(0.0, t))
    ) * u_distortion * (1.0 + u_bass * 0.5);
    
    // Aberración cromática del agua
    vec4 colR = texture(u_input, uv + distort * 1.2);
    vec4 colG = texture(u_input, uv + distort);
    vec4 colB = texture(u_input, uv + distort * 0.8);
    vec4 color = vec4(colR.r, colG.g, colB.b, 1.0);
    
    // Caustics — intensidad reactiva al bass
    float caustic = abs(sin(uv.x * 10.0 + flow * 6.28 + t) + cos(uv.y * 10.0 + flow * 6.28 - t));
    caustic = pow(caustic, 3.0) * u_caustics * (0.5 + u_bass);
    
    // Tinte teal/verde del agua
    vec3 waterTint = mix(vec3(1.0), u_color2, u_tint_strength);
    color.rgb *= waterTint;
    color.rgb += u_color2 * caustic * 0.3;
    
    // Gotas: SDF circular sobre grid
    vec2 dropUV = fract(uv * u_drop_density) - 0.5;
    float drop = smoothstep(0.15, 0.1, length(dropUV) - 0.05 * sin(t * 3.0));
    color.rgb += u_color2 * drop * 0.1;
    
    fragColor = color;
}
```

**Custom Parameters en Base FILTER_03:**
- `Distortion` (Float, 0-0.2, default 0.05)
- `FlowSpeed` (Float, 0-3, default 0.8)
- `DropDensity` (Float, 1-20, default 8)
- `Caustics` (Float, 0-1, default 0.4)
- `TintStrength` (Float, 0-1, default 0.5)
- `MixAmount` (Float, 0-1, default 1.0)

---

## FILTER_04: STARFIELD_RESILIENCE

**Descripción:** Campo estelar procedural, twinkle individual, nebulosa púrpura, reactivo a voz/high. *Las Estrellas No Brillan* + mar de celulares del Last Party Tour.

**Código GLSL fragment shader:**

```glsl
uniform float u_star_density;   // 50-500, default 200
uniform float u_twinkle_speed;  // 0-5, default 1.5
uniform float u_star_size;      // 0.001-0.01, default 0.003
uniform float u_nebula_density; // 0-2, default 0.8
uniform float u_threshold;      // 0-1, default 0.7
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float hash1(float n) { return fract(sin(n) * 43758.5453); }

float star(vec2 uv, vec2 center, float size) {
    return smoothstep(size, 0.0, length(uv - center));
}

void main() {
    vec2 uv = vUV.st;
    vec2 p = uv * 2.0 - 1.0;
    
    // Fondo: mezcla input con espacio
    vec4 inputCol = texture(u_input, uv);
    vec3 space = mix(u_color3, u_color1 * 0.1, length(p) * 0.3);
    vec3 col = mix(inputCol.rgb, space, 0.7);
    
    // Nebulosa
    float neb = 0.0;
    for(int i = 0; i < 3; i++) {
        vec2 offset = vec2(hash1(float(i) * 13.7), hash1(float(i) * 7.3)) * 2.0 - 1.0;
        neb += exp(-length(p - offset * 0.5) * u_nebula_density) * 0.3;
    }
    col += u_color1 * neb * 0.4;
    
    // Campo estelar — estrellas emergen y se intensifican con el bass
    float stars = 0.0;
    int density = int(u_star_density);
    for(int i = 0; i < 200; i++) {
        if(i >= density) break;
        vec2 starPos = vec2(hash1(float(i) * 1.3), hash1(float(i) * 2.7));
        float twinkle = sin(u_time * u_twinkle_speed * hash1(float(i)) + float(i)) * 0.5 + 0.5;
        
        // Bass impulsa el brillo de cada estrella
        float brightness = mix(0.3, 1.0, twinkle) * (1.0 + u_bass * hash1(float(i) * 5.1));
        float size = u_star_size * (0.5 + hash1(float(i) * 3.3) * 0.5);
        
        // Threshold: el bass hace aparecer estrellas nuevas
        if(twinkle > u_threshold - u_bass * 0.3) {
            stars += star(uv, starPos, size) * brightness;
        }
    }
    
    col += vec3(stars);
    col += u_color2 * stars * 0.3;
    
    // Flash de destello en golpe de bass
    float flash = u_bass * 0.1 * exp(-length(p) * 2.0);
    col += u_color2 * flash;
    
    fragColor = vec4(col, 1.0);
}
```

**Custom Parameters en Base FILTER_04:**
- `StarDensity` (Int, 50-200, default 120)
- `TwinkleSpeed` (Float, 0-5, default 1.5)
- `StarSize` (Float, 0.001-0.01, default 0.003)
- `NebulaDensity` (Float, 0-2, default 0.8)
- `Threshold` (Float, 0-1, default 0.7)
- `MixAmount` (Float, 0-1, default 1.0)

---

## FILTER_05: TEAL_ORANGE_CINEMATIC

**Descripción:** LUT procedural teal/naranja, grano analógico Kodak Portra, anamorphic lens flare, light leaks, viñeta. Firma solista de Alan.

**Código GLSL fragment shader:**

```glsl
uniform float u_teal_strength;      // 0-1, default 0.5
uniform float u_orange_strength;    // 0-1, default 0.5
uniform float u_grain_amount;       // 0-1, default 0.25
uniform float u_flare_intensity;    // 0-2, default 0.5
uniform float u_leak_opacity;       // 0-1, default 0.2
uniform float u_vignette_strength;  // 0-1, default 0.4
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

float rand(vec2 co) { return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453); }

void main() {
    vec2 uv = vUV.st;
    vec4 color = texture(u_input, uv);
    
    // LUT teal-orange cinematográfico
    float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    
    // Sombras → teal
    vec3 tealShift = mix(color.rgb, u_color2, u_teal_strength * (1.0 - luma) * 0.7);
    // Luces → naranja/ámbar
    vec3 warmShift = mix(tealShift, u_color1, u_orange_strength * luma * 0.5);
    color.rgb = warmShift;
    
    // Lift de sombras (estilo Kodak)
    color.rgb = color.rgb * 0.9 + 0.05;
    
    // Grano analógico multiplicativo sobre luminancia
    float grain = rand(uv + fract(u_time * 0.1)) * 2.0 - 1.0;
    color.rgb += grain * u_grain_amount * 0.08 * (1.0 + luma);
    
    // Anamorphic lens flare horizontal
    float flarePosY = 0.5 + sin(u_time * 0.3) * 0.1;
    float flareStreak = exp(-abs(uv.y - flarePosY) * 80.0);
    float flareMask = smoothstep(0.3, 0.7, uv.x) * smoothstep(1.0, 0.7, uv.x);
    vec3 flareColor = mix(u_color1, vec3(1.0, 0.95, 0.8), 0.5);
    color.rgb += flareColor * flareStreak * flareMask * u_flare_intensity * (0.3 + u_bass * 0.5);
    
    // Light leaks desde bordes
    float leakLeft = exp(-uv.x * 8.0) * u_leak_opacity;
    float leakTop = exp(-(1.0 - uv.y) * 10.0) * u_leak_opacity * 0.5;
    color.rgb += u_color1 * leakLeft;
    color.rgb += mix(u_color1, u_color2, 0.5) * leakTop;
    
    // Viñeta
    vec2 vigUV = uv * 2.0 - 1.0;
    float vignette = 1.0 - dot(vigUV, vigUV) * u_vignette_strength;
    color.rgb *= clamp(vignette, 0.0, 1.0);
    
    fragColor = vec4(clamp(color.rgb, 0.0, 1.0), 1.0);
}
```

**Custom Parameters en Base FILTER_05:**
- `TealStrength` (Float, 0-1, default 0.5)
- `OrangeStrength` (Float, 0-1, default 0.5)
- `GrainAmount` (Float, 0-1, default 0.25)
- `FlareIntensity` (Float, 0-2, default 0.5)
- `LeakOpacity` (Float, 0-1, default 0.2)
- `VignetteStrength` (Float, 0-1, default 0.4)
- `MixAmount` (Float, 0-1, default 1.0)

---

## FILTER_06: SPLATTER_REVOLUTION

**Descripción:** Manchas de pintura procedurales tipo metaballs en paleta candy pop sobre fondo blanco. Era *Revolution* de CD9.

**Código GLSL fragment shader:**

```glsl
uniform float u_num_blobs;      // 3-12, default 6
uniform float u_blob_size;      // 0.05-0.4, default 0.15
uniform float u_threshold;      // 0.3-0.9, default 0.5
uniform float u_softness;       // 0.01-0.2, default 0.05
uniform float u_background;     // 0-1, default 1.0 (1=blanco)
uniform float u_splat_speed;    // 0-3, default 0.8
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

float hash1(float n) { return fract(sin(n) * 43758.5453); }

void main() {
    vec2 uv = vUV.st;
    vec4 inputCol = texture(u_input, uv);
    
    // Paleta candy pop fija
    vec3 colors[5];
    colors[0] = vec3(1.0, 0.1, 0.4);
    colors[1] = vec3(0.0, 0.9, 0.3);
    colors[2] = vec3(1.0, 0.9, 0.0);
    colors[3] = vec3(0.0, 0.6, 1.0);
    colors[4] = vec3(1.0, 0.4, 0.0);
    
    vec3 bg = mix(inputCol.rgb, vec3(u_background), u_background);
    vec3 col = bg;
    
    float metafield = 0.0;
    vec3 blendColor = vec3(0.0);
    float totalWeight = 0.0;
    
    int n = int(u_num_blobs);
    for(int i = 0; i < 12; i++) {
        if(i >= n) break;
        
        float fi = float(i);
        float speed = u_splat_speed * (0.5 + hash1(fi * 3.1) * 0.5);
        // Movimiento Lissajous — tamaño explota con el bass
        vec2 blobPos = vec2(
            0.5 + sin(u_time * speed * hash1(fi) + fi) * 0.35 * (1.0 + u_bass * 0.3),
            0.5 + cos(u_time * speed * hash1(fi * 2.3) + fi * 1.7) * 0.35 * (1.0 + u_bass * 0.3)
        );
        
        float blobSize = u_blob_size * (0.7 + hash1(fi * 4.1) * 0.6) * (1.0 + u_bass * 0.4);
        float d = length(uv - blobPos);
        float meta = blobSize / (d * d + 0.001);
        
        float angle = atan(uv.y - blobPos.y, uv.x - blobPos.x);
        float splat = 1.0 + sin(angle * 7.0 + u_time * 0.5) * 0.15 + sin(angle * 13.0) * 0.08;
        meta *= splat;
        
        metafield += meta;
        vec3 blobColor = colors[i % 5];
        blendColor += blobColor * meta;
        totalWeight += meta;
    }
    
    if(totalWeight > 0.0) blendColor /= totalWeight;
    
    float mask = smoothstep(u_threshold - u_softness, u_threshold + u_softness, metafield);
    col = mix(bg, blendColor, mask);
    
    float outline = smoothstep(u_threshold - u_softness * 3.0, u_threshold - u_softness, metafield);
    outline -= mask;
    col = mix(col, vec3(0.0), outline * 0.3);
    
    fragColor = vec4(col, 1.0);
}
```

**Custom Parameters en Base FILTER_06:**
- `NumBlobs` (Int, 3-12, default 6)
- `BlobSize` (Float, 0.05-0.4, default 0.15)
- `Threshold` (Float, 0.3-0.9, default 0.5)
- `Softness` (Float, 0.01-0.2, default 0.05)
- `Background` (Float, 0-1, default 1.0)
- `SplatSpeed` (Float, 0-3, default 0.8)
- `MixAmount` (Float, 0-1, default 1.0)

---

## FILTER_07: BOKEH_NIGHT_PARTY

**Descripción:** Partículas bokeh circulares ámbar/magenta, motion drift, lens flares cálidos. *Prohibido* + *Vuelves* + Love & Live Edition.

**Código GLSL fragment shader:**

```glsl
uniform float u_num_particles;  // 20-150, default 60
uniform float u_particle_size;  // 0.005-0.08, default 0.025
uniform float u_drift_speed;    // 0-2, default 0.3
uniform float u_depth_layers;   // 1-4, default 3
uniform float u_flare_count;    // 0-5, default 2
uniform float u_warmth;         // 0-1, default 0.7
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

float hash1(float n) { return fract(sin(n) * 43758.5453); }
float hash2x(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

float bokehDisk(vec2 uv, vec2 center, float size, float softness) {
    float d = length(uv - center);
    return smoothstep(size, size - softness, d) * smoothstep(0.0, size * 0.3, d) * 0.7
         + smoothstep(size * 0.3, 0.0, d);
}

void main() {
    vec2 uv = vUV.st;
    vec4 inputCol = texture(u_input, uv);
    vec3 col = inputCol.rgb * 0.4; // oscurecer input para que emerjan las partículas
    
    int np = int(u_num_particles);
    int layers = int(u_depth_layers);
    
    for(int layer = 0; layer < 4; layer++) {
        if(layer >= layers) break;
        float fl = float(layer);
        float layerScale = 0.4 + fl * 0.3; // partículas más grandes en frente
        
        for(int i = 0; i < 150; i++) {
            if(i >= np / layers) break;
            float fi = float(i) + fl * 37.0;
            
            // Posición con drift
            vec2 pos = vec2(hash1(fi), hash1(fi * 2.3));
            pos.y = fract(pos.y + u_time * u_drift_speed * hash1(fi * 0.1) * 0.1);
            pos.x = fract(pos.x + sin(u_time * 0.2 + fi) * 0.01);
            
            float size = u_particle_size * layerScale * (0.5 + hash1(fi * 3.3) * 0.5);
            size *= 1.0 + u_bass * 0.3;
            
            float brightness = 0.5 + hash1(fi * 5.1) * 0.5;
            brightness *= 1.0 + u_bass * 0.5;
            
            // Color ámbar/magenta según layer
            vec3 pColor = mix(u_color1, u_color2, hash1(fi * 7.3));
            pColor = mix(pColor, vec3(1.0, 0.9, 0.6), u_warmth * 0.5);
            
            float b = bokehDisk(uv, pos, size, size * 0.3) * brightness;
            col += pColor * b * 0.8;
        }
    }
    
    // Lens flares cálidos
    int nf = int(u_flare_count);
    for(int i = 0; i < 5; i++) {
        if(i >= nf) break;
        float fi = float(i);
        vec2 flarePos = vec2(0.3 + fi * 0.15, 0.3 + sin(u_time * 0.1 + fi) * 0.2);
        float flare = exp(-length(uv - flarePos) * 15.0) * 0.6;
        float streak = exp(-abs(uv.y - flarePos.y) * 40.0) * 0.2;
        col += u_color1 * (flare + streak) * (0.5 + u_bass * 0.5);
    }
    
    fragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
```

**Custom Parameters en Base FILTER_07:**
- `NumParticles` (Int, 20-150, default 60)
- `ParticleSize` (Float, 0.005-0.08, default 0.025)
- `DriftSpeed` (Float, 0-2, default 0.3)
- `DepthLayers` (Int, 1-4, default 3)
- `FlareCount` (Int, 0-5, default 2)
- `Warmth` (Float, 0-1, default 0.7)
- `MixAmount` (Float, 0-1, default 1.0)

---

## FILTER_08: CHROME_COUNTDOWN_LAST_PARTY

**Descripción:** Contador 9→0 con superficie chrome, fresnel, iridiscencia, bloom blanco/rojo. The Last Party Tour 2024-2025.

**Código GLSL fragment shader:**

```glsl
uniform float u_countdown;          // 0-9, default 9 (valor del número a mostrar)
uniform float u_chrome_roughness;   // 0-1, default 0.15
uniform float u_fresnel_power;      // 1-8, default 3.0
uniform float u_bloom_intensity;    // 0-3, default 1.5
uniform float u_iridescence;        // 0-1, default 0.4
uniform float u_cube_opacity;       // 0-1, default 0.3
// + uniforms globales (u_bass, u_time, u_res, u_color1/2/3, u_input)

out vec4 fragColor;

// SDF para dígito tipo 7-segment (simplificado)
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

float digit(vec2 uv, float n) {
    uv = uv * 2.0 - 1.0; // -1 a 1
    uv.y = -uv.y;
    
    float d = 1e10;
    float seg = 0.08; float len = 0.7;
    
    // Segmento A (top)
    if(n != 1.0 && n != 4.0)
        d = min(d, sdBox(uv - vec2(0.0, 0.8), vec2(len * 0.5, seg)));
    // Segmento G (middle)
    if(n != 0.0 && n != 1.0 && n != 7.0)
        d = min(d, sdBox(uv, vec2(len * 0.5, seg)));
    // Segmento D (bottom)
    if(n != 1.0 && n != 4.0 && n != 7.0)
        d = min(d, sdBox(uv - vec2(0.0, -0.8), vec2(len * 0.5, seg)));
    // Segmento F (top-left)
    if(n != 1.0 && n != 2.0 && n != 3.0 && n != 7.0)
        d = min(d, sdBox(uv - vec2(-0.42, 0.4), vec2(seg, 0.35)));
    // Segmento E (bottom-left)
    if(n == 0.0 || n == 2.0 || n == 6.0 || n == 8.0)
        d = min(d, sdBox(uv - vec2(-0.42, -0.4), vec2(seg, 0.35)));
    // Segmento B (top-right)
    if(n != 5.0 && n != 6.0)
        d = min(d, sdBox(uv - vec2(0.42, 0.4), vec2(seg, 0.35)));
    // Segmento C (bottom-right)
    if(n != 2.0)
        d = min(d, sdBox(uv - vec2(0.42, -0.4), vec2(seg, 0.35)));
    
    return d;
}

void main() {
    vec2 uv = vUV.st;
    vec2 p = uv * 2.0 - 1.0;
    
    vec4 inputCol = texture(u_input, uv);
    vec3 col = inputCol.rgb * 0.3 + u_color3 * 0.7;
    
    // Dígito centrado
    vec2 digitUV = (uv - vec2(0.25, 0.1)) / vec2(0.5, 0.8);
    float n = floor(u_countdown);
    float d = digit(clamp(digitUV, 0.0, 1.0), n);
    
    // Chrome material
    float fresnel = pow(1.0 - abs(dot(normalize(p), vec2(0.0, 1.0))), u_fresnel_power);
    vec3 chromeBase = mix(vec3(0.1), vec3(0.9), u_chrome_roughness);
    
    // Iridiscencia
    vec3 iriColor = vec3(
        sin(fresnel * 3.14 + u_time * 0.5) * 0.5 + 0.5,
        sin(fresnel * 3.14 + u_time * 0.5 + 2.094) * 0.5 + 0.5,
        sin(fresnel * 3.14 + u_time * 0.5 + 4.189) * 0.5 + 0.5
    );
    vec3 chrome = mix(chromeBase, iriColor, u_iridescence);
    chrome = mix(chrome, u_color1, fresnel * 0.5);
    
    // Aplicar sobre el dígito
    float digitMask = smoothstep(0.02, 0.0, d);
    float glowMask = smoothstep(0.15, 0.0, d);
    
    col = mix(col, chrome, digitMask);
    
    // Bloom del dígito — pulsa con el bass
    vec3 glowColor = mix(u_color1, u_color2, sin(u_time) * 0.5 + 0.5);
    glowColor *= 1.0 + u_bass * 2.0;
    col += glowColor * glowMask * u_bloom_intensity * 0.4;
    
    // Cubo 3D fondo
    float cubePattern = sin(p.x * 5.0 + u_time) * sin(p.y * 5.0 + u_time * 0.7);
    col += u_color2 * step(0.8, cubePattern) * u_cube_opacity * 0.2;
    
    // Flash en golpe de bass
    col += u_color1 * u_bass * 0.15 * exp(-length(p) * 1.5);
    
    fragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
```

**Custom Parameters en Base FILTER_08:**
- `Countdown` (Float, 0-9, default 9) → ¡conéctalo a un timer CHOP para countdown automático!
- `ChromeRoughness` (Float, 0-1, default 0.15)
- `FresnelPower` (Float, 1-8, default 3.0)
- `BloomIntensity` (Float, 0-3, default 1.5)
- `Iridescence` (Float, 0-1, default 0.4)
- `CubeOpacity` (Float, 0-1, default 0.3)
- `MixAmount` (Float, 0-1, default 1.0)

---

## Módulo MIX_OUTPUT

Crear dentro de `MIX_OUTPUT`:
- 8x inputs (uno por filtro)
- 1x `switch` TOP + `cross` TOP para mezcla suave entre shaders
- 1x `over` TOP para superposición aditiva
- 1x `out` TOP llamado `FINAL_OUTPUT`

**Custom Parameters en Base MIX_OUTPUT:**
- `ActiveFilter` (Menu: CRT_VHS / NEON_GRID / LIQUID / STARFIELD / CINEMATIC / SPLATTER / BOKEH / CHROME)
- `CrossfadeAmount` (Float, 0-1, default 0.0)
- `CrossfadeTarget` (Menu: igual que ActiveFilter)
- `MasterBrightness` (Float, 0-2, default 1.0)
- `MasterOpacity` (Float, 0-1, default 1.0)

---

## Script Python para generar la red

Genera un archivo `alan_navarro_vj.py` completo que:

1. **Cree toda la jerarquía de Base COMPs** con `op('/project1').create(baseCOMP, 'ALAN_NAVARRO_VJ')` etc.
2. **Agregue todos los TOPs y CHOPs** dentro de cada Base usando `base.create(glslTOP, 'shader')` etc.
3. **Configure el código GLSL** de cada filtro con `glsl_op.par.pixeldat.val = SHADER_CODE`
4. **Cree todos los Custom Parameters** usando `page = base.appendCustomPage('Controls')` y `page.appendFloat('MixAmount', label='Mix Amount')` etc.
5. **Configure los valores default** de cada parámetro
6. **Conecte los nodos**: AUDIO_OUT → shaders, palette → shaders, shaders → mixer
7. **Haga layout automático** con posicionamiento en UI usando `op.nodeX` y `op.nodeY`
8. **Imprima un log de confirmación** al final con el nombre de cada base creada

### Notas técnicas para el script:

```python
# Audio: UN solo canal llamado 'bass'
# El usuario conecta manualmente su select CHOP externo al IN CHOP de AUDIO_ANALYSIS
# El script solo crea: in_chop → math (gain) → lag (attack/release) → null AUDIO_OUT
# Canal de salida: 'bass' (renombrado en el rename CHOP antes del null)

# Ejemplo creación AUDIO_ANALYSIS simplificado:
audio_base = root.create(baseCOMP, 'AUDIO_ANALYSIS')
in_chop    = audio_base.create(inCHOP, 'AUDIO_IN')      # usuario conecta aquí su select CHOP
math_chop  = audio_base.create(mathCHOP, 'gain')
lag_chop   = audio_base.create(lagCHOP, 'smooth')
rename_chop = audio_base.create(renameCHOP, 'rename')   # renombra canal 0 → 'bass'
null_chop  = audio_base.create(nullCHOP, 'AUDIO_OUT')

# Conectar cadena
math_chop.inputConnectors[0].connect(in_chop)
lag_chop.inputConnectors[0].connect(math_chop)
rename_chop.inputConnectors[0].connect(lag_chop)
null_chop.inputConnectors[0].connect(rename_chop)

# Threshold: cortar piso de ruido
# Agregar math CHOP extra con expresión: max(val - threshold, 0) / (1 - threshold)

# Conexión del uniform u_bass al GLSL TOP:
# En TD, conectar AUDIO_OUT como CHOP input al GLSL TOP (input index 1 o 2 según orden)
# En el DAT de uniforms del GLSL TOP agregar fila:
#   name: bass   type: float   chop: ../../../AUDIO_ANALYSIS/AUDIO_OUT   chan: bass

# Ejemplo de creación de Custom Parameter Float en TD:
page = base.appendCustomPage('Controls')
p = page.appendFloat('MixAmount', label='Mix Amount')
p[0].default = 1.0
p[0].min = 0.0
p[0].max = 1.0
p[0].clampMin = True
p[0].clampMax = True

# Ejemplo de asignar shader GLSL:
glsl_op = base.create(glslTOP, 'shader_main')
glsl_op.par.pixeldat.val = """
// shader code aquí
"""

# Para exponer parámetro de Base como variable en shader:
# glsl_op.par.value0x.expr = "op('../').par.MixAmount"
```

---

## Output esperado

Al ejecutar el script en TouchDesigner TextPort:
- ✅ 1 Base COMP `ALAN_NAVARRO_VJ` contenedor
- ✅ 10 Bases internas (AUDIO_ANALYSIS, PALETTE_SYSTEM, 8 filtros, MIX_OUTPUT)
- ✅ `AUDIO_ANALYSIS` con `AUDIO_IN` listo para recibir el select CHOP del usuario → canal único `bass`
- ✅ Cada filtro con su GLSL TOP, IN TOP, OUT TOP
- ✅ Custom Parameters expuestos en cada Base
- ✅ `u_bass` conectado a todos los filtros como único driver de audio
- ✅ Paleta conectada a todos los filtros vía uniforms
- ✅ Output final en MIX_OUTPUT listo para mapear a pantalla

---

## Notas finales para el show

- **Paleta NEON_URBAN** → canciones de CD9 grupo (era urbana)
- **Paleta COASTAL_WARM** → canciones solistas de Alan (California, Santa Mónica)
- **Paleta ASTRAL_DEEP** → Las Estrellas No Brillan, momentos emotivos
- **FILTER_08 Countdown** → conectar `u_countdown` a un `timer` CHOP para countdown real previo al drop
- **FILTER_05 Cinematic** → usar siempre como capa base con baja opacidad para unificar la estética del set completo
