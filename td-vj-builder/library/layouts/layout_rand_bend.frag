// layout_rand_bend.frag  -- Flag in wind
// =============================================================
// Familia rand_wave: pero en lugar de scroll vertical, el UV.x de
// cada columna se desplaza segun una sin wave que VIAJA por Y.
// Visualmente: el contenido de cada cam se ondula horizontalmente
// como una bandera. La AMPLITUD del bend viene del peso del canal i.
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

    // Closest-column con X wobble (sin gaps lateral)
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

    // Amplitud del bend horizontal: [0.04, 0.30]
    float amp  = 0.04 + w * 0.26;
    // Frecuencia espacial: cuantas "olas" caben en una columna verticalmente
    float fSpa = 3.0 + fi * 0.7;
    // Frecuencia temporal: velocidad de propagacion de la onda
    float fTime = 0.40 + fi * 0.15;

    // X bend: desplazamiento horizontal que recorre Y
    float xBend = sin(uv.y * fSpa + uTime * fTime + fi * 1.27) * amp;

    vec2 bentUV = vec2(fract(localX + xBend), uv.y);

    float cellAspect = (colW * uResolution.x) / max(uResolution.y, 1.0);
    fragColor = sampleCam(col, bentUV, cellAspect);
}
