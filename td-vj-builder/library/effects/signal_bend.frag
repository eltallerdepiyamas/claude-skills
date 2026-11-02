// =====================================================================
// signal_bend.frag — Circuit bending de video
// Categoria: efecto / filtro (convencion camelCase, sTD2DInputs)
//   sTD2DInputs[0] = video de entrada
//   sTD2DInputs[1] = feedback (frame anterior)
//
// Cadena de señal (en este orden — cada etapa corrompe lo anterior,
// igual que en la placa real):
//   1) drift/chaos global   -> ruido lento que modula todo, acoplamiento entre etapas
//   2) sync corruption      -> offset por linea + skew + linedrop + vhold
//   3) sample & hold        -> cuantizacion en columnas onduladas (peine)
//   4) luma -> displacement -> brillo empuja posicion (feedback local)
//   5) chroma desacoplado   -> muestreo separado + hue por luma + drift
//   6) oscilador            -> bandas de arcoiris fijas (seno/cuadrada, gated por luma)
//   7) corrupcion de bits   -> crush + XOR gateado por threshold
//   8) sparkle              -> rejilla de puntos blancos en picos
//   9) feedback             -> mezcla con frame anterior + zoom/rot (el bend "canta")
//   10) wet/dry             -> Intensity contra la fuente
// =====================================================================

out vec4 fragColor;

uniform float uTime;
uniform vec2  uResolution;

uniform vec4 uMacro;    // x Intensity | y Speed | z Bend | w Chroma
uniform vec4 uChaos;    // x Chaos | y DriftAmt | z DriftSpeed | w (libre)
uniform vec4 uSync;     // x Lineshift | y Linestep | z Skew | w Linedrop
uniform vec4 uVhold;    // x Vhold | y Vholdspeed | z (libre) | w (libre)
uniform vec4 uClock;    // x Columns | y Colwave | z Colwavefreq | w Holdskew
uniform vec4 uHold;     // x Holdmix | y Lumapush | z Lumapushy | w Lumabias
uniform vec4 uChromaA;  // x Chromaoffsetx | y Chromaoffsety | z Hueluma | w Huedrift
uniform vec4 uChromaB;  // x Chromagain | y Chromaclip(0/1) | z (libre) | w (libre)
uniform vec4 uOsc;      // x Oscamt | y Oscfreq | z Oscspread | w Oscshape(0=sine,1=square)
uniform vec4 uOscGate;  // x Oscgate | y (libre) | z (libre) | w (libre)
uniform vec4 uCorrupt;  // x Crush | y Xoramount | z Xormask(0-255) | w Xorthresh
uniform vec4 uSparkle;  // x Sparkleamt | y Sparklescale | z Sparklethresh | w (libre)
uniform vec4 uFb;       // x Fbdecay(<1) | y Fbzoom | z Fbrot(deg) | w (libre)

#define M_INTENSITY  uMacro.x
#define M_SPEED      uMacro.y
#define M_BEND       uMacro.z
#define M_CHROMA     uMacro.w
#define M_CHAOS      uChaos.x

// ---------------- helpers de hash / noise ----------------
float hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float vnoise(float x) {
    float i = floor(x);
    float f = fract(x);
    float u = f * f * (3.0 - 2.0 * f);
    return mix(hash11(i), hash11(i + 1.0), u);
}

float fbm1(float x) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) {
        v += a * vnoise(x);
        x *= 2.03;
        a *= 0.5;
    }
    return v;
}

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

// XOR entero (ivec3 ^ int) via bitwiseXor manual: GLSL 4.30+ soporta ^ nativo
ivec3 ixor(ivec3 a, int m) { return a ^ ivec3(m); }

void main() {
    vec2 uv = vUV.st;
    float t = uTime * max(0.01, M_SPEED);
    float bend    = M_BEND;
    float chroma  = M_CHROMA;
    float chaos   = M_CHAOS;

    // ---------------- 1) drift global ----------------
    float drift = (fbm1(t * uChaos.z * 0.5) - 0.5) * 2.0 * uChaos.y;   // -1..1
    // acoplamiento por Chaos: con chaos alto, drift modula bend y chroma juntos
    float bendC   = bend   * (1.0 + chaos * drift);
    float chromaC = chroma * (1.0 + chaos * drift * 0.7);

    // ---------------- 2) sync corruption ----------------
    float line     = floor(uv.y * uResolution.y);
    float lineJump = floor(t * max(0.5, uSync.y * 30.0));   // saltos escalonados
    float lineH    = hash12(vec2(line, lineJump)) - 0.5;
    // brillo medio de la linea: aproximado con tap en la columna central (1 fetch)
    float lumaLine = dot(texture(sTD2DInputs[0], vec2(0.5, uv.y)).rgb,
                         vec3(0.299, 0.587, 0.114));

    float lineOff = lineH * uSync.x * bendC
                  + sin(line * 0.07 + t * 3.0) * uSync.x * 0.30
                  + (lumaLine - 0.5) * uHold.y * 0.15 * bendC;   // luma -> x (crossfeed)

    float skew   = (uv.y - 0.5) * uSync.z * bendC;
    float vhold  = sin(t * uVhold.y) * uVhold.x * bendC;

    vec2 uv1 = uv;
    uv1.x += lineOff + skew;
    uv1.y  = fract(uv1.y + vhold);

    // linedrop: linea completa reemplazada por otra (no negra)
    if (hash12(vec2(line * 0.7, lineJump)) < uSync.w * bendC) {
        uv1.y = fract(uv1.y + hash11(line + lineJump * 3.7) * 0.30);
    }

    // ---------------- 3) sample & hold: columnas onduladas ----------------
    float cols = max(4.0, uClock.x * (1.0 + drift * chaos * 0.3));
    cols += sin(uv1.y * 6.2831 * uClock.z + t * 0.8) * uClock.y * cols * 0.30;
    // holdskew: la fase de la cuantizacion se corre segun uv.y (curva las columnas)
    float phase = uv1.y * uClock.w * 8.0;
    float uxCol = floor((uv1.x + phase / max(cols, 1.0)) * cols) / cols;
    // mezcla dura vs suave
    float uxHold = mix(uv1.x, uxCol, clamp(uHold.x, 0.0, 1.0));
    vec2 uv2 = vec2(uxHold, uv1.y);

    // ---------------- 4) luma -> displacement (feedback local) ----------------
    vec3 sample1 = texture(sTD2DInputs[0], uv2).rgb;
    float l1 = dot(sample1, vec3(0.299, 0.587, 0.114)) - uHold.w;
    uv2.x += l1 * uHold.y * 0.05 * bendC;
    uv2.y += l1 * uHold.z * 0.02 * bendC;

    // ---------------- 5) chroma desacoplado ----------------
    vec2 uvC = uv2 + vec2(uChromaA.x, uChromaA.y) * chromaC * 0.05;
    vec3 lumaSample   = texture(sTD2DInputs[0], uv2).rgb;
    vec3 chromaSample = texture(sTD2DInputs[0], uvC).rgb;

    float lumaGray = dot(lumaSample, vec3(0.299, 0.587, 0.114));
    vec3  hsvC = rgb2hsv(chromaSample);
    hsvC.x = fract(hsvC.x
                 + lumaGray * uChromaA.z * chromaC
                 + t * uChromaA.w * 0.10);
    hsvC.y *= (1.0 + (uChromaB.x - 1.0) * chromaC);
    if (uChromaB.y > 0.5) hsvC.y = clamp(hsvC.y, 0.0, 1.0);
    vec3 col = hsv2rgb(vec3(hsvC.x, hsvC.y, lumaGray));
    col = mix(lumaSample, col, chromaC);

    // ---------------- 6) inyeccion de oscilador ----------------
    float oscFreq   = uOsc.y;
    float oscSpread = uOsc.z * 0.15;
    float phR = uv2.x * uResolution.x * 0.001 * oscFreq + t * 2.1;
    float phG = uv2.x * uResolution.x * 0.001 * (oscFreq + oscSpread * 20.0) + t * 2.3;
    float phB = uv2.x * uResolution.x * 0.001 * (oscFreq + oscSpread * 40.0) + t * 2.5;
    vec3 osc = vec3(sin(phR), sin(phG), sin(phB));
    if (uOsc.w > 0.5) osc = sign(osc);
    float oscGate = smoothstep(uOscGate.x, uOscGate.x + 0.2, lumaGray);
    col += osc * uOsc.x * chromaC * oscGate;

    // ---------------- 7) corrupcion de bits ----------------
    float crush = uCorrupt.x;
    if (crush > 2.5) col = floor(col * crush) / crush;

    float xorAmt = uCorrupt.y * bendC;
    if (xorAmt > 0.001) {
        vec3 threshMask = step(vec3(uCorrupt.w), col);
        ivec3 iC = ivec3(clamp(col, 0.0, 1.0) * 255.0);
        int   m  = int(clamp(uCorrupt.z, 0.0, 255.0));
        vec3 corrupted = vec3(ixor(iC, m)) / 255.0;
        col = mix(col, corrupted, xorAmt * threshMask);
    }

    // ---------------- 8) sparkle ----------------
    if (uSparkle.x > 0.001) {
        float scale = max(1.0, uSparkle.y);
        vec2  spCell = floor(uv * uResolution.xy / scale);
        float spH    = hash12(spCell + floor(t * 20.0));
        float sp     = step(1.0 - uSparkle.x * 0.05, spH)
                     * step(uSparkle.z, lumaGray);
        col += vec3(sp);
    }

    // ---------------- 9) feedback ----------------
    if (uFb.x > 0.001) {
        vec2 fbUV = uv - 0.5;
        float ang = uFb.z * 0.01745329;   // deg -> rad
        float cs = cos(ang), sn = sin(ang);
        fbUV = mat2(cs, -sn, sn, cs) * fbUV / max(0.5, uFb.y);
        fbUV += 0.5;
        vec3 prev = texture(sTD2DInputs[1], fbUV).rgb;
        col = mix(col, prev, min(0.95, uFb.x));   // nunca 1.0 (se blanquea)
    }

    // ---------------- 10) wet/dry ----------------
    vec3 srcCol = texture(sTD2DInputs[0], uv).rgb;
    col = mix(srcCol, col, clamp(M_INTENSITY, 0.0, 1.0));

    fragColor = TDOutputSwizzle(vec4(max(col, vec3(0.0)), 1.0));
}
