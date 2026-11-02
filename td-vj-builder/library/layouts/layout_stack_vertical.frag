// =============================================================
// STACK VERTICAL LAYOUT — LITTLE JESUS
// =============================================================
// N camaras apiladas verticalmente en franjas de altura 1/N.
// Aspect preservado por franja.
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform float uSeparatorH;
uniform vec3  uSeparatorColor;

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

    float stripH = 1.0 / float(n);
    float invY = 1.0 - uv.y;
    int   row  = clamp(int(floor(invY / stripH)), 0, n - 1);

    float localY = 1.0 - fract(invY / stripH);
    vec2  localUV = vec2(uv.x, localY);

    float yMod = mod(invY, stripH);
    float half_sep = max(uSeparatorH * 0.5, 0.0);
    if (yMod < half_sep || yMod > stripH - half_sep) {
        fragColor = vec4(uSeparatorColor, 1.0);
        return;
    }

    // Aspect de la franja: full width / (stripH * resH)
    float cellAspect = uResolution.x / (stripH * uResolution.y);
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    fragColor = sampleCamFit(row, localUV, cellAspect, camAspect);
}
