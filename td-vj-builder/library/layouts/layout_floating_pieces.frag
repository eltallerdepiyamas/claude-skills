// =============================================================
// FLOATING PIECES LAYOUT — LITTLE JESUS
// =============================================================
// Cada camara es un cuadrado que flota con su propia velocidad
// y fase. Se pueden cruzar; la ultima cam pintada gana (sin blend).
// Aspect ratio preservado: si la celda no coincide con la cam,
// se hace letterbox/pillarbox a negro.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;     // 2..5
uniform float uPieceSize;    // 0.3 lado del cuadrado en UV
uniform float uSpeed;        // 0.2 velocidad de drift
uniform vec3  uBgColor;      // color de fondo

out vec4 fragColor;

// Modo Fill: la cam cubre toda la pieza, recortando el excedente.
// Asi evitamos bandas negras cuando la pieza y la cam tienen aspect distinto.
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

vec2 piecePos(int i, float t) {
    float fi = float(i);
    return vec2(
        sin(t * uSpeed       + fi * 1.7) * 0.4 + 0.5,
        cos(t * uSpeed * 0.7 + fi * 2.3) * 0.4 + 0.5
    );
}

void main() {
    vec2  uv = vUV.st;
    int   n  = clamp(uCamCount, 2, 5);
    float sz = max(uPieceSize, 0.05);

    // Aspect ratio del frame y de la cam (asume todas las cams = aspect del input 0)
    float frameAspect = uResolution.x / max(uResolution.y, 1.0);
    vec2  cs = vec2(textureSize(sTD2DInputs[0], 0));
    float camAspect = cs.x / max(cs.y, 1.0);

    // Cada pieza es cuadrada en pantalla -> en UV su altura compensa el aspect
    vec2 pieceUV = vec2(sz, sz * frameAspect);

    vec4 col = vec4(uBgColor, 1.0);

    for (int i = 0; i < 5; i++) {
        if (i >= n) break;
        vec2 center = piecePos(i, uTime);
        vec2 minP = center - pieceUV * 0.5;
        vec2 maxP = center + pieceUV * 0.5;
        if (uv.x >= minP.x && uv.x <= maxP.x &&
            uv.y >= minP.y && uv.y <= maxP.y) {
            vec2 localUV = (uv - minP) / pieceUV;
            // cellAspect de la pieza = 1.0 (cuadrada)
            col = sampleCamFit(i, localUV, 1.0, camAspect);
        }
    }

    fragColor = col;
}
