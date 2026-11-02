// =============================================================
// BREATHING GRID LAYOUT — LITTLE JESUS
// =============================================================
// Grid uniforme cuyas celdas escalan ritmicamente (respiran).
// Cada celda tiene un desfase distinto -> sensacion de organismo
// vivo. Aspect preservado.
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform float uBreatheAmt;     // 0.05 amplitud de la escala (0..0.3)
uniform float uBreatheSpeed;   // 0.5 hz
uniform float uPhaseOffset;    // 1.5 radianes entre celdas
uniform vec3  uBgColor;

out vec4 fragColor;

// Modo Fill: la cam cubre toda la celda, recortando el excedente.
// Sin bandas negras cuando celda y cam tienen aspect distinto.
vec4 sampleCamFit(int idx, vec2 uv, float cellAspect, float camAspect) {
    if (cellAspect > camAspect) {
        float s = camAspect / cellAspect;
        uv.y = uv.y * s + (1.0 - s) * 0.5;
    } else if (cellAspect < camAspect) {
        float s = cellAspect / camAspect;
        uv.x = uv.x * s + (1.0 - s) * 0.5;
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
    int cellIdx = row * cols + col;

    if (cellIdx >= n) {
        fragColor = vec4(uBgColor, 1.0);
        return;
    }

    vec2 localUV = vec2(
        mod(uv.x, cellW) / cellW,
        1.0 - mod(1.0 - uv.y, cellH) / cellH
    );

    // Escala respirante centrada en la celda
    float phase = float(cellIdx) * uPhaseOffset;
    float scale = 1.0 + sin(uTime * uBreatheSpeed * 6.28318 + phase) * uBreatheAmt;
    vec2  scaledUV = (localUV - 0.5) / max(scale, 0.01) + 0.5;

    if (scaledUV.x < 0.0 || scaledUV.x > 1.0 ||
        scaledUV.y < 0.0 || scaledUV.y > 1.0) {
        fragColor = vec4(uBgColor, 1.0);
        return;
    }

    float cellAspect = (cellW * uResolution.x) / (cellH * uResolution.y);
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    fragColor = sampleCamFit(cellIdx, scaledUV, cellAspect, camAspect);
}
