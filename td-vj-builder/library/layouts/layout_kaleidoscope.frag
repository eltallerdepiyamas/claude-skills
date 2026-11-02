// =============================================================
// KALEIDOSCOPE LAYOUT — LITTLE JESUS
// =============================================================
// Caleidoscopio radial. El frame se divide en N segmentos
// triangulares espejados; el contenido de cada segmento sale de
// una camara distinta segun el radio. Rotacion automatica.
//
// Mejor uso: con uSegments alto (8..12) la imagen se ve organica
// y simetrica; con uSegments bajo (3..4) se ven los segmentos.
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform float uSegments;       // 6 (3..12) cantidad de gajos
uniform float uRotateSpeed;    // 0.1 rad/s
uniform float uZoom;           // 1.0 zoom del contenido

out vec4 fragColor;

vec4 sampleCamRaw(int idx, vec2 uv) {
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

    // UV centrado en pantalla, corregido por aspect (gajos isotropicos)
    vec2  c = uv - 0.5;
    float frameAspect = uResolution.x / max(uResolution.y, 1.0);
    c.x *= frameAspect;

    float r     = length(c);
    float angle = atan(c.y, c.x);

    // Rotacion automatica
    angle += uTime * uRotateSpeed;

    // Kaleidoscope: modular angulo en gajos, espejo alternado
    float seg = 6.28318 / max(uSegments, 1.0);
    float segIdx   = floor(angle / seg);
    float segLocal = mod(angle, seg);
    if (mod(segIdx, 2.0) > 0.5) segLocal = seg - segLocal;

    // UV reconstruido dentro de un gajo
    vec2 newC = vec2(cos(segLocal), sin(segLocal)) * r * uZoom;
    newC.x /= frameAspect;
    vec2 newUV = newC + 0.5;

    // Cam segun radio (anillos)
    int camIdx = clamp(int(r * float(n) * uZoom), 0, n - 1);

    // Wrap del UV para que se vea cuando newUV salga del rango
    fragColor = sampleCamRaw(camIdx, fract(newUV));
}
