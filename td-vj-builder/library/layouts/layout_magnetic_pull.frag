// =============================================================
// MAGNETIC PULL LAYOUT - LITTLE JESUS
// =============================================================
// Camaras atraidas por un punto central movil. La fuerza de
// atraccion decae con la distancia (smoothstep en uPullRadius).
// Cuando una cam es atraida, tambien escala ligeramente.
// El punto de atraccion traza una figura de Lissajous lenta.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;       // 2..5
uniform int   uCamfit;         // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;
uniform vec3  uBgColor;
uniform float uSpeed;          // 0.15  velocidad del punto
uniform float uPullStrength;   // 0.4   0=nada, 1=colapsan
uniform float uPullRadius;     // 0.5   radio de influencia
uniform float uCamSize;        // 0.30  tamano base

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

// Posicion base de cada cam: pentagono alrededor del centro
vec2 basePos(int i) {
    float a = float(i) * 1.2566;  // 2pi/5
    return vec2(0.5 + 0.30 * cos(a),
                0.5 + 0.30 * sin(a));
}

void main() {
    vec2  uv = vUV.st;
    int   n  = clamp(uCamCount, 2, 5);

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);

    // Punto de atraccion (Lissajous lento)
    vec2 pull = vec2(0.5 + 0.30 * sin(uTime * uSpeed),
                     0.5 + 0.30 * cos(uTime * uSpeed * 0.7));

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        vec2  bp    = basePos(i);
        float dist  = length(bp - pull);
        float radius = max(uPullRadius, 0.001);
        // attr = 1 cuando dist=0, 0 cuando dist>=radius
        float attr  = uPullStrength * (1.0 - smoothstep(0.0, radius, dist));
        vec2  pos   = mix(bp, pull, attr);
        float scale = 1.0 + attr * 0.30;

        vec2 sz   = vec2(uCamSize * scale, uCamSize * scale * frameAspect);
        vec2 minP = pos - sz * 0.5;
        vec2 maxP = pos + sz * 0.5;
        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV = (uv - minP) / sz;
            col = applyCamFit(i, localUV, 1.0);
        }
    }

    fragColor = col;
}
