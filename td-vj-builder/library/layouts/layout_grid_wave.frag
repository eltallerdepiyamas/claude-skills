// =============================================================
// GRID WAVE LAYOUT — LITTLE JESUS
// =============================================================
// Grid uniforme con movimiento ondulatorio sutil en Y por celda.
// Aspect preservado.
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform float uWaveAmt;
uniform float uWaveSpeed;
uniform float uPhaseOffset;

out vec4 fragColor;

vec4 sampleCamFit(int idx, vec2 uv, float cellAspect, float camAspect) {
    if (cellAspect > camAspect) {
        float s = camAspect / cellAspect;
        float p = (1.0 - s) * 0.5;
        if (uv.x < p || uv.x > 1.0 - p) return vec4(0.0, 0.0, 0.0, 1.0);
        uv.x = (uv.x - p) / s;
    } else if (cellAspect < camAspect) {
        float s = cellAspect / camAspect;
        float p = (1.0 - s) * 0.5;
        if (uv.y < p || uv.y > 1.0 - p) return vec4(0.0, 0.0, 0.0, 1.0);
        uv.y = (uv.y - p) / s;
    }
    if (idx == 0) return texture(sTD2DInputs[0], uv);
    if (idx == 1) return texture(sTD2DInputs[1], uv);
    if (idx == 2) return texture(sTD2DInputs[2], uv);
    if (idx == 3) return texture(sTD2DInputs[3], uv);
    if (idx == 4) return texture(sTD2DInputs[4], uv);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

void main() {
    vec2 uv = vUV.st;
    int  n  = clamp(uCamCount, 2, 5);

    int cols = (n == 2) ? 2 : ((n <= 4) ? 2 : 3);
    int rows = (n == 2) ? 1 : 2;

    float cellW = 1.0 / float(cols);
    float cellH = 1.0 / float(rows);

    int col = int(uv.x / cellW);
    int row = int((1.0 - uv.y) / cellH);
    int idx = row * cols + col;

    vec2 localUV = vec2(
        mod(uv.x, cellW) / cellW,
        1.0 - mod(1.0 - uv.y, cellH) / cellH
    );

    float phase = float(idx) * uPhaseOffset;
    float wave  = sin(uTime * uWaveSpeed + phase) * uWaveAmt;
    localUV.y = clamp(localUV.y + wave, 0.0, 1.0);

    if (idx >= n) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    float cellAspect = (cellW * uResolution.x) / (cellH * uResolution.y);
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    fragColor = sampleCamFit(idx, localUV, cellAspect, camAspect);
}
