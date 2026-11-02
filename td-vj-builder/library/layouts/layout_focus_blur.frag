// =============================================================
// FOCUS BLUR LAYOUT — LITTLE JESUS
// =============================================================
// Hero en foco al centro, secundarias borrosas a opacidad reducida
// visibles en los bordes (efecto halo). Aspect preservado.
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uHeroIndex;
uniform float uBgOpacity;
uniform float uBlurRadius;

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

vec3 blurredFit(int idx, vec2 uv, float frameAspect, float camAspect, float r) {
    vec3 sum = vec3(0.0);
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            vec2 off = vec2(float(x), float(y)) * r;
            vec2 sUV = clamp(uv + off, vec2(0.0), vec2(1.0));
            sum += sampleCamFit(idx, sUV, frameAspect, camAspect).rgb;
        }
    }
    return sum / 9.0;
}

void main() {
    vec2 uv   = vUV.st;
    int  n    = clamp(uCamCount, 2, 5);
    int  hero = clamp(uHeroIndex, 0, n - 1);

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    // Promedio borroso de las secundarias
    vec3 bg = vec3(0.0);
    int  count = 0;
    for (int i = 0; i < 5; i++) {
        if (i < n && i != hero) {
            bg += blurredFit(i, uv, frameAspect, camAspect, uBlurRadius);
            count++;
        }
    }
    if (count > 0) bg /= float(count);

    vec3 heroCol = sampleCamFit(hero, uv, frameAspect, camAspect).rgb;

    float vig = smoothstep(0.7, 0.0, distance(uv, vec2(0.5)));
    vec3  final = mix(bg * uBgOpacity, heroCol, vig);

    fragColor = vec4(final, 1.0);
}
