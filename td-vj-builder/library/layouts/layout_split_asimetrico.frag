// =============================================================
// SPLIT ASIMETRICO LAYOUT - LITTLE JESUS
// =============================================================
// Division asimetrica con jerarquia visual. Cam 0 grande,
// resto en franja secundaria subdividida segun uCamCount.
// uGap inserta separacion (uBgColor) entre regiones.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform float uSplitRatio;   // 0.6   ratio del lado grande (0.1..0.9)
uniform int   uOrientation;  // 0=vertical, 1=horizontal
uniform float uGap;          // 0.004 separacion entre regiones (UV)
uniform int   uCamfit;       // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;    // aspect w/h de la cam fuente
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
    vec2  uv = vUV.st;
    int   n  = clamp(uCamCount, 2, 5);
    float r  = clamp(uSplitRatio, 0.1, 0.9);

    bool vertical = (uOrientation == 0);
    vec2 uv2      = vertical ? uv : vec2(uv.y, 1.0 - uv.x);
    vec2 frameRes = vertical ? uResolution : uResolution.yx;

    vec4 outCol = vec4(uBgColor, 1.0);

    // Gap vertical entre el lado grande y la franja secundaria
    if (uv2.x > r - uGap * 0.5 && uv2.x < r + uGap * 0.5) {
        fragColor = vec4(uBgColor, 1.0);
        return;
    }

    if (uv2.x < r) {
        // Lado grande: cam 0
        vec2  localUV    = vec2(uv2.x / r, uv2.y);
        float cellAspect = (r * frameRes.x) / max(frameRes.y, 1.0);
        outCol = sampleCam(0, localUV, cellAspect);
    } else {
        float rx = (uv2.x - r) / max(1.0 - r, 0.001);
        float ry = uv2.y;
        int   subIdx;
        vec2  subUV;
        float subAspect;
        float secW = (1.0 - r) * frameRes.x;

        if (n == 2) {
            subIdx    = 1;
            subUV     = vec2(rx, ry);
            subAspect = secW / max(frameRes.y, 1.0);
        }
        else if (n == 3) {
            // gap horizontal entre las 2 subceldas verticales
            if (abs(ry - 0.5) < uGap * 0.5) { fragColor = vec4(uBgColor, 1.0); return; }
            if (ry > 0.5) { subIdx = 1; subUV = vec2(rx, (ry - 0.5) * 2.0); }
            else          { subIdx = 2; subUV = vec2(rx,  ry * 2.0); }
            subAspect = secW / max(0.5 * frameRes.y, 1.0);
        }
        else if (n == 4) {
            // gaps entre las 3 subceldas
            if (abs(ry - 1.0/3.0) < uGap * 0.5 || abs(ry - 2.0/3.0) < uGap * 0.5) {
                fragColor = vec4(uBgColor, 1.0); return;
            }
            if      (ry > 2.0/3.0) { subIdx = 1; subUV = vec2(rx, (ry - 2.0/3.0) * 3.0); }
            else if (ry > 1.0/3.0) { subIdx = 2; subUV = vec2(rx, (ry - 1.0/3.0) * 3.0); }
            else                   { subIdx = 3; subUV = vec2(rx,  ry * 3.0); }
            subAspect = secW / max((1.0/3.0) * frameRes.y, 1.0);
        }
        else { // n == 5: grid 2x2 en la franja secundaria
            if (abs(rx - 0.5) < uGap * 0.5 || abs(ry - 0.5) < uGap * 0.5) {
                fragColor = vec4(uBgColor, 1.0); return;
            }
            int col2 = int(floor(rx * 2.0));
            int row2 = int(floor((1.0 - ry) * 2.0));
            subIdx   = clamp(row2 * 2 + col2 + 1, 1, 4);
            subUV    = vec2(fract(rx * 2.0), 1.0 - fract((1.0 - ry) * 2.0));
            subAspect = (secW * 0.5) / max(frameRes.y * 0.5, 1.0);
        }
        outCol = sampleCam(subIdx, subUV, subAspect);
    }

    fragColor = outCol;
}
