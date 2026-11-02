// =====================================================================
// crt_pvm.frag — Procesador CRT completo (PVM / Trinitron como base)
// Categoria: efecto / filtro (convencion camelCase, sTD2DInputs)
//   sTD2DInputs[0] = video de entrada (Movie File In)
//   sTD2DInputs[1] = feedback (persistencia de fosforo)
//
// Cadena de señal (en este orden, como un tubo real):
//   geometria de pantalla (4:3 / 16:9) -> curvatura -> overscan
//   -> wobble (roll, jitter por linea, banda de tracking)
//   -> RGB delay -> chroma bleed -> dot crawl
//   -> halation/bloom -> scanlines -> interlace -> mascara de fosforo
//   -> damper wires -> hum bar -> persistencia -> grade -> ruido
//   -> vignette -> esquinas redondeadas -> reflejo de vidrio -> bezel
//
// Los uniforms van empacados en vec4 para no reventar la pagina Vectors
// del GLSL TOP. Los #define de abajo son el mapa legible.
// =====================================================================

out vec4 fragColor;

uniform float uTime;
uniform vec2  uResolution;

uniform vec4 uMacro;   // x Intensity | y Speed | z Warp | w RgbDelay(px)
uniform vec4 uScan;    // x ScanDepth | y ScanCount | z ScanSharp | w ScanRoll
uniform vec4 uGeom;    // x Curvature | y Corner | z Overscan | w AspectMode
uniform vec4 uMask;    // x MaskStrength | y MaskPitch(px) | z MaskMode | w WireStrength
uniform vec4 uSignal;  // x ChromaBleed | y DotCrawl | z Interlace | w Hum
uniform vec4 uGrade;   // x Brightness | y Contrast | z Saturation | w Gamma
uniform vec4 uGlow;    // x Bloom | y BloomRadius(px) | z BloomThresh | w Persistence
uniform vec4 uNoise;   // x Grain | y Snow | z Tracking | w Vignette
uniform vec4 uWobble;  // x HJitter | y JitterSpeed | z RollAmount | w RollSpeed
uniform vec4 uFrame;   // x Glare | y BlackLevel | z SrcAspect | w BezelDark
uniform vec4 uTint;    // rgb = tinte de fosforo (punto blanco del tubo)

#define M_INTENSITY  uMacro.x
#define M_SPEED      uMacro.y
#define M_WARP       uMacro.z
#define M_RGBDELAY   uMacro.w
#define SCAN_DEPTH   uScan.x
#define SCAN_COUNT   uScan.y
#define SCAN_SHARP   uScan.z
#define SCAN_ROLL    uScan.w
#define CURVATURE    uGeom.x
#define CORNER       uGeom.y
#define OVERSCAN     uGeom.z
#define ASPECT_MODE  uGeom.w
#define MASK_AMT     uMask.x
#define MASK_PITCH   uMask.y
#define MASK_MODE    uMask.z
#define WIRE_AMT     uMask.w
#define CHROMA_BLEED uSignal.x
#define DOT_CRAWL    uSignal.y
#define INTERLACE    uSignal.z
#define HUM          uSignal.w
#define BRIGHTNESS   uGrade.x
#define CONTRAST     uGrade.y
#define SATURATION   uGrade.z
#define GAMMA        uGrade.w
#define BLOOM        uGlow.x
#define BLOOM_RAD    uGlow.y
#define BLOOM_THR    uGlow.z
#define PERSISTENCE  uGlow.w
#define GRAIN        uNoise.x
#define SNOW         uNoise.y
#define TRACKING     uNoise.z
#define VIGNETTE     uNoise.w
#define HJITTER      uWobble.x
#define JITTER_SPEED uWobble.y
#define ROLL_AMT     uWobble.z
#define ROLL_SPEED   uWobble.w
#define GLARE        uFrame.x
#define BLACKLEVEL   uFrame.y
#define SRC_ASPECT   uFrame.z
#define BEZEL_DARK   uFrame.w

const float PI = 3.14159265;

// ------------------------- helpers -------------------------
float saturate1(float x) { return clamp(x, 0.0, 1.0); }
vec3  saturate3(vec3 x)  { return clamp(x, 0.0, 1.0); }
float luma(vec3 c)       { return dot(c, vec3(0.299, 0.587, 0.114)); }

float hash21(vec2 p) {
    p = fract(p * vec2(443.897, 441.423));
    p += dot(p, p + 19.19);
    return fract(p.x * p.y);
}

// Muestra el contenido. Fuera del area de contenido = negro (barras del
// letterbox: en un CRT real ahi no hay emision de fosforo).
vec3 src(vec2 uv) {
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) return vec3(0.0);
    return texture(sTD2DInputs[0], uv).rgb;
}

// Rectangulo redondeado en espacio [-1,1]: <0 dentro, >0 fuera.
float roundedBox(vec2 p, vec2 halfSize, float r) {
    vec2 q = abs(p) - halfSize + r;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

void main() {
    vec2  res       = uResolution;
    float outAspect = res.x / max(1.0, res.y);
    vec2  uv        = vUV.st;
    float t         = uTime * max(0.0, M_SPEED);
    float warp      = M_WARP;

    // =================================================================
    // 1. GEOMETRIA DE PANTALLA — el tubo dentro del frame de salida
    //    AspectMode: 0 = 16:9 nativo | 1 = 4:3 fit (letterbox dentro del
    //    tubo) | 2 = 4:3 fill (recorta los lados) | 3 = 4:3 anamorfico
    // =================================================================
    int   am           = int(ASPECT_MODE + 0.5);
    float screenAspect = (am == 0) ? outAspect : (4.0 / 3.0);

    vec2 fitScale = vec2(1.0);
    if (screenAspect < outAspect) fitScale.x = screenAspect / outAspect;
    else                          fitScale.y = outAspect / screenAspect;

    vec2 suv = (uv - 0.5) / fitScale + 0.5;      // 0..1 dentro del tubo
    if (suv.x < -0.02 || suv.x > 1.02 || suv.y < -0.02 || suv.y > 1.02) {
        // Fuera del tubo: bezel. Salida temprana, no cuesta nada.
        vec3 raw = texture(sTD2DInputs[0], uv).rgb;
        vec3 bez = mix(raw, vec3(0.0), saturate1(BEZEL_DARK));
        fragColor = TDOutputSwizzle(vec4(mix(raw, bez, saturate1(M_INTENSITY)), 1.0));
        return;
    }

    // Curvatura de barril + overscan (en espacio centrado [-1,1])
    vec2 c  = suv * 2.0 - 1.0;
    vec2 cc = c * (1.0 + CURVATURE * vec2(c.y * c.y, c.x * c.x));
    cc /= max(0.001, OVERSCAN);
    vec2 puv = cc * 0.5 + 0.5;                   // uv de la superficie del tubo

    // Mascara del tubo: rectangulo redondeado + borde suave
    float box     = roundedBox(cc, vec2(1.0), max(0.001, CORNER * 2.0));
    float edgePx  = 2.5 / max(1.0, res.y);
    float tubeMask = 1.0 - smoothstep(-edgePx, edgePx, box);

    // =================================================================
    // 2. ENCUADRE DEL CONTENIDO dentro del tubo
    // =================================================================
    float k   = max(0.01, SRC_ASPECT) / screenAspect;
    vec2  cuv = puv;
    if (am == 2) {                    // fill / crop
        if (k > 1.0) cuv.x = (puv.x - 0.5) / k + 0.5;
        else         cuv.y = (puv.y - 0.5) * k + 0.5;
    } else if (am != 3) {             // fit (modos 0 y 1)
        if (k > 1.0) cuv.y = (puv.y - 0.5) * k + 0.5;
        else         cuv.x = (puv.x - 0.5) / k + 0.5;
    }                                 // am == 3: anamorfico, estira

    // =================================================================
    // 3. WOBBLE — vertical hold, jitter por linea, banda de tracking
    // =================================================================
    float lines = max(16.0, SCAN_COUNT);
    float line  = floor(puv.y * lines);

    // Roll vertical (sincronia vertical perdida): envuelve, no recorta
    float roll = ROLL_AMT * warp * fract(t * ROLL_SPEED);
    cuv.y = fract(cuv.y + roll);

    // Jitter horizontal por linea de barrido
    float jstep = floor(t * max(0.001, JITTER_SPEED) * 60.0);
    float j     = hash21(vec2(line, jstep)) - 0.5;
    cuv.x += j * HJITTER * warp * 0.02;

    // Banda de tracking que sube por la pantalla
    float bandPos = fract(t * 0.13);
    float band    = smoothstep(0.07, 0.0, abs(fract(puv.y - bandPos + 0.5) - 0.5));
    float bnoise  = hash21(vec2(line, floor(t * 37.0))) - 0.5;
    cuv.x += band * bnoise * TRACKING * warp * 0.05;

    // =================================================================
    // 4. RGB DELAY — desalineacion de los tres cañones
    // =================================================================
    float d = M_RGBDELAY / max(1.0, res.x);
    vec3 col = vec3(
        src(cuv + vec2(d, 0.0)).r,
        src(cuv).g,
        src(cuv - vec2(d, 0.0)).b
    );

    // =================================================================
    // 5. CHROMA BLEED — luma nitida, croma arrastrado (ancho de banda NTSC)
    // =================================================================
    if (CHROMA_BLEED > 0.001) {
        vec3  acc = vec3(0.0);
        float wsum = 0.0;
        for (int i = -3; i <= 3; i++) {
            float o = float(i) * CHROMA_BLEED * 7.0 / max(1.0, res.x);
            float w = 1.0 - abs(float(i)) / 4.0;
            acc  += src(cuv + vec2(o, 0.0)) * w;
            wsum += w;
        }
        acc /= max(0.001, wsum);
        float y = luma(col);
        col = max(vec3(0.0), y + (acc - luma(acc)));
    }

    // =================================================================
    // 6. DOT CRAWL — el hormigueo de croma en los bordes de color
    // =================================================================
    if (DOT_CRAWL > 0.001) {
        float ph = (cuv.x * res.x * 0.5 + line * 0.5 + t * 14.0) * PI;
        float y  = luma(col);
        vec3  ch = col - y;
        col = y + ch * (1.0 + DOT_CRAWL * 0.7 * sin(ph))
                + DOT_CRAWL * 0.03 * sin(ph) * vec3(1.0, -0.6, 1.0) * length(ch);
        col = max(col, vec3(0.0));
    }

    // =================================================================
    // 7. HALATION / BLOOM — el brillo que sangra sobre el vidrio
    // =================================================================
    if (BLOOM > 0.001) {
        vec3  bl = vec3(0.0);
        float rr = BLOOM_RAD / max(1.0, res.y);
        for (int i = 0; i < 8; i++) {
            float a = float(i) * (PI / 4.0);
            vec2  o = vec2(cos(a), sin(a) * outAspect) * rr;
            bl += max(src(cuv + o) - BLOOM_THR, vec3(0.0));
        }
        col += (bl / 8.0) * BLOOM * 2.2 * uTint.rgb;
    }

    // =================================================================
    // 8. SCANLINES — ancladas al tubo, no al contenido
    // =================================================================
    if (SCAN_DEPTH > 0.001) {
        float phase = puv.y * lines + SCAN_ROLL * t;
        float prof  = pow(abs(sin(PI * phase)), max(0.05, SCAN_SHARP) * 2.0);
        // En zonas brillantes el haz engorda y la linea se cierra menos
        float open  = 1.0 - 0.65 * smoothstep(0.35, 1.0, luma(col));
        float depth = SCAN_DEPTH * open;
        col *= mix(1.0, prof, depth);
        col *= 1.0 + depth * 0.40;              // compensacion de brillo
    }

    // =================================================================
    // 9. INTERLACE — campos pares/impares alternando a 60 Hz
    // =================================================================
    if (INTERLACE > 0.001) {
        float field = mod(floor(uTime * 59.94), 2.0);
        float ly    = floor(puv.y * lines);
        float onField = (abs(mod(ly, 2.0) - field) < 0.5) ? 1.0 : 0.5;
        col *= mix(1.0, onField, INTERLACE);
        col *= 1.0 + INTERLACE * 0.18;
    }

    // =================================================================
    // 10. MASCARA DE FOSFORO
    //     0 = aperture grille (Trinitron) | 1 = shadow mask
    //     2 = slot mask | 3 = ninguna
    // =================================================================
    if (MASK_AMT > 0.001) {
        int   mm    = int(MASK_MODE + 0.5);
        float pitch = max(1.0, MASK_PITCH);
        float px    = puv.x * res.x;
        float py    = puv.y * res.y;
        vec3  m     = vec3(1.0);

        if (mm == 0) {                                   // aperture grille
            float f = fract(px / (pitch * 3.0)) * 3.0;
            m = vec3(smoothstep(1.0, 0.0, abs(f - 0.5)),
                     smoothstep(1.0, 0.0, abs(f - 1.5)),
                     smoothstep(1.0, 0.0, abs(f - 2.5)));
            m = m * 1.15 + 0.12;
        } else if (mm == 1) {                            // shadow mask
            float row = floor(py / (pitch * 2.0));
            float f   = fract(px / (pitch * 3.0) + mod(row, 2.0) * 0.5) * 3.0;
            m = vec3(smoothstep(1.0, 0.0, abs(f - 0.5)),
                     smoothstep(1.0, 0.0, abs(f - 1.5)),
                     smoothstep(1.0, 0.0, abs(f - 2.5)));
            float vgap = 0.75 + 0.25 * abs(sin(PI * py / (pitch * 2.0)));
            m = (m * 1.1 + 0.15) * vgap;
        } else if (mm == 2) {                            // slot mask
            float row = floor(py / (pitch * 3.0));
            float f   = fract(px / (pitch * 3.0) + mod(row, 2.0) * 0.5) * 3.0;
            m = vec3(smoothstep(1.0, 0.0, abs(f - 0.5)),
                     smoothstep(1.0, 0.0, abs(f - 1.5)),
                     smoothstep(1.0, 0.0, abs(f - 2.5)));
            float slot = smoothstep(0.0, 0.25, abs(fract(py / (pitch * 3.0)) - 0.5));
            m = (m * 1.1 + 0.15) * (0.7 + 0.3 * slot);
        }

        col *= mix(vec3(1.0), m, MASK_AMT);
        col *= 1.0 + MASK_AMT * 0.55;                    // compensacion
    }

    // Damper wires: los dos hilos horizontales del Trinitron
    if (WIRE_AMT > 0.001) {
        float wpx = 1.6 / max(1.0, res.y);
        float w1  = smoothstep(wpx, 0.0, abs(puv.y - 0.3333));
        float w2  = smoothstep(wpx, 0.0, abs(puv.y - 0.6666));
        col *= 1.0 - WIRE_AMT * 0.85 * saturate1(w1 + w2);
    }

    // =================================================================
    // 11. HUM BAR — la barra de 60 Hz que respira hacia arriba
    // =================================================================
    if (HUM > 0.001) {
        float hpos = fract(t * 0.25);
        float hbar = smoothstep(0.28, 0.0, abs(fract(puv.y - hpos + 0.5) - 0.5));
        col *= 1.0 + HUM * (0.22 * hbar - 0.05);
    }

    // =================================================================
    // 12. PERSISTENCIA DE FOSFORO (feedback, max-blend con decay)
    // =================================================================
    if (PERSISTENCE > 0.001) {
        vec3 prev = texture(sTD2DInputs[1], uv).rgb * min(PERSISTENCE, 0.985);
        col = max(col, prev);
    }

    // =================================================================
    // 13. GRADE — nivel de negro, brillo, contraste, saturacion, gamma, tinte
    // =================================================================
    col = max(col - BLACKLEVEL, vec3(0.0)) / max(0.001, 1.0 - BLACKLEVEL);
    col *= BRIGHTNESS;
    col  = (col - 0.5) * CONTRAST + 0.5;
    col  = max(col, vec3(0.0));
    col  = mix(vec3(luma(col)), col, SATURATION);
    col  = pow(max(col, vec3(0.0)), vec3(1.0 / max(0.05, GAMMA)));
    col *= uTint.rgb;

    // =================================================================
    // 14. RUIDO — grano analogico + nieve de impulso
    // =================================================================
    if (GRAIN > 0.001) {
        float g = hash21(uv * res + vec2(t * 91.7, t * 53.3)) - 0.5;
        col += g * GRAIN * 0.22;
    }
    if (SNOW > 0.001) {
        float s = hash21(uv * res * 1.7 + vec2(t * 131.0, t * 77.0));
        col += step(1.0 - SNOW * 0.06, s) * vec3(1.0) * 0.9;
    }

    // =================================================================
    // 15. VIDRIO — vignette, reflejo, bezel
    // =================================================================
    if (VIGNETTE > 0.001) {
        float v = 1.0 - VIGNETTE * 0.85 * pow(saturate1(dot(cc, cc) * 0.42), 1.4);
        col *= max(v, 0.0);
    }
    if (GLARE > 0.001) {
        float g = smoothstep(1.45, 0.0, length(cc - vec2(-0.45, 0.5)));
        col += g * g * GLARE * 0.14 * vec3(0.85, 0.92, 1.0);
    }

    col *= mix(1.0, tubeMask, saturate1(BEZEL_DARK));

    // =================================================================
    // 16. WET / DRY (macro 1)
    // =================================================================
    vec3 orig = texture(sTD2DInputs[0], uv).rgb;
    col = mix(orig, col, saturate1(M_INTENSITY));

    fragColor = TDOutputSwizzle(vec4(max(col, vec3(0.0)), 1.0));
}
