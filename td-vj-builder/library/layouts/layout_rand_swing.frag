// layout_rand_swing.frag  -- Pendulum Swing
// =============================================================
// 5 tiles VERTICALES (full height) que cuelgan del tope y se
// balancean HORIZONTALMENTE como pendulos. Cada tile tiene
// frecuencia escalonada y amplitud del swing controlada por el
// peso del canal i (cambia al presionar 0).
// Inspirado en layout_pendulum del .md.
// =============================================================

uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;
uniform float uCamAspect;
uniform vec3  uBgColor;
uniform float uTileSize;     // multiplicador del tamano del tile

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

    float ts    = max(uTileSize, 0.1);
    float tileW = 0.40 * ts;
    float tileH = 1.20 * ts;  // mayor a 1.0 -> siempre cubre Y

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        float fi = float(i);
        float w  = getWeight(i);

        // Posicion base X: distribuida
        float baseX = (fi + 0.5) / float(n);

        // Amplitud del swing: [0.10, 0.45]
        float amp = 0.10 + w * 0.35;
        // Frecuencia escalonada (cada pendulo distinto)
        float freq = 0.4 + fi * 0.13;
        float phase = fi * 1.26;

        float swingX = baseX + sin(uTime * freq + phase) * amp;
        // Wobble vertical sutil para que no quede rigido
        float wobbleY = sin(uTime * freq * 0.5 + phase) * 0.03;

        vec2 center = vec2(swingX, 0.5 + wobbleY);
        vec2 size   = vec2(tileW, tileH);
        vec2 minP   = center - size * 0.5;
        vec2 maxP   = center + size * 0.5;

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
