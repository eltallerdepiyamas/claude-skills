// layout_mv_persianas.frag — "Persianas" · Little Jesus · Rio Salvaje
// Franjas (verticales o inclinadas) que se deslizan por la pantalla: unas son solidos de un
// color del album, otras son ventanas a una camara a PANTALLA COMPLETA (cada franja deja ver su
// pedazo de esa camara). Los anchos ondulan. Una linea crema separa las franjas.
// Camaras = sTD2DInputs[0..4].

uniform float uTime;
uniform float uPhase;        // reloj acumulado de la velocidad (knob 2, con su audio): no brinca
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;       // 0 Fill · 1 Fit · 2 Stretch
uniform float uCamAspect;

uniform float uSolidos;      // 1 intensidad · 0-1     cuantas franjas son de color solido (el resto: camaras)
uniform float uSpeed;        // 2 velocidad  · 0-1.5   las franjas se deslizan
uniform float uInclinacion;  // 3 distorsion · -0.6-0.6 inclinacion de las franjas
uniform float uTint;         // 4 color      · 0-1     tinte del album en cada camara (su color)
uniform float uFranjas;      // 5 firma      · 3-16    franjas en pantalla
uniform float uOnda;         // extra · 0-1     anchos desiguales que ondulan
uniform float uLinea;        // extra · 0-0.01  linea crema entre franjas (alto de pantalla = 1)
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

void main() {
    vec2 uv = vUV.st;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    int n = clamp(uCamCount, 2, 5);
    vec2 q = vec2(uv.x * aspect, uv.y);

    float s = q.x + (q.y - 0.5) * uInclinacion;
    float N = max(uFranjas, 1.0) / aspect;                 // franjas por unidad de alto
    float x = s * N + uPhase * 0.25;
    x += clamp(uOnda, 0.0, 1.0) * 0.35 * sin(x * 0.9 + uPhase * 0.6);   // sigue siendo creciente: sin cruces
    float k = floor(x);
    float f = fract(x);

    vec3 col;
    if (hash11(k + 17.0) < clamp(uSolidos, 0.0, 1.0)) {
        col = albumColor(int(mod(k, 5.0)));
    } else {
        int idx = int(mod(k, float(n)));
        vec3 cam = sampleCam(idx, uv, uResolution.x, uResolution.y).rgb;
        col = albumTint(cam, albumColor(idx), uTint);
    }
    // linea crema entre franjas
    float lw = clamp(uLinea, 0.0, 0.02) * N * 0.5;
    col = mix(col, uBgColor, 1.0 - step(lw, min(f, 1.0 - f)));
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
