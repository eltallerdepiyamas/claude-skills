// =============================================================
// SWARM LAYOUT - LITTLE JESUS
// =============================================================
// El centro del enjambre se mueve lento por la pantalla trazando
// una figura Lissajous. Cada cam orbita el centro con su propio
// radio y velocidad, generando un patron caotico organico.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;       // 2..5
uniform int   uCamfit;         // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;
uniform vec3  uBgColor;
uniform float uSpeed;          // 0.20  velocidad orbital base
uniform float uSwarmRadius;    // 0.25  radio del enjambre (fraccion)
uniform float uCenterSpeed;    // 0.08  velocidad del centro
uniform float uCamSize;        // 0.25

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

    // Centro del enjambre (Lissajous lento)
    float cx = sin(uTime * uCenterSpeed * 1.3) * 0.30;
    float cy = cos(uTime * uCenterSpeed * 1.0) * 0.30;
    vec2  swarmCenter = vec2(0.5 + cx, 0.5 + cy);

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        float fi = float(i);
        // Orbita individual con freq escalonada y fase distinta
        float ox = cos(uTime * uSpeed * (1.0 + fi * 0.20) + fi * 1.257) * uSwarmRadius;
        float oy = sin(uTime * uSpeed * (1.0 + fi * 0.15) + fi * 0.900) * uSwarmRadius;
        vec2  center = swarmCenter + vec2(ox, oy);

        vec2 minP = center - sz * 0.5;
        vec2 maxP = center + sz * 0.5;
        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV = (uv - minP) / sz;
            col = applyCamFit(i, localUV, 1.0);
        }
    }

    fragColor = col;
}
