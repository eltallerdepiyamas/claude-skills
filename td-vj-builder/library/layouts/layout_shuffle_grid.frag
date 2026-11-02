// =============================================================
// SHUFFLE GRID LAYOUT — LITTLE JESUS
// =============================================================
// Grid como gridwall pero las asignaciones cam->celda CICLAN con
// el tiempo. Cada uCycleTime segundos las cams rotan a la celda
// vecina con un crossfade suave (smoothstep en el ultimo 20%).
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform float uCycleTime;   // 4.0 seg por shift
uniform vec3  uBgColor;

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
    int cellIdx = row * cols + col;

    if (cellIdx >= n) {
        fragColor = vec4(uBgColor, 1.0);
        return;
    }

    vec2 localUV = vec2(
        mod(uv.x, cellW) / cellW,
        1.0 - mod(1.0 - uv.y, cellH) / cellH
    );

    // Aspect ratios para letterbox
    float cellAspect = (cellW * uResolution.x) / (cellH * uResolution.y);
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    // Rotacion cam-cell con crossfade
    float t = uTime / max(uCycleTime, 0.1);
    int   shift = int(mod(floor(t), float(n)));
    float frac  = fract(t);

    int camA = (cellIdx + shift)     % n;
    int camB = (cellIdx + shift + 1) % n;

    float mixF = smoothstep(0.8, 1.0, frac);
    vec4 a = sampleCamFit(camA, localUV, cellAspect, camAspect);
    vec4 b = sampleCamFit(camB, localUV, cellAspect, camAspect);

    fragColor = mix(a, b, mixF);
}
