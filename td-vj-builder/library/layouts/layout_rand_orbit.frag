// layout_rand_orbit.frag  -- Polar Orbit
// =============================================================
// Las N cams son tiles verticales orbitando lentamente alrededor
// del centro de la pantalla. Cada cam tiene su propio RADIO
// (peso del canal i) que cambia al presionar 0: algunas se
// acercan al centro, otras se alejan. La rotacion es continua
// e independiente del shuffle.
//
// Vibe: mandala kinetic, hipnotico.
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

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);

    // Tile grande — cubre la pantalla incluso con n=2.
    float ts = max(uTileSize, 0.1);
    float tileW = 0.55 * ts;
    float tileH = 0.95 * ts;

    // Velocidad de rotacion global (rad/s). Lenta para no marear.
    float orbSpeed = 0.18;
    // Radio maximo de la orbita
    float maxR = 0.34;

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        float fi = float(i);
        // Angulo: distribucion uniforme + rotacion global
        float angle = fi * (6.28318 / float(n)) + uTime * orbSpeed;
        // Radio individual de [0..maxR] desde el peso
        float radius = getWeight(i) * maxR;

        // Compensamos aspect para que la orbita sea circular en pantalla
        vec2 center = vec2(
            0.5 + cos(angle) * radius,
            0.5 + sin(angle) * radius * frameAspect
        );

        vec2 size = vec2(tileW, tileH);
        vec2 minP = center - size * 0.5;
        vec2 maxP = center + size * 0.5;

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
