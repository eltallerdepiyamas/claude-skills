// test_pantallas.frag — barras SMPTE, empty (negro) o imagen cargada desde archivo,
// con rampa de glow animada encima. La forma del glow se elige (línea diagonal, círculo expandiéndose,
// barra horizontal o vertical). Resolución = la del show.
//
// uModo: 0 Barras SMPTE · 1 Empty · 2 Imagen cargada (desde sTD2DInputs[0]) · 3 Contorno
// Contorno: el borde exacto del lienzo en blanco, para cuadrar el LED. El grosor va en
// PIXELES reales (uContorno): con 4608x1280 una fraccion de pantalla daria distinto grosor
// arriba que a los lados. Se dibuja pegado al primer y al ultimo pixel.
// uGlowforma: 0 Linea diagonal · 1 Circulo expandiendo · 2 Barra horizontal · 3 Barra vertical
// uGlowvel: velocidad del glow (0 = detenido)

uniform float uModo;
uniform vec2  uResolution;
uniform float uTime;
uniform float uGlowforma;
uniform float uGlowvel;
uniform float uGlowon;      // 0 apaga completamente el glow
uniform float uContorno;    // grosor del contorno en PIXELES (modo 3)

// 1.0 dentro de la banda [a, b] en pixeles, con medio pixel de suavizado en los cantos
float banda_px(float x, float a, float b) {
    return clamp(min(x - a, b - x) + 0.5, 0.0, 1.0);
}

out vec4 fragColor;

vec3 barras_smpte(vec2 uv) {
    float x = uv.x * 7.0;
    int i = int(floor(x));
    if (i == 0) return vec3(0.75);
    if (i == 1) return vec3(0.75, 0.75, 0.0);
    if (i == 2) return vec3(0.0, 0.75, 0.75);
    if (i == 3) return vec3(0.0, 0.75, 0.0);
    if (i == 4) return vec3(0.75, 0.0, 0.75);
    if (i == 5) return vec3(0.75, 0.0, 0.0);
    return vec3(0.0, 0.0, 0.75);
}

void main() {
    vec2 uv = vUV.st;
    vec3 col = vec3(0.0);
    int modo = int(uModo + 0.5);
    float asp = uResolution.x / max(uResolution.y, 1.0);

    // ── fondo base ──────────────────────────────────────────────────────────
    if (modo == 0) {
        // Barras SMPTE (con pluge inferior)
        if (uv.y > 0.25) {
            col = barras_smpte(uv);
        } else {
            float x = uv.x * 5.0;
            int i = int(floor(x));
            if (i == 0) col = vec3(1.0);
            else if (i == 1) col = vec3(0.5);
            else if (i == 2) col = vec3(0.25);
            else if (i == 3) col = vec3(0.0);
            else col = vec3(0.03);
        }
    } else if (modo == 1) {
        // Empty
        col = vec3(0.0);
    } else if (modo == 2) {
        // Imagen cargada (TOP conectado en input 0 del GLSL)
        col = textureLod(sTD2DInputs[0], uv, 0.0).rgb;
    } else {
        // Contorno: el borde del lienzo en blanco, pegado al primer / ultimo pixel.
        // dentroX / dentroY recortan al ancho y alto utiles para que las esquinas cierren
        // en angulo recto y no sobresalga nada.
        vec2 px = uv * uResolution;
        float g = max(uContorno, 1.0);
        float izq = banda_px(px.x, 0.0, g);
        float der = banda_px(px.x, uResolution.x - g, uResolution.x);
        float aba = banda_px(px.y, 0.0, g);
        float arr = banda_px(px.y, uResolution.y - g, uResolution.y);
        float dentroY = banda_px(px.y, 0.0, uResolution.y);
        float dentroX = banda_px(px.x, 0.0, uResolution.x);
        col = vec3(max(max(izq, der) * dentroY, max(aba, arr) * dentroX));
    }

    // ── rampa con glow encima ─────────────────────────────────────────────
    if (uGlowon < 0.5) {
        fragColor = TDOutputSwizzle(vec4(col, 1.0));
        return;
    }
    int forma = int(uGlowforma + 0.5);
    float t = uTime * clamp(uGlowvel, 0.0, 4.0);
    float dist;

    if (forma == 0) {
        // Línea diagonal recorriendo
        float ang = 0.55;
        float cs = cos(ang), sn = sin(ang);
        float d = uv.x * asp * cs + uv.y * sn;
        float totalD = asp * cs + sn;
        float rampPos = fract(t * 0.18) * (totalD + 0.6) - 0.3;
        dist = d - rampPos;
    } else if (forma == 1) {
        // Círculo expandiendo desde el centro (en espacio con aspect: círculo real)
        vec2 p = (uv - 0.5) * vec2(asp, 1.0);
        float r = length(p);
        float maxR = sqrt(asp * asp * 0.25 + 0.25) + 0.1;
        float rampR = fract(t * 0.18) * (maxR + 0.2);
        dist = r - rampR;
    } else if (forma == 2) {
        // Barra horizontal (sube/baja)
        float rampY = fract(t * 0.15);
        dist = uv.y - rampY;
    } else {
        // Barra vertical (recorre lateralmente)
        float rampX = fract(t * 0.15);
        dist = uv.x - rampX;
    }

    float core  = exp(-abs(dist) * 60.0);
    float halo  = exp(-abs(dist) * 6.0);
    float trail = smoothstep(0.0, 0.25, -dist) * exp(dist * 2.8);
    float pulse = 0.7 + 0.3 * sin(t * 2.6);

    vec3 glow1 = vec3(1.00, 0.55, 0.92);   // rosa neón
    vec3 glow2 = vec3(0.60, 0.35, 1.00);   // púrpura eléctrico
    vec3 spark = vec3(1.00, 0.98, 1.00);   // casi blanco

    col += glow2 * halo * 0.40 * pulse;
    col += glow1 * trail * 0.50;
    col += spark * core * 1.40;

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
