// =============================================================
// PIP LAYOUT - LITTLE JESUS
// =============================================================
// Picture in Picture. Hero a pantalla completa + PIPs en las
// esquinas (con bob suave si uPipSpeed > 0) y borde de color
// uBorderColor.
//
// Distribucion segun uCamCount:
//   2 -> BR / 3 -> BL,BR / 4 -> BL,BR,TR / 5 -> 4 esquinas
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;        // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;     // aspect w/h de la cam fuente
uniform int   uHeroIndex;
uniform float uPipSize;
uniform float uPipBorder;
uniform float uPipPadding;
uniform float uPipSpeed;      // 0..2  velocidad del bob (0 = quietas)
uniform float uPipBobAmt;     // 0..1  amplitud del bob (fraccion del padding)
uniform vec3  uBorderColor;   // color del borde de las PIPs
uniform vec3  uBgColor;       // color de fondo fuera de area en modo Fit

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
    // FIX: en Fill (0) y Stretch (2) clampea, solo Fit (1) muestra negro/bg
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
    vec2  uv   = vUV.st;
    int   n    = clamp(uCamCount, 2, 5);
    int   hero = clamp(uHeroIndex, 0, n - 1);

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);

    // Hero a pantalla completa
    vec4 outCol = sampleCam(hero, uv, frameAspect);

    // PIPs cuadradas en pantalla
    vec2  pipSize = vec2(uPipSize, uPipSize * frameAspect);
    float pad = uPipPadding;
    float bdr = uPipBorder;

    vec2 corners[4] = vec2[4](
        vec2(pad,                       pad),
        vec2(1.0 - pad - pipSize.x,     pad),
        vec2(pad,                       1.0 - pad - pipSize.y),
        vec2(1.0 - pad - pipSize.x,     1.0 - pad - pipSize.y)
    );

    int pipOrder[4] = int[4](-1, -1, -1, -1);
    if      (n == 2) { pipOrder[0] = 1; }
    else if (n == 3) { pipOrder[0] = 0; pipOrder[1] = 1; }
    else if (n == 4) { pipOrder[0] = 0; pipOrder[1] = 1; pipOrder[2] = 3; }
    else             { pipOrder[0] = 0; pipOrder[1] = 1; pipOrder[2] = 2; pipOrder[3] = 3; }

    int pipCams[4] = int[4](0, 0, 0, 0);
    int pipCount = 0;
    for (int i = 0; i < 5; i++) {
        if (i < n && i != hero && pipCount < 4) {
            pipCams[pipCount] = i;
            pipCount++;
        }
    }

    float bobAmp = uPipPadding * clamp(uPipBobAmt, 0.0, 1.0) * 0.5;
    float t      = uTime * uPipSpeed;

    for (int p = 0; p < 4; p++) {
        int cIdx = pipOrder[p];
        if (cIdx < 0)         continue;
        if (p >= pipCount)    continue;

        float fp  = float(p);
        vec2  bob = vec2(sin(t * 1.0 + fp * 1.7) * bobAmp,
                         cos(t * 1.3 + fp * 2.1) * bobAmp * frameAspect);

        vec2 origin = corners[cIdx] + bob;
        vec2 pipMin = origin;
        vec2 pipMax = origin + pipSize;

        if (uv.x >= pipMin.x && uv.x <= pipMax.x &&
            uv.y >= pipMin.y && uv.y <= pipMax.y)
        {
            float dx = min(uv.x - pipMin.x, pipMax.x - uv.x);
            float dy = min(uv.y - pipMin.y, pipMax.y - uv.y);
            float edge = min(dx, dy);

            if (edge < bdr) {
                outCol = vec4(uBorderColor, 1.0);
            } else {
                vec2 localUV = (uv - pipMin) / pipSize;
                // PIP cuadrada en pantalla -> cellAspect = 1.0
                outCol = sampleCam(pipCams[p], localUV, 1.0);
            }
        }
    }

    fragColor = outCol;
}
