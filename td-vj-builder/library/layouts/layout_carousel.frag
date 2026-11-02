// =============================================================
// CAROUSEL LAYOUT — LITTLE JESUS
// =============================================================
// Camaras en fila horizontal. Hero centrada y mas grande.
// Avance manual (uScrollOffset) o automatico (uAutoScroll + uTime).
// Aspect preservado por celda.
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uHeroIndex;
uniform float uHeroScale;
uniform float uScrollOffset;
uniform float uAutoScroll;
uniform float uScrollSpeed;

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
    vec2 uv   = vUV.st;
    int  n    = clamp(uCamCount, 2, 5);
    int  hero = clamp(uHeroIndex, 0, n - 1);

    float autoOff = (uAutoScroll > 0.5) ? uTime * uScrollSpeed : 0.0;
    float scroll  = uScrollOffset + autoOff;

    float cellW = 1.0 / float(n);
    float virtX = uv.x - 0.5 + float(hero) * cellW + cellW * 0.5 + scroll;
    int   idx   = int(floor(virtX / cellW));

    if (idx < 0 || idx >= n) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    float localX = fract(virtX / cellW);
    float scale  = (idx == hero) ? max(uHeroScale, 0.1) : 1.0;

    // Sample con escala centrada
    float sx = (localX - 0.5) / scale + 0.5;
    float sy = (uv.y   - 0.5) / scale + 0.5;

    if (sx < 0.0 || sx > 1.0 || sy < 0.0 || sy > 1.0) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // Cell aspect: cellW (en frame) -> cellW * resX, full height resY
    float cellAspect = (cellW * uResolution.x) / uResolution.y;
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    fragColor = sampleCamFit(idx, vec2(sx, sy), cellAspect, camAspect);
}
