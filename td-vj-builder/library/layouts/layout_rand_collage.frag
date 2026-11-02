// layout_rand_collage.frag  -- 2D Scatter
// =============================================================
// 5 cams dispersas en 2D con tile en aspect 16:9 (matchea uCamAspect)
// para que ocupen el maximo de pantalla sin distorsion. Las cams se
// pueden traslapar (last-cam-wins).
//
// Posicion:
//   X = weight[i]              (cambia con shuffle)
//   Y = hash(weight[i], i)     (cambia con shuffle pero distinto a X)
// Plus wobble continuo subtle con uTime para que nunca quede estatico.
//
// uTileSize escala las tiles para cubrir mas (o menos) pantalla.
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
    vec2  uv = vUV.st;
    int   n  = clamp(uCamCount, 2, 5);

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);

    // Tile grande para cubrir pantalla incluso si los 5 quedan agrupados.
    // Alto = ancho * frameAspect / camAspect -> rect en PANTALLA matchea cam aspect.
    float ts    = max(uTileSize, 0.1);
    float tileW = 0.70 * ts;
    float tileH = tileW * frameAspect / max(uCamAspect, 0.001);

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        float fi = float(i);
        float w  = getWeight(i);

        // Posicion shuffle-driven en 2D
        float cx = w;
        float cy = fract(w * 4.713 + fi * 0.731);

        // Wobble continuo: fases distintas por cam, distintas en X/Y
        cx += sin(uTime * 0.31 + fi * 1.27) * 0.04;
        cy += cos(uTime * 0.43 + fi * 1.51) * 0.04;

        vec2 center = vec2(cx, cy);
        vec2 size   = vec2(tileW, tileH);
        vec2 minP   = center - size * 0.5;
        vec2 maxP   = center + size * 0.5;

        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV     = (uv - minP) / size;
            float cellAspect = (tileW * uResolution.x) /
                               max(tileH * uResolution.y, 1.0);
            col = sampleCam(i, localUV, cellAspect);
        }
    }

    fragColor = col;
}
