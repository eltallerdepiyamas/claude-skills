// =============================================================
// FLOAT CHAOS LAYOUT - LITTLE JESUS
// =============================================================
// Camaras flotando libremente con trayectorias sinusoidales
// independientes (frecuencias y fases distintas por cam).
// Vibe: hipnotico organico tipo burbujas.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;     // 2..5
uniform int   uCamfit;       // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;    // aspect ratio w/h de la cam fuente
uniform vec3  uBgColor;
uniform float uSpeed;        // 0.2  velocidad base
uniform float uSpread;       // 0.6  alejamiento del centro
uniform float uCamSize;      // 0.5  fraccion del ancho

out vec4 fragColor;

vec4 applyCamFit(int idx, vec2 uv, float cellAspect) {
    if (uCamfit == 0) {
        if (cellAspect > uCamAspect) {
            float s = uCamAspect / cellAspect;
            uv.y = uv.y * s + (1.0 - s) * 0.5;
        } else if (cellAspect < uCamAspect) {
            float s = cellAspect / uCamAspect;
            uv.x = uv.x * s + (1.0 - s) * 0.5;
        }
    } else if (uCamfit == 1) {
        if (cellAspect > uCamAspect) {
            float s = uCamAspect / cellAspect;
            float p = (1.0 - s) * 0.5;
            if (uv.x < p || uv.x > 1.0 - p) return vec4(0.0, 0.0, 0.0, 1.0);
            uv.x = (uv.x - p) / s;
        } else if (cellAspect < uCamAspect) {
            float s = cellAspect / uCamAspect;
            float p = (1.0 - s) * 0.5;
            if (uv.y < p || uv.y > 1.0 - p) return vec4(0.0, 0.0, 0.0, 1.0);
            uv.y = (uv.y - p) / s;
        }
    }
    if (idx == 0) return texture(sTD2DInputs[0], uv);
    if (idx == 1) return texture(sTD2DInputs[1], uv);
    if (idx == 2) return texture(sTD2DInputs[2], uv);
    if (idx == 3) return texture(sTD2DInputs[3], uv);
    if (idx == 4) return texture(sTD2DInputs[4], uv);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

// Frecuencias y fases por cam (del spec L9 del CLAUDE.md)
float fx(int i) {
    if (i == 0) return 0.7;
    if (i == 1) return 1.1;
    if (i == 2) return 0.6;
    if (i == 3) return 1.4;
    return 0.9;
}
float fy(int i) {
    if (i == 0) return 0.5;
    if (i == 1) return 0.8;
    if (i == 2) return 1.3;
    if (i == 3) return 0.4;
    return 1.1;
}
float px(int i) {
    if (i == 0) return 0.0;
    if (i == 1) return 2.1;
    if (i == 2) return 4.2;
    if (i == 3) return 1.5;
    return 3.3;
}
float py(int i) {
    if (i == 0) return 1.0;
    if (i == 1) return 0.7;
    if (i == 2) return 2.5;
    if (i == 3) return 3.8;
    return 1.2;
}

void main() {
    vec2  uv = vUV.st;
    int   n  = clamp(uCamCount, 2, 5);

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);
    // Cada cam es cuadrada en pantalla
    vec2  sz = vec2(uCamSize, uCamSize * frameAspect);

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        float cx = sin(uTime * uSpeed * fx(i) + px(i)) * uSpread * 0.5;
        float cy = cos(uTime * uSpeed * fy(i) + py(i)) * uSpread * 0.5;
        vec2  center = vec2(0.5 + cx, 0.5 + cy);

        vec2 minP = center - sz * 0.5;
        vec2 maxP = center + sz * 0.5;
        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV = (uv - minP) / sz;
            col = applyCamFit(i, localUV, 1.0);
        }
    }

    fragColor = col;
}
