// =============================================================
// GRIDWALL DRIFT LAYOUT - LITTLE JESUS
// =============================================================
// Grid de camaras con celdas de tamano variable. Drift continuo
// en X o Y con loop wrap: cuando una cam sale por un lado,
// reaparece por el otro.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;       // 2..5
uniform int   uCamfit;         // 0=Fill, 1=Fit, 2=Stretch
uniform float uCamAspect;      // aspect ratio w/h de la cam fuente
uniform vec3  uBgColor;        // color de fondo
uniform float uSpeed;          // 0.05  velocidad del drift
uniform int   uDirection;      // 0=horizontal, 1=vertical
uniform float uSizeVariance;   // 0..1  0=cams iguales, 1=specs .md

out vec4 fragColor;

// Sampler con mode de encuadre. uCamfit 0=Fill 1=Fit 2=Stretch.
vec4 applyCamFit(int idx, vec2 uv, float cellAspect) {
    if (uCamfit == 0) {
        // Fill: cubre la celda, recorta excedente de la cam
        if (cellAspect > uCamAspect) {
            float s = uCamAspect / cellAspect;
            uv.y = uv.y * s + (1.0 - s) * 0.5;
        } else if (cellAspect < uCamAspect) {
            float s = cellAspect / uCamAspect;
            uv.x = uv.x * s + (1.0 - s) * 0.5;
        }
    } else if (uCamfit == 1) {
        // Fit: cam entera visible, bandas negras donde sobra
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
    // uCamfit == 2 Stretch: uv pasa directo
    if (idx == 0) return texture(sTD2DInputs[0], uv);
    if (idx == 1) return texture(sTD2DInputs[1], uv);
    if (idx == 2) return texture(sTD2DInputs[2], uv);
    if (idx == 3) return texture(sTD2DInputs[3], uv);
    if (idx == 4) return texture(sTD2DInputs[4], uv);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

// Tamano base de cada celda en fraccion de ResW x ResH
vec2 baseSize(int i) {
    if (i == 0) return vec2(0.40, 0.60);  // principal
    if (i == 1) return vec2(0.35, 0.50);  // secundaria grande
    if (i == 2) return vec2(0.25, 0.40);  // pequenia
    if (i == 3) return vec2(0.35, 0.50);  // secundaria grande
    return vec2(0.25, 0.40);              // i==4 pequenia
}

// Offset perpendicular al eje de drift (-0.5..0.5 escalado por uSpread)
float perpOff(int i) {
    if (i == 0) return -0.30;
    if (i == 1) return  0.10;
    if (i == 2) return -0.10;
    if (i == 3) return  0.25;
    return -0.25;
}

void main() {
    vec2  uv     = vUV.st;
    int   n      = clamp(uCamCount, 2, 5);
    vec2  meanSz = vec2(0.32, 0.48);

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;

        vec2  size       = mix(meanSz, baseSize(i), uSizeVariance);
        float cellAspect = (size.x * uResolution.x) /
                           max(size.y * uResolution.y, 1.0);

        float drift = fract(uTime * uSpeed + float(i) * 0.2);
        float perp  = 0.5 + perpOff(i);

        // Dos copias para wrap visual sin saltos
        for (int k = 0; k < 2; k++) {
            float pos = drift - float(k);
            vec2  center = (uDirection == 0)
                           ? vec2(pos,  perp)
                           : vec2(perp, pos);
            vec2 minP = center - size * 0.5;
            vec2 maxP = center + size * 0.5;
            if (uv.x >= minP.x && uv.x <= maxP.x &&
                uv.y >= minP.y && uv.y <= maxP.y) {
                vec2 localUV = (uv - minP) / size;
                col = applyCamFit(i, localUV, cellAspect);
            }
        }
    }

    fragColor = col;
}
