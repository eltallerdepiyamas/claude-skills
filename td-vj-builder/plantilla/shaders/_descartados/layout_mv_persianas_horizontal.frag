// layout_mv_persianas.frag — "Persianas" (horizontal) · Little Jesus · Rio Salvaje
// Persiana horizontal: bandas a lo ancho que suben despacio; cada banda es una ventana a una
// camara (imagen HORIZONTAL, nunca rebanadas verticales). Entre bandas, listones de un color del
// album que abren y cierran en ola, como una persiana. Linea crema en la orilla de cada ventana.
// Encuadre (extra): 0 = la banda deja ver su pedazo de la camara a pantalla completa (ventana)
//                   1 = cada banda muestra su camara completa recortada en formato cine.
// Camaras = sTD2DInputs[0..4]. Version vertical anterior: shaders/_descartados/layout_mv_persianas_vertical.frag

uniform float uTime;
uniform float uPhase;        // reloj acumulado de la velocidad (knob 2, con su audio): no brinca
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;       // 0 Fill · 1 Fit · 2 Stretch
uniform float uCamAspect;

uniform float uApertura;     // 1 intensidad · 0-1     cuanto abre la persiana (1 = casi sin listones)
uniform float uSpeed;        // 2 velocidad  · 0-1.5   las bandas suben
uniform float uInclinacion;  // 3 distorsion · -0.25-0.25 inclinacion de la persiana (rad)
uniform float uTint;         // 4 color      · 0-1     tinte del album en cada camara (su color)
uniform float uBandas;       // 5 firma      · 2-7     bandas en pantalla
uniform float uRespira;      // extra · 0-1  los listones abren y cierran en ola
uniform float uOnda;         // extra · 0-1  alturas desiguales que ondulan
uniform float uEncuadre;     // extra · 0-1  0 ventana · 1 camara completa en la banda
uniform float uLinea;        // extra · 0-0.01 linea crema en la orilla de cada ventana
uniform vec3  uColor1;       // paleta del album: amarillo
uniform vec3  uColor2;       // verde
uniform vec3  uColor3;       // azul
uniform vec3  uColor4;       // negro
uniform vec3  uColor5;       // rojo
uniform vec3  uBgColor;      // crema del album

out vec4 fragColor;

// -- tinte del album (ESTANDAR Rio Salvaje, igual en todos los layouts) ---------------------------
vec3 albumColor(int i) {
    i = i - (i / 5) * 5;
    if (i == 0) return uColor1;
    if (i == 1) return uColor2;
    if (i == 2) return uColor3;
    if (i == 3) return uColor4;
    return uColor5;
}
float albumLuma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
vec3 albumTint(vec3 cam, vec3 pc, float amt) {
    return mix(cam, pc * (0.35 + 1.3 * albumLuma(cam)), clamp(amt, 0.0, 1.0) * 0.75);
}

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

vec4 camAt(int idx, vec2 uv) {
    uv = clamp(uv, 0.0, 1.0);
    if (idx == 0) return textureLod(sTD2DInputs[0], uv, 0.0);
    if (idx == 1) return textureLod(sTD2DInputs[1], uv, 0.0);
    if (idx == 2) return textureLod(sTD2DInputs[2], uv, 0.0);
    if (idx == 3) return textureLod(sTD2DInputs[3], uv, 0.0);
    if (idx == 4) return textureLod(sTD2DInputs[4], uv, 0.0);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

float hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    int n = clamp(uCamCount, 2, 5);

    // coordenada de la persiana (inclinable alrededor del centro)
    vec2 p = vec2((uv.x - 0.5) * aspect, uv.y - 0.5);
    float a = clamp(uInclinacion, -0.4, 0.4);
    float yr = -sin(a) * p.x + cos(a) * p.y + 0.5;

    float nb = clamp(uBandas, 1.0, 9.0);
    float on = clamp(uOnda, 0.0, 1.0) * 0.3;
    float t0 = yr * nb - uPhase * 0.18;                       // las bandas suben
    float t = t0 + on * sin(t0 * 1.3 + uPhase * 0.5);         // derivada > 0: sin cruces
    float dtdy = nb * (1.0 + on * 1.3 * cos(t0 * 1.3 + uPhase * 0.5));
    float k = floor(t);
    float f = fract(t);
    float bandH = 1.0 / max(dtdy, 0.001);                     // alto de la banda (alto de pantalla = 1)

    // listones: cuanto de la banda es ventana (respira en ola, desfasado por banda)
    float ap = clamp(uApertura, 0.0, 1.0);
    ap -= clamp(uRespira, 0.0, 1.0) * 0.35 * (0.5 + 0.5 * sin(uPhase * 0.9 + k * 1.1));
    ap = clamp(ap, 0.05, 1.0);
    float hw = 0.5 * ap;
    float d = abs(f - 0.5);                                    // 0 centro de la banda · 0.5 orilla

    int idx = int(mod(k + 50.0, float(n)));
    vec3 col;
    if (d < hw) {
        // ventana: 0 = pedazo de la camara a pantalla completa · 1 = camara completa en la banda
        float v = (f - (0.5 - hw)) / max(ap, 0.0001);        // 0-1 dentro de la ventana
        float winH = bandH * ap;
        vec2 fill = applyCamFit(vec2(uv.x, v), uCamAspect, aspect / max(winH, 0.0001), uCamfit == 1 ? 0 : uCamfit);
        // un poco de deriva horizontal alterna por banda, para que no se vea como una sola imagen
        fill.x += 0.04 * sin(uPhase * 0.3 + k * 2.0) * (1.0 - uEncuadre * 0.5);
        vec2 cuv = mix(uv, fill, clamp(uEncuadre, 0.0, 1.0));
        vec3 cam = camAt(idx, cuv).rgb;
        col = albumTint(cam, albumColor(idx), uTint);
        // linea crema en la orilla de la ventana
        float lw = clamp(uLinea, 0.0, 0.02) / max(bandH, 0.0001);
        col = mix(col, uBgColor, step(hw - lw, d));
    } else {
        // liston: color del album, con un poco de luz de persiana (se aclara hacia arriba)
        // un liston = el espacio entre dos bandas: UN solo color (b = la orilla entre banda b-1 y b)
        float b = (f > 0.5) ? k + 1.0 : k;
        int ci = int(mod(b * 3.0 + 1.0 + floor(hash11(b + 3.0) * 2.0), 5.0));
        vec3 lc = albumColor(ci);
        float g = max(0.5 - hw, 0.0001);
        float s = (f > 0.5) ? 0.5 * (f - 0.5 - hw) / g : 0.5 + 0.5 * f / g;   // 0 abajo · 1 arriba
        col = lc * (0.93 + 0.12 * s);
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
