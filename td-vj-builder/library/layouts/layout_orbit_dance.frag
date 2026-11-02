// =============================================================
// ORBIT DANCE LAYOUT - LITTLE JESUS
// =============================================================
// Hero (uHeroIndex) como franja horizontal que abarca todo el
// ancho de pantalla, centrada verticalmente. Las demas camaras
// orbitan en circulo alrededor del centro a uOrbitSpeed,
// pudiendo pasar delante de la franja hero.
// =============================================================

// --- Uniforms ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uHeroIndex;
uniform int   uHeroMode;      // 0=cuadrado centro, 1=franja horizontal, 2=pantalla completa
uniform float uOrbitRadius;   // 0.3   distancia del centro
uniform float uOrbitSpeed;    // 0.3   rad/s
uniform float uPieceSize;     // 0.2   tamano de la pieza orbital
uniform float uHeroSize;      // 0.5   tamano del hero (interpretacion segun uHeroMode)
uniform float uBgScale;       // 1.0   zoom del UV de la cam de fondo (0.5..3.0)
uniform vec3  uBgColor;

out vec4 fragColor;

// Modo Fill: la cam cubre toda la celda, recortando el excedente.
// Asi evitamos bandas negras cuando la celda y la cam tienen aspect distinto.
vec4 sampleCamFit(int idx, vec2 uv, float cellAspect, float camAspect) {
    if (cellAspect > camAspect) {
        float s = camAspect / cellAspect;
        uv.y = uv.y * s + (1.0 - s) * 0.5;
    } else if (cellAspect < camAspect) {
        float s = cellAspect / camAspect;
        uv.x = uv.x * s + (1.0 - s) * 0.5;
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

    float frameAspect = uResolution.x / max(uResolution.y, 1.0);
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    vec4 col = vec4(uBgColor, 1.0);

    // Aplicar uBgScale al UV del hero antes de samplear (zoom centrado)
    float bgScale = max(uBgScale, 0.01);

    // Hero segun uHeroMode (clamp del bgUV para evitar repeat fuera de 0..1)
    if (uHeroMode == 2) {
        // Modo 2: pantalla completa
        vec2  bgUV       = (uv - 0.5) / bgScale + 0.5;
        bgUV = clamp(bgUV, 0.0, 1.0);
        float cellAspect = uResolution.x / max(uResolution.y, 1.0);
        col = sampleCamFit(hero, bgUV, cellAspect, camAspect);
    } else if (uHeroMode == 1) {
        // Modo 1: franja horizontal full-width, altura = uHeroSize
        float h    = clamp(uHeroSize, 0.05, 1.0);
        float yMin = 0.5 - h * 0.5;
        float yMax = 0.5 + h * 0.5;
        if (uv.y >= yMin && uv.y <= yMax) {
            vec2  localUV    = vec2(uv.x, (uv.y - yMin) / h);
            vec2  bgUV       = (localUV - 0.5) / bgScale + 0.5;
            bgUV = clamp(bgUV, 0.0, 1.0);
            float cellAspect = uResolution.x / max(h * uResolution.y, 1.0);
            col = sampleCamFit(hero, bgUV, cellAspect, camAspect);
        }
    } else {
        // Modo 0: cuadrado al centro
        vec2 sz   = vec2(uHeroSize, uHeroSize * frameAspect);
        vec2 minP = vec2(0.5) - sz * 0.5;
        vec2 maxP = vec2(0.5) + sz * 0.5;
        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV = (uv - minP) / sz;
            vec2 bgUV    = (localUV - 0.5) / bgScale + 0.5;
            bgUV = clamp(bgUV, 0.0, 1.0);
            col = sampleCamFit(hero, bgUV, 1.0, camAspect);
        }
    }

    // Resto orbita
    int orbitalCount = max(n - 1, 1);
    int oi = 0;
    vec2 pieceSz = vec2(uPieceSize, uPieceSize * frameAspect);
    for (int i = 0; i < 5; i++) {
        if (i >= n) break;
        if (i == hero) continue;
        float angle = uTime * uOrbitSpeed + float(oi) * (6.28318 / float(orbitalCount));
        // Radio en X y Y compensado por aspect (orbita ciruclar en pantalla)
        vec2 offset = vec2(cos(angle) * uOrbitRadius,
                           sin(angle) * uOrbitRadius * frameAspect);
        vec2 center = vec2(0.5) + offset;
        vec2 minP = center - pieceSz * 0.5;
        vec2 maxP = center + pieceSz * 0.5;
        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV = (uv - minP) / pieceSz;
            col = sampleCamFit(i, localUV, 1.0, camAspect);
        }
        oi++;
    }

    fragColor = col;
}
