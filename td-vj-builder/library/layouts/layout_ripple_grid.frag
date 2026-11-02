// =============================================================
// RIPPLE GRID LAYOUT - LITTLE JESUS
// =============================================================
// Grid uniforme de camaras donde el UV local de cada celda se
// distorsiona con una onda sinusoidal: cada columna pulsa en Y
// con desfase distinto.
//
// Layout por uCamCount:
//   2 -> 2x1   3 -> 2x2 (ultima vacia)
//   4 -> 2x2   5 -> 3x2 (ultima vacia)
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform float uSpeed;          // 0.5   velocidad de la onda
uniform float uRippleAmt;      // 0.05  amplitud del desplazamiento UV
uniform float uRippleFreq;     // 1.5   desfase por columna
uniform int   uCamfit;         // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;      // aspect w/h de la cam fuente
uniform vec3  uBgColor;

out vec4 fragColor;

vec2 applyCamFit(vec2 cellUV, float camAspect, float cellAspect, int fitMode) {
    if (fitMode == 2) return cellUV;
    float scaleX = 1.0;
    float scaleY = 1.0;
    float ratio = cellAspect / camAspect;
    if (fitMode == 0) {
        if (ratio > 1.0) { scaleY = ratio; }
        else             { scaleX = 1.0 / ratio; }
    } else {
        if (ratio > 1.0) { scaleX = 1.0 / ratio; }
        else             { scaleY = ratio; }
    }
    vec2 c = cellUV - 0.5;
    c.x /= scaleX;
    c.y /= scaleY;
    return c + 0.5;
}

vec4 sampleCam(int idx, vec2 localUV, float cellAspect) {
    vec2 fitUV = applyCamFit(localUV, uCamAspect, cellAspect, uCamfit);
    if (uCamfit != 1) {
        fitUV = clamp(fitUV, 0.0, 1.0);
    } else if (fitUV.x < 0.0 || fitUV.x > 1.0 ||
               fitUV.y < 0.0 || fitUV.y > 1.0) {
        return vec4(uBgColor, 1.0);
    }
    if (idx == 0) return texture(sTD2DInputs[0], fitUV);
    if (idx == 1) return texture(sTD2DInputs[1], fitUV);
    if (idx == 2) return texture(sTD2DInputs[2], fitUV);
    if (idx == 3) return texture(sTD2DInputs[3], fitUV);
    if (idx == 4) return texture(sTD2DInputs[4], fitUV);
    return vec4(uBgColor, 1.0);
}

void main() {
    vec2 uv = vUV.st;
    int  n  = clamp(uCamCount, 2, 5);

    int cols = (n <= 2) ? 2 : ((n <= 4) ? 2 : 3);
    int rows = (n <= 2) ? 1 : 2;

    float cellW = 1.0 / float(cols);
    float cellH = 1.0 / float(rows);

    int col = int(uv.x / cellW);
    int row = int((1.0 - uv.y) / cellH);
    int idx = row * cols + col;

    if (idx >= n) {
        fragColor = vec4(uBgColor, 1.0);
        return;
    }

    // UV local dentro de la celda
    vec2 localUV = vec2(
        mod(uv.x, cellW) / cellW,
        1.0 - mod(1.0 - uv.y, cellH) / cellH
    );

    // Distorsion en Y segun columna (formula del .md)
    localUV.y += sin(uTime * uSpeed + float(col) * uRippleFreq) * uRippleAmt;

    float cellAspect = (cellW * uResolution.x) / max(cellH * uResolution.y, 1.0);
    fragColor = sampleCam(idx, localUV, cellAspect);
}
