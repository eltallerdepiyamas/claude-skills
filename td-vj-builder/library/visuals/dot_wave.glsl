// dot_wave.glsl — base18 · Malla de puntos (CORONA x FUTURE x ULTRA)
// Ref. cliente pinterest7: malla de puntos en hilos verticales que ondula como tela; donde la malla
// se pliega los hilos se juntan y brilla más. Hilos verticales (no líneas apiladas tipo Joy Division).
// Paleta del cliente por altura de la tela: valles azules (≈70%) · crestas amarillas · picos blancos.
// Un solo canvas continuo alrededor del booth (repartido); techo = la misma tela en todo el cuadro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_low;         // graves suavizados
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (picos)
uniform vec3  u_color2;      // amarillo Corona (crestas)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (dominante)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–3    ondulación
uniform float u_fold;        // 3 distorsión · 0–1    amplitud de los pliegues
uniform float u_accent;      // 4 color      · 0–1    franja amarilla de las crestas (0.2 = paleta)
uniform float u_lines;       // 5 firma      · 40–400 hilos por cada 1920 px

// extras
uniform float u_dots;        // 0.3–3  separación de puntos en el hilo (× separación de hilos)
uniform float u_dotsize;     // 0.5–3  radio del punto (px)
uniform float u_white;       // 0–0.5  franja blanca de los picos (0.1 = paleta)

out vec4 fragColor;

vec3 tonemap(vec3 c, float k) {
    float m = max(c.r, max(c.g, c.b));
    return m > 1e-5 ? c * (1.0 - exp(-m * k)) / m : c;
}

// altura de la tela (-1..1): ondas lentas cruzadas + ondulación del kick
float height(vec2 q, float t, float kick) {
    float h = sin(q.x * 2.1 + t * 0.7) * 0.45
            + sin(q.y * 3.3 - t * 0.9 + sin(q.x * 1.3 + t * 0.3) * 1.5) * 0.35
            + sin((q.x + q.y) * 5.0 + t * 1.3) * 0.2;
    h += kick * 0.12 * sin(length(q - vec2(1.0, 0.5)) * 6.0 - t * 6.0);
    return h;
}

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float lo = clamp(u_low, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    float t = u_time * u_speed;
    float aspect = u_res.x / u_res.y;

    vec2 q = uv * vec2(aspect, 1.0);
    float A = u_fold * (1.0 + 0.6 * lo);
    float h  = height(q, t, kick);
    float hx = height(q + vec2(0.004, 0.0), t, kick);
    float hy = height(q + vec2(0.0, 0.004), t, kick);
    vec2 grad = vec2(hx - h, hy - h) / 0.004;

    // la tela se desplaza de lado según su pendiente → los hilos se juntan en los pliegues
    vec2 w = q + vec2(grad.x * 0.09, grad.y * 0.02) * A + vec2(h * 0.06 * A, 0.0);
    float lines = max(u_lines, 1.0) * u_res.x / 1920.0;   // misma separación en px en columnas y en techo
    float gx = w.x / aspect * lines;
    float gy = w.y / aspect * lines / max(u_dots, 0.1);

    float sx = 1.0 / max(fwidth(gx), 1e-4);            // px entre hilos
    float sy = 1.0 / max(fwidth(gy), 1e-4);            // px entre puntos
    vec2 f = (fract(vec2(gx, gy)) - 0.5) * vec2(sx, sy);
    float rad = u_dotsize;
    float dotV = 1.0 - smoothstep(rad - 0.6, rad + 0.6, length(f));
    float cover = min(3.14159 * rad * rad / (sx * sy), 1.0);   // cuando los hilos se juntan: densidad promedio
    dotV = mix(dotV, cover * 1.6, smoothstep(3.5, 1.5, min(sx, sy)));

    // luz rasante: las caras que miran a la luz brillan, las otras se van a negro
    float shade = clamp(0.25 + 0.75 * (0.5 + 0.35 * grad.x * 0.3 - 0.25 * grad.y * 0.3), 0.08, 1.0);
    float compress = clamp(pow(12.0 / sx, 2.0) * 0.5, 0.0, 2.0);   // hilos juntos = pliegue brillante
    float lvl = shade * (0.35 + 0.9 * compress) * (0.75 + 0.4 * e);

    // color por altura: valles azules, crestas amarillas, picos blancos
    float hh = 1.0 / (1.0 + exp(-4.0 * h));          // ≈ percentil de la altura → Accent/White son fracciones reales
    float yellow = smoothstep(1.0 - u_white - u_accent - 0.03, 1.0 - u_white - u_accent + 0.03, hh);
    float white  = smoothstep(1.0 - u_white - 0.03, 1.0 - u_white + 0.03, hh);
    vec3 c = mix(mix(u_color4, u_color2, yellow), u_color1, white);

    vec3 col = c * dotV * lvl * 3.0;
    col *= u_intensity;
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
