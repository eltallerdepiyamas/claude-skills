// layout_mv_multiview.frag — "Multiview" · Little Jesus · Río Salvaje
// Las cámaras en mosaico limpio, tipo multiview de transmisión, sobre la crema del flyer. El
// acomodo sigue a "Camaras en multicam": 2 lado a lado · 3 (una grande + dos) · 4 en 2×2 ·
// 5 en 2 arriba + 3 abajo. Cada celda con borde del color de su cámara y esquinas redondeadas;
// un "tally" recorre las celdas y resalta una a la vez. Cámaras = sTD2DInputs[0..4].

uniform float uTime;
uniform float uPhase;        // reloj acumulado de la velocidad (knob 2, con su audio): no brinca
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;       // 0 Fill · 1 Fit · 2 Stretch
uniform float uCamAspect;

uniform float uBorder;       // 1 intensidad · 0–1     grosor del borde de color de cada celda
uniform float uTally;        // 2 velocidad  · 0–1     velocidad del tally que resalta una celda (0 = apagado)
uniform float uRound;        // 3 distorsión · 0–1     esquinas redondeadas
uniform float uTint;         // 4 color      · 0–1     duotono de cada celda con su color
uniform float uGap;          // 5 firma      · 0–0.08  separación entre celdas (alto de pantalla = 1)
uniform vec3  uColor1;       // amarillo
uniform vec3  uColor2;       // verde
uniform vec3  uColor3;       // azul
uniform vec3  uColor4;       // negro
uniform vec3  uColor5;       // rojo
uniform vec3  uBgColor;      // crema

out vec4 fragColor;

// -- tinte del album (ESTANDAR Rio Salvaje, igual en todos los layouts) ---------------------------
// La camara toma un color de la paleta del album segun su luz (como los discos de Playeras).
// amt = el slider de color (4); 0 = camara limpia. Nada de hue / chroma / RGB.
vec3 albumColor(int i) {
    i = i - (i / 5) * 5;
    if (i == 0) return uColor1;   // amarillo
    if (i == 1) return uColor2;   // verde
    if (i == 2) return uColor3;   // azul
    if (i == 3) return uColor4;   // negro
    return uColor5;               // rojo
}
float albumLuma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
vec3 albumTint(vec3 cam, vec3 pc, float amt) {
    return mix(cam, pc * (0.35 + 1.3 * albumLuma(cam)), clamp(amt, 0.0, 1.0) * 0.75);
}

// ── ajuste de aspecto de cámara dentro de su celda (0 Fill · 1 Fit · 2 Stretch)
vec2 applyCamFit(vec2 cellUV, float camAspect, float cellAspect, int fitMode) {
    if (fitMode == 2) return cellUV;
    float scaleX = 1.0;
    float scaleY = 1.0;
    float ratio = cellAspect / camAspect;
    if (fitMode == 0) {
        if (ratio > 1.0) scaleY = ratio;
        else             scaleX = 1.0 / ratio;
    } else {
        if (ratio > 1.0) scaleX = 1.0 / ratio;
        else             scaleY = ratio;
    }
    vec2 c = cellUV - 0.5;
    c.x /= scaleX;
    c.y /= scaleY;
    return c + 0.5;
}

// cámara idx en una celda de cellW × cellH píxeles. Fill recorta; Fit deja negro fuera.
vec4 sampleCam(int idx, vec2 localUV, float cellW, float cellH) {
    float cellAspect = cellW / max(cellH, 0.0001);
    vec2 fitUV = applyCamFit(localUV, uCamAspect, cellAspect, uCamfit);
    if (uCamfit != 1) {
        fitUV = clamp(fitUV, 0.0, 1.0);
    } else if (fitUV.x < 0.0 || fitUV.x > 1.0 || fitUV.y < 0.0 || fitUV.y > 1.0) {
        return vec4(0.0, 0.0, 0.0, 1.0);
    }
    if (idx == 0) return texture(sTD2DInputs[0], fitUV);
    if (idx == 1) return texture(sTD2DInputs[1], fitUV);
    if (idx == 2) return texture(sTD2DInputs[2], fitUV);
    if (idx == 3) return texture(sTD2DInputs[3], fitUV);
    if (idx == 4) return texture(sTD2DInputs[4], fitUV);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

vec3 pal(int i) {
    if (i == 0) return uColor1;
    if (i == 1) return uColor2;
    if (i == 2) return uColor3;
    if (i == 3) return uColor4;
    return uColor5;
}

float sdRoundRect(vec2 p, vec2 b, float r) {
    vec2 d = abs(p) - b + r;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0) - r;
}

float luma(vec3 c) {
    return dot(c, vec3(0.2126, 0.7152, 0.0722));
}

// rectangulo (x0, y0, x1, y1) en 0..1 de la celda i para n camaras
vec4 cellRect(int i, int n) {
    if (n == 2) return vec4(0.5 * float(i), 0.0, 0.5 * float(i) + 0.5, 1.0);
    if (n == 3) {
        if (i == 0) return vec4(0.0, 0.0, 0.62, 1.0);                     // grande a la izquierda
        return vec4(0.62, i == 1 ? 0.5 : 0.0, 1.0, i == 1 ? 1.0 : 0.5);
    }
    if (n == 4) {
        float x = float(i % 2) * 0.5;
        float y = i < 2 ? 0.5 : 0.0;
        return vec4(x, y, x + 0.5, y + 0.5);
    }
    // 5: dos arriba, tres abajo
    if (i < 2) return vec4(0.5 * float(i), 0.5, 0.5 * float(i) + 0.5, 1.0);
    float x = float(i - 2) / 3.0;
    return vec4(x, 0.0, x + 1.0 / 3.0, 0.5);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    float px = 1.0 / uResolution.y;
    int n = clamp(uCamCount, 2, 5);
    float g = clamp(uGap, 0.0, 0.1);

    // celda activa del tally (avanza en orden; 0 = sin tally)
    float tallyPos = mod(uPhase * 1.5, float(n));
    int tallyCell = int(floor(tallyPos));
    float tallyOn = step(0.001, uTally);

    vec3 col = uBgColor;
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;
        vec4 r = cellRect(i, n);
        // en unidades de alto (x escalado por el aspecto) para que separacion y esquinas sean parejas
        vec2 c = vec2((r.x + r.z) * 0.5 * aspect, (r.y + r.w) * 0.5);
        vec2 hb = vec2((r.z - r.x) * aspect, r.w - r.y) * 0.5 - vec2(g * 0.5 + 0.01);
        vec2 lp = vec2(uv.x * aspect, uv.y) - c;
        float rad = clamp(uRound, 0.0, 1.0) * min(hb.x, hb.y) * 0.35;
        float d = sdRoundRect(lp, hb, rad);
        if (d > px) continue;

        vec3 pc = pal(i);
        float bw = clamp(uBorder, 0.0, 1.0) * 0.025;
        bool tally = tallyOn > 0.5 && i == tallyCell;
        float bwi = bw + (tally ? 0.012 : 0.0);

        vec2 camUV = lp / (2.0 * hb) + 0.5;
        vec3 cam = sampleCam(i, camUV, 2.0 * hb.x * uResolution.y, 2.0 * hb.y * uResolution.y).rgb;
        cam = albumTint(cam, pc, uTint);

        vec3 cellCol = mix(cam, pc, smoothstep(-bwi - px, -bwi + px, d));   // borde de color hacia adentro
        col = mix(col, cellCol, 1.0 - smoothstep(-px, px, d));
    }

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
