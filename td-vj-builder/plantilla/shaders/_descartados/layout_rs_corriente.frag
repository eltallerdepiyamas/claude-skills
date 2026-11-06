// layout_rs_corriente.frag — "Trazos" · Little Jesus · Río Salvaje
// Las letras de "Río Salvaje" del flyer como cintas: cada cámara va dentro de un trazo vertical que
// ondula como río, con borde de color sólido (amarillo, azul, rojo, negro, verde), sobre crema.
// La imagen de la cámara sigue la curva del trazo (fluye con él).
// Cámaras = sTD2DInputs[0..4]; uCamCount (2–5) decide cuántos trazos se ven.

uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;       // 0 Fill · 1 Fit · 2 Stretch
uniform float uCamAspect;

uniform float uBorder;       // 1 intensidad · 0–1     grosor del borde de color del trazo
uniform float uSpeed;        // 2 velocidad  · 0–1.5   qué tan rápido corre la ondulación
uniform float uMeander;      // 3 distorsión · 0–1     amplitud de la curva de los trazos
uniform float uTint;         // 4 color      · 0–1     tiñe la cámara con el color de su trazo
uniform float uWidth;        // 5 firma      · 0.3–1   ancho de los trazos (1 = se tocan)
uniform float uFreq;         // curvas por alto de pantalla (0.5–4)
uniform vec3  uColor1;       // amarillo
uniform vec3  uColor2;       // azul
uniform vec3  uColor3;       // rojo
uniform vec3  uColor4;       // negro
uniform vec3  uColor5;       // verde
uniform vec3  uBgColor;      // crema del flyer

out vec4 fragColor;

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

// color del trazo de cada cámara, en el orden de las letras del flyer
vec3 strokeColor(int i) {
    if (i == 0) return uColor1;
    if (i == 1) return uColor2;
    if (i == 2) return uColor3;
    if (i == 3) return uColor4;
    return uColor5;
}

float luma(vec3 c) {
    return dot(c, vec3(0.2126, 0.7152, 0.0722));
}

void main() {
    vec2 uv = vUV.st;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    vec2 p = (uv - 0.5) * vec2(aspect, 1.0);    // alto = 1
    float px = 1.0 / uResolution.y;
    int n = clamp(uCamCount, 2, 5);
    float fn = float(n);
    float slot = aspect * 0.94 / fn;            // espacio horizontal de cada trazo
    float halfW = 0.5 * slot * clamp(uWidth, 0.2, 1.0);
    float amp = clamp(uMeander, 0.0, 1.0) * slot * 0.6;
    float k2 = max(uFreq, 0.1) * 3.14159;

    vec3 col = uBgColor;

    for (int k = 0; k < 5; k++) {
        if (k >= n) break;
        float fi = float(k);
        float cx0 = (fi - (fn - 1.0) * 0.5) * slot;
        float w = p.y * k2 + uTime * uSpeed * 1.5 + fi * 1.9;
        float cx = cx0 + amp * sin(w);
        float slope = amp * k2 * cos(w);
        float dx = (p.x - cx) / sqrt(1.0 + slope * slope);   // distancia perpendicular aprox.

        // sombra suave del trazo sobre la crema
        col *= 1.0 - 0.15 * (1.0 - smoothstep(halfW, halfW + 0.03, abs(dx - 0.008)));

        float ad = abs(dx);
        if (ad > halfW + 2.0 * px) continue;
        vec3 sc = strokeColor(k);
        float bw = halfW * mix(0.04, 0.45, clamp(uBorder, 0.0, 1.0));
        float inner = max(halfW - bw, px);

        // cámara dentro del trazo: x sigue la curva, y es la pantalla completa
        vec2 camUV = vec2(dx / (2.0 * inner) + 0.5, uv.y);
        vec3 cam = sampleCam(k, camUV, 2.0 * inner * uResolution.y, uResolution.y).rgb;
        cam = mix(cam, sc * (0.35 + 1.3 * luma(cam)), uTint * 0.75);

        vec3 strokeCol = mix(cam, sc, smoothstep(inner - px, inner + px, ad));
        col = mix(col, strokeCol, 1.0 - smoothstep(halfW - px, halfW + px, ad));
    }

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
