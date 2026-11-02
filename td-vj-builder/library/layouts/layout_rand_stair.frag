// layout_rand_stair.frag  -- Staircase
// =============================================================
// N columnas verticales con alturas formando una ESCALERA: la
// columna i tiene una altura base = (i+1)/N, modulada por el
// peso aleatorio del canal i. Genera una escalera ascendente
// con variaciones por columna en cada shuffle.
// Anclaje al borde inferior.
// =============================================================

uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;
uniform float uCamAspect;
uniform vec3  uBgColor;

out vec4 fragColor;

vec2 applyCamFit(vec2 cellUV, float camAspect, float cellAspect, int fitMode) {
    if (fitMode == 2) return cellUV;
    float scaleX = 1.0, scaleY = 1.0;
    float ratio = cellAspect / camAspect;
    if (fitMode == 0) {
        if (ratio > 1.0) scaleY = ratio;
        else scaleX = 1.0 / ratio;
    } else {
        if (ratio > 1.0) scaleX = 1.0 / ratio;
        else scaleY = ratio;
    }
    vec2 c = cellUV - 0.5;
    c.x /= scaleX; c.y /= scaleY;
    return c + 0.5;
}

vec4 sampleCam(int idx, vec2 luv, float cellAspect) {
    vec2 fitUV = applyCamFit(luv, uCamAspect, cellAspect, uCamfit);
    if (uCamfit != 1) fitUV = clamp(fitUV, 0.0, 1.0);
    else if (fitUV.x < 0.0 || fitUV.x > 1.0 || fitUV.y < 0.0 || fitUV.y > 1.0)
        return vec4(uBgColor, 1.0);
    if (idx == 0) return texture(sTD2DInputs[0], fitUV);
    if (idx == 1) return texture(sTD2DInputs[1], fitUV);
    if (idx == 2) return texture(sTD2DInputs[2], fitUV);
    if (idx == 3) return texture(sTD2DInputs[3], fitUV);
    if (idx == 4) return texture(sTD2DInputs[4], fitUV);
    return vec4(uBgColor, 1.0);
}

float getWeight(int i) {
    float u = (float(i) + 0.5) / 5.0;
    return clamp(texture(sTD2DInputs[5], vec2(u, 0.5)).r, 0.0, 1.0);
}

void main() {
    vec2 uv = vUV.st;
    int  n  = clamp(uCamCount, 2, 5);

    float colW = 1.0 / float(n);

    // Lookup simple sin wobble: columnas estables, alturas ascendentes
    int col = int(uv.x / colW);
    if (col >= n) {
        fragColor = vec4(uBgColor, 1.0);
        return;
    }

    // Altura base ascendente: col 0 = 1/N, col N-1 = 1.0
    float baseH = (float(col) + 1.0) / float(n);
    // Modulacion suave en [0.7, 1.0] -- preserva orden ascendente
    float mod_  = 0.7 + getWeight(col) * 0.3;
    float h     = clamp(baseH * mod_, 0.1, 1.0);

    if (uv.y > h) {
        fragColor = vec4(uBgColor, 1.0);
        return;
    }

    float localX = (uv.x - float(col) * colW) / colW;
    vec2 localUV = vec2(localX, uv.y / h);
    float cellAspect = (colW * uResolution.x) / max(h * uResolution.y, 1.0);
    fragColor = sampleCam(col, localUV, cellAspect);
}
