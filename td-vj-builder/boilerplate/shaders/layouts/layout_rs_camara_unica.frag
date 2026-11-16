// layout_rs_camara_unica.frag — "Cámara única" · Little Jesus · Río Salvaje
// Una sola cámara (la que elija "Cámara única" en la pestaña Camaras de escena_modular, Cam 1–6).
//   Figura 0   -> pantalla completa con marco de color del álbum
//   Figura 1-5 -> la cámara dentro de UNA figura grande al centro (círculo, cuadrado, triángulo,
//                 medio disco, rombo) sobre crema, con un bloque del color desplazado detrás
// Vaivén lento, acercamiento y duotono en los dos modos. Cámara = sTD2DInputs[0] (SLOT_UNICA).

uniform float uTime;
uniform float uPhase;        // reloj acumulado de la velocidad (knob 2, con su audio): no brinca
uniform vec2  uResolution;
uniform int   uCamCount;     // no se usa: siempre 1 cámara
uniform int   uCamfit;       // 0 Fill · 1 Fit · 2 Stretch
uniform float uCamAspect;

uniform float uFrame;        // 1 intensidad · 0–1     marco (Figura 0) / desplazamiento del bloque de color (Figura 1-5)
uniform float uDrift;        // 2 velocidad  · 0–1     vaivén lento de la toma (tipo Ken Burns)
uniform float uZoom;         // 3 distorsión · 1–1.6   acercamiento
uniform float uTint;         // 4 color      · 0–1     duotono con el color del marco
uniform float uShape;        // 5 firma      · 0–5     0 pantalla completa · 1 círculo · 2 cuadrado ·
                             //                        3 triángulo · 4 medio disco · 5 rombo
uniform float uHue;          // extra · 0–1   color: amarillo → verde → azul → negro → rojo
uniform float uSize;         // extra · 0.25–0.48  tamaño de la figura (alto de pantalla = 1)
uniform vec3  uColor1;       // amarillo
uniform vec3  uColor2;       // verde
uniform vec3  uColor3;       // azul
uniform vec3  uColor4;       // negro
uniform vec3  uColor5;       // rojo
uniform vec3  uBgColor;      // crema (fondo de las figuras y luz del duotono)

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

vec3 pal(float i) {
    i = mod(floor(i), 5.0);
    if (i < 0.5) return uColor1;
    if (i < 1.5) return uColor2;
    if (i < 2.5) return uColor3;
    if (i < 3.5) return uColor4;
    return uColor5;
}

float luma(vec3 c) {
    return dot(c, vec3(0.2126, 0.7152, 0.0722));
}

mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

float sdTri(vec2 p, float r) {
    const float k = 1.7320508;
    p.x = abs(p.x) - r;
    p.y = p.y + r / k;
    if (p.x + k * p.y > 0.0) p = vec2(p.x - k * p.y, -k * p.x - p.y) / 2.0;
    p.x -= clamp(p.x, -2.0 * r, 0.0);
    return -length(p) * sign(p.y);
}

// figura i (0 círculo · 1 cuadrado · 2 triángulo · 3 medio disco · 4 rombo) de "radio" s
float sdShape(int i, vec2 p, float s) {
    if (i == 0) return length(p) - s;
    if (i == 1) return sdBox(p, vec2(s * 0.86));
    if (i == 2) return sdTri(p + vec2(0.0, s * 0.18), s * 1.1);
    if (i == 3) return max(length(p + vec2(0.0, s * 0.35)) - s * 1.1, -(p.y + s * 0.35));
    return sdBox(rot(0.785398) * p, vec2(s * 0.74));
}

// la toma con acercamiento y vaivén, en una celda de aspecto cellAspect
vec3 camera(vec2 local, float cellAspect) {
    float t = uPhase;
    float z = max(uZoom, 1.0);
    vec2 drift = (z - 1.0) * 0.5 * vec2(sin(t * 0.7), cos(t * 0.53));
    vec2 zuv = (local - 0.5) / z + 0.5 + drift;
    vec2 fitUV = applyCamFit(zuv, uCamAspect, cellAspect, uCamfit);
    if (uCamfit != 1) {
        return texture(sTD2DInputs[0], clamp(fitUV, 0.0, 1.0)).rgb;
    }
    if (fitUV.x < 0.0 || fitUV.x > 1.0 || fitUV.y < 0.0 || fitUV.y > 1.0) {
        return vec3(0.0);
    }
    return texture(sTD2DInputs[0], fitUV).rgb;
}

vec3 duotone(vec3 cam, vec3 fc) {
    return albumTint(cam, fc, uTint);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    float px = 1.0 / uResolution.y;
    vec3 fc = pal(clamp(uHue, 0.0, 0.999) * 5.0);
    vec2 p = (uv - 0.5) * vec2(aspect, 1.0);    // alto = 1
    int fig = int(floor(clamp(uShape, 0.0, 5.0) + 0.5));

    vec3 col;
    if (fig == 0) {
        // pantalla completa con marco (mismo grosor en x y y)
        float fw = clamp(uFrame, 0.0, 1.0) * 0.09;
        vec2 halfIn = vec2(aspect * 0.5 - fw, 0.5 - fw);
        vec2 d = abs(p) - halfIn;
        float outside = smoothstep(-px, px, max(d.x, d.y));
        vec2 local = p / (2.0 * halfIn) + 0.5;
        vec3 cam = duotone(camera(local, halfIn.x / halfIn.y), fc);
        col = mix(cam, fc, outside);
    } else {
        // una figura grande al centro sobre crema, con bloque de color desplazado detras
        int shp = fig - 1;
        float s = clamp(uSize, 0.15, 0.48);
        float t = uPhase;
        vec2 c = vec2(0.0, 0.02 * sin(t * 1.1));              // flota apenas
        vec2 off = vec2(0.6, -0.6) * s * 0.35 * clamp(uFrame, 0.0, 1.0);
        col = uBgColor;
        float db = sdShape(shp, p - c - off, s);
        col = mix(col, fc, 1.0 - smoothstep(-px, px, db));
        float d = sdShape(shp, p - c, s);
        float m = 1.0 - smoothstep(-px, px, d);
        vec2 local = (p - c) / (2.0 * s * 1.15) + 0.5;        // la figura en un cuadrado
        vec3 cam = duotone(camera(local, 1.0), fc);
        col = mix(col, cam, m);
    }

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
