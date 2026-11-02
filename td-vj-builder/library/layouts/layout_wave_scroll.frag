// =============================================================
// WAVE SCROLL LAYOUT - LITTLE JESUS
// =============================================================
// Camaras en fila con scroll continuo + ola sinusoidal en eje
// perpendicular. Cada cam tiene offset de fase distinto para
// formar la onda. Wrap continuo: la cam que sale por un extremo
// reaparece por el otro.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;     // 2..5
uniform int   uCamfit;       // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;
uniform vec3  uBgColor;
uniform float uSpeed;        // 0.3   velocidad del scroll
uniform float uWaveAmt;      // 0.15  amplitud de la ola (fraccion)
uniform float uWaveFreq;     // 1.0   frecuencia de la ola
uniform float uCamSize;      // 0.35

out vec4 fragColor;

vec4 applyCamFit(int idx, vec2 uv, float cellAspect) {
    if (uCamfit == 0) {
        if (cellAspect > uCamAspect) {
            float s = uCamAspect / cellAspect;
            uv.y = uv.y * s + (1.0 - s) * 0.5;
        } else if (cellAspect < uCamAspect) {
            float s = cellAspect / uCamAspect;
            uv.x = uv.x * s + (1.0 - s) * 0.5;
        }
    } else if (uCamfit == 1) {
        if (cellAspect > uCamAspect) {
            float s = uCamAspect / cellAspect;
            float p = (1.0 - s) * 0.5;
            if (uv.x < p || uv.x > 1.0 - p) return vec4(0.0, 0.0, 0.0, 1.0);
            uv.x = (uv.x - p) / s;
        } else if (cellAspect < uCamAspect) {
            float s = cellAspect / uCamAspect;
            float p = (1.0 - s) * 0.5;
            if (uv.y < p || uv.y > 1.0 - p) return vec4(0.0, 0.0, 0.0, 1.0);
            uv.y = (uv.y - p) / s;
        }
    }
    if (idx == 0) return texture(sTD2DInputs[0], uv);
    if (idx == 1) return texture(sTD2DInputs[1], uv);
    if (idx == 2) return texture(sTD2DInputs[2], uv);
    if (idx == 3) return texture(sTD2DInputs[3], uv);
    if (idx == 4) return texture(sTD2DInputs[4], uv);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

void main() {
    vec2  uv = vUV.st;
    int   n  = clamp(uCamCount, 2, 5);

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);
    vec2  sz = vec2(uCamSize, uCamSize * frameAspect);

    float scroll = uTime * uSpeed;

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        float fi      = float(i);
        float basePos = fi / float(n);
        float waveY   = sin(uTime * uWaveFreq * 2.0 + fi * 1.257) * uWaveAmt;
        float rawX    = fract(basePos + scroll);

        // Dos copias para wrap continuo
        for (int k = 0; k < 2; k++) {
            float pos    = rawX - float(k);
            vec2  center = vec2(pos, 0.5 + waveY);
            vec2  minP   = center - sz * 0.5;
            vec2  maxP   = center + sz * 0.5;
            if (uv.x >= minP.x && uv.x <= maxP.x &&
                uv.y >= minP.y && uv.y <= maxP.y) {
                vec2 localUV = (uv - minP) / sz;
                col = applyCamFit(i, localUV, 1.0);
            }
        }
    }

    fragColor = col;
}
