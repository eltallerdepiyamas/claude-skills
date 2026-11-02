// layout_rand_wave.frag  -- Wave UV scroll
// =============================================================
// N columnas verticales que cubren toda la pantalla. El UV vertical
// de cada cam tiene un SCROLL CONTINUO sinusoidal: la ola viaja por
// las columnas con desfase por indice. La AMPLITUD del scroll viene
// del peso del canal i (cambia al presionar 0).
// Inspirado en layout_wave_scroll del .md.
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

    // Closest-column con X wobble (voronoi, sin gaps lateral)
    int col = 0;
    float bestDist = 999.0;
    float bestCx = 0.5;
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;
        float fii = float(i);
        float baseX = (fii + 0.5) * colW;
        float xWob = sin(uTime * 0.32 + fii * 1.27 + getWeight(i) * 3.14159)
                     * (0.30 * colW);
        float cx = baseX + xWob;
        float d  = abs(uv.x - cx);
        if (d < bestDist) {
            bestDist = d;
            col = i;
            bestCx = cx;
        }
    }
    float localX = (uv.x - bestCx) / colW + 0.5;

    float fi = float(col);
    float w  = getWeight(col);

    // Amplitud del scroll vertical: [0.05, 0.5] segun peso
    float amp  = 0.05 + w * 0.45;
    float freq = 0.35 + fi * 0.18;

    // Y scroll con sin wave viajera + wrap (fract)
    float yOff   = sin(uTime * freq + fi * 1.27) * amp;
    vec2  colUV  = vec2(localX, fract(uv.y + yOff));

    float cellAspect = (colW * uResolution.x) / max(uResolution.y, 1.0);
    fragColor = sampleCam(col, colUV, cellAspect);
}
