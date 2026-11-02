// =============================================================
// BLOOM LAYOUT - LITTLE JESUS
// =============================================================
// Camaras distribuidas en circulo alrededor del centro. Cada
// cam late hacia afuera y adentro con una fase desplazada por
// posicion angular: la onda recorre el anillo como una flor
// que se abre y cierra en secuencia.
//
// Vibe: ritmico, organico, hipnotico. Funciona bien con beats.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;       // 2..5
uniform int   uCamfit;         // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;      // aspect ratio w/h de la cam fuente
uniform vec3  uBgColor;
uniform float uSpeed;          // 0.6   velocidad del latido
uniform float uBaseRadius;     // 0.25  radio base del anillo (fraccion)
uniform float uPulseAmt;       // 0.15  variacion del radio (in/out)
uniform float uCamSize;        // 0.25  tamano base de cada cam
uniform float uSizePulse;      // 0.30  variacion del tamano con el latido
uniform float uRotate;         // 0.05  rotacion lenta del anillo (rad/s)

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

    vec4 col = vec4(uBgColor, 1.0);

    float TAU      = 6.28318530718;
    float angStep  = TAU / float(n);
    float ringRot  = uTime * uRotate;  // rotacion lenta del anillo entero

    // Pintamos cams desde la mas lejana a la mas cercana (z order falso)
    // Aqui simplemente iteramos en orden 0..n: la ultima cam dentro de la
    // celda pinta encima — natural para overlap puntual.
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        float fi    = float(i);
        // Angulo de cada cam: distribucion uniforme + rotacion del anillo
        float angle = fi * angStep + ringRot;
        // Onda viajera: pulse depende de la posicion angular
        float pulse = sin(uTime * uSpeed - fi * angStep);
        float radius = uBaseRadius + pulse * uPulseAmt;
        float scale  = 1.0 + pulse * uSizePulse;

        vec2 offset = vec2(cos(angle) * radius,
                           sin(angle) * radius * frameAspect);
        vec2 center = vec2(0.5) + offset;

        vec2 sz   = vec2(uCamSize * scale, uCamSize * scale * frameAspect);
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
