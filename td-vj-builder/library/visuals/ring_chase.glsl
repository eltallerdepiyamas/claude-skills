// ring_chase.glsl — base6 · Persecución circular (CORONA x FUTURE x ULTRA)
// Pensado para las 8 columnas en mapeo Repartido (canvas ≈ 2.4:1): el ancho del canvas es
// la vuelta completa al booth. Pulsos de luz con estela que le dan vueltas a la gente; en los
// picos aparece un pulso a contracorriente; el kick enciende el anillo completo un instante.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo: los pulsos giran alrededor de la corona

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–2    vueltas por segundo
uniform float u_smear;       // 3 distorsión · 0–1    largo de estela + curvatura del pulso
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_count;       // 5 firma      · 1–8    pulsos en la vuelta

// extras
uniform float u_panels;      // 1–16  columnas en el canvas (8 = booth)
uniform float u_snap;        // 0–1   0 = pulso suave · 1 = enciende columnas enteras
uniform float u_split;       // 0–1   pulso a contracorriente en los picos

uniform float u_white;       // 0–0.5  fracción blanca (0.1 = paleta)

out vec4 fragColor;

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

// paleta del cliente por elemento: White → blanco · Accent → amarillo · resto → azul
vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

// reparto fijo por columna (permutación): con 8 columnas siempre salen las proporciones de la paleta
float colRank(float i, float n) { return (mod(i * 5.0 + 3.0, n) + 0.5) / n; }

// curva de brillo que respeta el tono (el amarillo no se lava a blanco)
vec3 tonemap(vec3 c, float k) {
    float m = max(c.r, max(c.g, c.b));
    return m > 1e-5 ? c * (1.0 - exp(-m * k)) / m : c;
}

// estela detrás de la cabeza: d = distancia hacia atrás (en columnas)
float chase(float d, float tail) {
    float head = exp(-d / 0.08);
    float tr = exp(-d / tail);
    return head * 1.4 + tr * 0.4;
}

void main() {
    vec2 uv = vUV.st;
    if (u_surface > 0.5) {      // techo: la vuelta al booth = la vuelta alrededor del centro (polar)
        vec2 c = uv - 0.5;
        uv = vec2(atan(c.y, c.x) / 6.28318 + 0.5, min(length(c) * 2.0, 1.0));
    }
    float N = max(floor(u_panels + 0.5), 1.0);
    float e = clamp(u_bass, 0.0, 2.0);
    float kick = clamp(u_kick, 0.0, 1.5);
    float t = u_time * u_speed;

    // curvatura: el pulso se dobla a lo alto de la columna
    float x = uv.x + sin(uv.y * 5.0 + u_time * 1.3) * u_smear * 0.012;
    float xs = mix(x, (floor(x * N) + 0.5) / N, u_snap);   // snap a columnas enteras

    float tail = 0.12 + u_smear * 1.1 + e * 0.25;           // en columnas
    float n = max(floor(u_count + 0.5), 1.0);
    float main_ = 0.0;
    float trailOnly = 0.0;
    for (int k = 0; k < 8; k++) {
        if (float(k) >= n) break;
        float pos = fract(t + float(k) / n);
        float d = fract(pos - xs) * N;                      // hacia atrás, en columnas
        main_ += chase(d, tail);
        trailOnly += exp(-d / tail) * (1.0 - exp(-d / 0.3));
    }
    // contracorriente en los picos
    float pos2 = fract(-t * 1.37 + 0.5);
    float d2 = fract(xs - pos2) * N;
    float counter = chase(d2, tail * 0.6) * u_split * smoothstep(0.5, 1.3, e);

    // lamas horizontales: textura de LED / persiana
    float slat = 0.78 + 0.22 * step(0.5, fract(uv.y * 48.0));
    // marco tenue de cada columna
    float lx = fract(x * N);
    float frame = 1.0 - smoothstep(0.0, 2.0 * N / u_res.x, min(lx, 1.0 - lx));

    vec3 cc = pick(colRank(floor(fract(x) * N), N));        // el pulso toma el color de la columna
    vec3 col = cc * (max(main_ - trailOnly, 0.0) + trailOnly * 0.45);
    col += mix(u_color2, u_color1, 0.3) * counter * 0.6;
    col *= slat;
    col += u_color4 * kick * 0.08 * slat;                   // anillo completo en el golpe
    col += u_color4 * frame * 0.05;
    col *= u_intensity * (0.8 + 0.3 * e);
    col = tonemap(col, 1.3);
    col += u_color3;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
