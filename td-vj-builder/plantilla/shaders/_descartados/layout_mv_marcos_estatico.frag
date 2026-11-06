// layout_mv_marcos.frag — "Marcos" · Little Jesus · Rio Salvaje
// Collage de las camaras COMPLETAS (su proporcion real, sin recorte), cada una con un paspartu
// grueso de un color del album y un bloque solido desfasado detras, como cuadros colgados en una pared
// crema. Dos filas escalonadas que derivan y giran poco; el desorden las desacomoda.
// Camaras = sTD2DInputs[0..4].

uniform float uTime;
uniform float uPhase;        // reloj acumulado de la velocidad (knob 2, con su audio): no brinca
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;       // 0 Fill · 1 Fit · 2 Stretch
uniform float uCamAspect;

uniform float uMarco;        // 1 intensidad · 0-1     grosor del paspartu de color
uniform float uSpeed;        // 2 velocidad  · 0-1.5   deriva del collage
uniform float uDesorden;     // 3 distorsion · 0-1     giro y desacomodo de los cuadros
uniform float uTint;         // 4 color      · 0-1     tinte del album en cada camara (su color)
uniform float uEscala;       // 5 firma      · 0.5-1.2 tamano de las camaras
uniform float uSombra;       // extra · 0-0.06  bloque de color desfasado detras de cada cuadro
uniform vec3  uColor1;       // paleta del album: amarillo
uniform vec3  uColor2;       // verde
uniform vec3  uColor3;       // azul
uniform vec3  uColor4;       // negro
uniform vec3  uColor5;       // rojo
uniform vec3  uBgColor;      // crema del album

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

// -- ajuste de aspecto de camara dentro de su celda (0 Fill · 1 Fit · 2 Stretch)
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

// camara idx en una celda de cellW x cellH pixeles. textureLod: sin pixeles rotos entre celdas vecinas.
vec4 sampleCam(int idx, vec2 localUV, float cellW, float cellH) {
    float cellAspect = cellW / max(cellH, 0.0001);
    vec2 fitUV = applyCamFit(localUV, uCamAspect, cellAspect, uCamfit);
    if (uCamfit != 1) {
        fitUV = clamp(fitUV, 0.0, 1.0);
    } else if (fitUV.x < 0.0 || fitUV.x > 1.0 || fitUV.y < 0.0 || fitUV.y > 1.0) {
        return vec4(0.0, 0.0, 0.0, 1.0);
    }
    if (idx == 0) return textureLod(sTD2DInputs[0], fitUV, 0.0);
    if (idx == 1) return textureLod(sTD2DInputs[1], fitUV, 0.0);
    if (idx == 2) return textureLod(sTD2DInputs[2], fitUV, 0.0);
    if (idx == 3) return textureLod(sTD2DInputs[3], fitUV, 0.0);
    if (idx == 4) return textureLod(sTD2DInputs[4], fitUV, 0.0);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

mat2 rot(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c);
}

float hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

// centro de la camara i (alto de pantalla = 1, ancho = aspect): dos filas escalonadas
vec2 slotCenter(int i, int n, float aspect) {
    if (n == 2) return vec2((i == 0 ? 0.27 : 0.73) * aspect, 0.5);   // 2: lado a lado
    int top = (n + 1) / 2;
    bool isTop = i < top;
    int k = isTop ? i : i - top;
    int cnt = isTop ? top : n - top;
    float x = (float(k) + 0.5) / float(cnt) * aspect + (isTop ? -0.04 : 0.04) * aspect;
    float y = (n == 2) ? 0.5 : (isTop ? 0.71 : 0.29);
    return vec2(x, y);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    float px = 1.0 / uResolution.y;
    int n = clamp(uCamCount, 2, 5);
    int top = (n + 1) / 2;
    vec2 q = vec2(uv.x * aspect, uv.y);
    float dis = clamp(uDesorden, 0.0, 1.0);
    float frame = clamp(uMarco, 0.0, 1.0) * 0.05;

    // la camara mantiene SU proporcion; se achica si la fila no cabe
    float camH = clamp(uEscala, 0.3, 1.4) * (n == 2 ? 0.55 : 0.36);
    vec2 hb = vec2(camH * uCamAspect, camH) * 0.5;
    float maxW = aspect / float(n == 2 ? 2 : top) * 0.86 - 2.0 * frame;
    if (2.0 * hb.x > maxW) hb *= maxW / (2.0 * hb.x);

    vec3 col = uBgColor;
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;
        vec2 c = slotCenter(i, n, aspect);
        float t = uPhase * 0.35 + float(i) * 1.7;
        c += dis * vec2(0.035 * sin(float(i) * 2.3), 0.03 * cos(float(i) * 1.7));
        c += dis * vec2(0.05 * sin(t * 0.9), 0.04 * cos(t * 0.7 + 1.3)) * min(uSpeed * 4.0, 1.0);
        float ang = dis * (0.08 * sin(float(i) * 1.9) + 0.04 * sin(uPhase * 0.25 + float(i)));
        vec2 p = q - c;
        vec2 lp = rot(ang) * p;

        // bloque solido desfasado detras
        if (uSombra > 0.0005) {
            float ds = sdBox(rot(ang) * (p - vec2(uSombra, -uSombra)), hb + frame);
            col = mix(col, albumColor(i + 2), 1.0 - smoothstep(-px, px, ds));
        }
        // paspartu de color
        float dfr = sdBox(lp, hb + frame);
        col = mix(col, albumColor(i), 1.0 - smoothstep(-px, px, dfr));
        // camara completa
        float dc = sdBox(lp, hb);
        if (dc < px) {
            vec2 cuv = lp / (2.0 * hb) + 0.5;
            vec3 cam = sampleCam(i, cuv, 2.0 * hb.x * uResolution.y, 2.0 * hb.y * uResolution.y).rgb;
            cam = albumTint(cam, albumColor(i), uTint);
            col = mix(col, cam, 1.0 - smoothstep(-px, px, dc));
        }
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
