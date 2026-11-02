// =============================================================
// TUNNEL ZOOM LAYOUT — LITTLE JESUS
// =============================================================
// Camaras en anillos concentricos. Hero al centro como tunel.
// Las secundarias forman los anillos exteriores con zoom radial
// animado por uTime * uZoomSpeed. Sensacion de profundidad.
//
// Distribucion (de centro a fuera): hero, cam1, cam2, cam3, cam4.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;     // 2..5
uniform int   uHeroIndex;    // 0..4
uniform float uZoomSpeed;    // 0.2 default
uniform float uRingBlend;    // 0.01 suavidad del borde entre anillos

out vec4 fragColor;

vec4 sampleCam(int idx, vec2 uv) {
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

    // UV centrado en el frame, corregido por aspect ratio
    vec2 c = uv - 0.5;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    c.x *= aspect;
    float r = length(c);

    // Animacion radial: el radio "respira" con el tiempo
    float offset = uTime * uZoomSpeed;
    float rAnim  = fract(r + offset);  // 0..1 ciclico

    // Bandas de anillo. Numero de bandas = n.
    // banda 0 = centro = hero, las demas = secundarias (saltando hero)
    int band = int(floor(rAnim * float(n)));
    band = clamp(band, 0, n - 1);

    // Indice de camara: banda 0 = hero, banda i (i>0) = i-esima camara no-hero
    int camIdx;
    if (band == 0) {
        camIdx = hero;
    } else {
        // Lista de camaras no-hero (en orden)
        int picked = -1;
        int passed = 0;
        for (int i = 0; i < 5; i++) {
            if (i < n && i != hero) {
                passed++;
                if (passed == band) { picked = i; break; }
            }
        }
        camIdx = (picked >= 0) ? picked : hero;
    }

    // UV local de la banda: estira/wrap segun radio
    // Reconstruimos un UV "normal" usando el angulo y la frac del radio
    float angle = atan(c.y, c.x);
    float u_loc = fract(angle / (2.0 * 3.14159265) + 0.5);
    float v_loc = fract(rAnim * float(n));
    vec2  localUV = vec2(u_loc, v_loc);

    vec4 outCol = sampleCam(camIdx, localUV);

    // Suavizar bordes entre anillos
    float edge = abs(fract(rAnim * float(n)) - 0.5) * 2.0;  // 0 al centro de la banda, 1 al borde
    float mask = smoothstep(1.0, 1.0 - uRingBlend, edge);
    outCol.rgb *= mask;

    fragColor = outCol;
}
