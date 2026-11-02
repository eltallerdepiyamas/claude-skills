// layout_rand_pulse.frag  -- Vertical breath con soft boundary blend
// =============================================================
// Cada columna pulsa en ESCALA VERTICAL con sin wave continuo.
// El UV.y se comprime/expande alrededor del centro -> efecto de
// "respiracion vertical". La AMPLITUD viene del peso del canal i.
//
// IMPORTANTE: para evitar lineas verticales visibles en las
// fronteras entre columnas (que pulsan a niveles de zoom distintos),
// se hace soft blend entre las 2 columnas mas cercanas usando
// smoothstep en la distancia al boundary.
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

// Calcula el UV pulsado de una columna dada, para un fragmento `uv`.
// Devuelve UV para samplear esa cam.
vec2 pulseUVFor(int colIdx, float colCx, vec2 uv, float colW) {
    float fi = float(colIdx);
    float w  = getWeight(colIdx);
    // Amp reducido para que adjacent cols no sean tan distintos
    float amp  = 0.10 + w * 0.20;
    // Frec por columna
    float freq = 0.35 + fi * 0.10;
    // Phase offset suave -> cols adyacentes pulsan similar
    float pulseY = 1.0 + sin(uTime * freq + fi * 0.60) * amp;

    float pulsedY = (uv.y - 0.5) / max(pulseY, 0.15) + 0.5;
    float localX  = (uv.x - colCx) / colW + 0.5;
    return vec2(localX, pulsedY);
}

void main() {
    vec2 uv = vUV.st;
    int  n  = clamp(uCamCount, 2, 5);
    float colW = 1.0 / float(n);

    // Encontrar las DOS columnas mas cercanas (con X wobble suave)
    int col1 = 0, col2 = 0;
    float dist1 = 999.0, dist2 = 999.0;
    float cx1 = 0.5, cx2 = 0.5;
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;
        float fii = float(i);
        float baseX = (fii + 0.5) * colW;
        float xWob = sin(uTime * 0.32 + fii * 1.27 + getWeight(i) * 3.14159)
                     * (0.20 * colW);
        float cx = baseX + xWob;
        float d  = abs(uv.x - cx);
        if (d < dist1) {
            dist2 = dist1; col2 = col1; cx2 = cx1;
            dist1 = d;     col1 = i;     cx1 = cx;
        } else if (d < dist2) {
            dist2 = d;     col2 = i;     cx2 = cx;
        }
    }

    // Samplear cada columna con su pulso propio
    float cellAspect = (colW * uResolution.x) / max(uResolution.y, 1.0);
    vec2 uv1 = pulseUVFor(col1, cx1, uv, colW);
    vec2 uv2 = pulseUVFor(col2, cx2, uv, colW);
    vec4 c1  = sampleCam(col1, uv1, cellAspect);
    vec4 c2  = sampleCam(col2, uv2, cellAspect);

    // Soft blend en el boundary: smoothstep en la diferencia de distancias.
    // Cerca del boundary (dist1 ~= dist2), blend ~ 0.5 -> mezcla equilibrada.
    // Lejos (dist1 << dist2), blend ~ 1.0 -> solo col1.
    float blendWidth = 0.015;
    float blend = smoothstep(0.0, blendWidth, dist2 - dist1);
    fragColor = mix(c2, c1, blend);
}
