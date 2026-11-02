// layout_rand_flow.frag  -- Waterfall Flow
// =============================================================
// N columnas full-screen. Cada columna tiene scroll Y CONTINUO
// (wrap). Las columnas pares fluyen hacia abajo, las impares hacia
// arriba — efecto de cascada en direcciones opuestas. La VELOCIDAD
// de cada columna viene del peso (al presionar 0 cambia el ritmo
// de cada cam: unas paran, otras se aceleran).
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

    // Closest-column con X wobble suave (la flow ya da mucho movimiento)
    int col = 0;
    float bestDist = 999.0;
    float bestCx = 0.5;
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;
        float fii = float(i);
        float baseX = (fii + 0.5) * colW;
        float xWob = sin(uTime * 0.25 + fii * 1.27 + getWeight(i) * 3.14159)
                     * (0.20 * colW);
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

    // Velocidad del flow: [0.05, 0.50] -- algunas casi quietas, otras rapidas
    float speed = 0.05 + w * 0.45;
    // Direccion alterna: pares hacia abajo, impares hacia arriba
    float dir = mod(fi, 2.0) < 0.5 ? 1.0 : -1.0;
    // Y scroll continuo con wrap
    float yScroll = uTime * speed * dir + fi * 0.21;

    vec2 flowUV = vec2(localX, fract(uv.y + yScroll));

    float cellAspect = (colW * uResolution.x) / max(uResolution.y, 1.0);
    fragColor = sampleCam(col, flowUV, cellAspect);
}
