// layout_rand_drift.frag  -- Horizontal Drifting Tiles
// =============================================================
// 5 tiles verticales altas (portrait) que se deslizan
// HORIZONTALMENTE por la pantalla. Cada tile tiene un X target
// aleatorio (peso del canal i) y un wobble vertical sutil
// continuo (sin(uTime)). Las tiles pueden traslaparse cuando
// los X targets se acercan — efecto de capas que se cruzan.
//
// Al presionar 0: nuevos X targets, Lag CHOP suaviza el deslizamiento.
// =============================================================

uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;
uniform float uCamAspect;
uniform vec3  uBgColor;
uniform float uTileSize;     // multiplicador del tamano del tile (1.0 = default)

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

    // Tile grande para que siempre cubra toda la pantalla.
    // uTileSize escala (1.0 = default ya generoso, 2.5 = enorme).
    float ts = max(uTileSize, 0.1);
    float tileW = 0.55 * ts;
    float tileH = 1.20 * ts;   // mayor a 1.0 -> sobresale del frame, sin gaps en Y

    vec4 col = vec4(uBgColor, 1.0);

    // Pintamos en orden 0..n-1: la ultima cam dentro del fragmento gana.
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        // X target del tile (de weights). El Lag CHOP lo suaviza.
        float cx = getWeight(i);
        // Wobble vertical sutil para que no sea estatico
        float fi = float(i);
        float cy = 0.5 + sin(uTime * 0.45 + fi * 1.27) * 0.06;

        vec2  center = vec2(cx, cy);
        vec2  size   = vec2(tileW, tileH);
        vec2  minP   = center - size * 0.5;
        vec2  maxP   = center + size * 0.5;

        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV = (uv - minP) / size;
            float cellAspect = (tileW * uResolution.x) /
                               max(tileH * uResolution.y, 1.0);
            col = sampleCam(i, localUV, cellAspect);
        }
    }

    fragColor = col;
}
