// code_rain.glsl — base13 · Lluvia de código (CORONA x FUTURE x ULTRA)
// Ref. cliente pinterest1 + pinterest2 (misma idea, solo cambia el color): columnas de glifos que
// caen, cabeza brillante y estela que se apaga, glifos que mutan, capas lejanas más chicas y tenues.
// Paleta del cliente por columna: 70% azul · 20% amarillo · 10% blanco (Accent / White la ajustan).
// u_surface: 0 = columnas (glifos alineados a las 8 tiras) · 1 = techo: la lluvia cae desde el borde
// hacia la corona del centro (columnas en polar).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_low;         // graves suavizados
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–3    caída
uniform float u_glitch;      // 3 distorsión · 0–1    mutación de glifos + filas que se desplazan
uniform float u_accent;      // 4 color      · 0–1    fracción de columnas amarillas (0.2 = paleta)
uniform float u_columns;     // 5 firma      · 2–16   columnas de glifos por tira

// extras
uniform float u_trail;       // 0.1–1  largo de la estela (fracción del alto)
uniform float u_depth;       // 0–1    capas lejanas
uniform float u_white;       // 0–0.5  fracción de columnas blancas (0.1 = paleta)
uniform float u_panels;      // 1–16   tiras en el canvas (8 = booth)

out vec4 fragColor;

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 tonemap(vec3 c, float k) {
    float m = max(c.r, max(c.g, c.b));
    return m > 1e-5 ? c * (1.0 - exp(-m * k)) / m : c;
}

// paleta por elemento: White → blanco · Accent → amarillo · resto → azul
vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

// glifo 5x7 de puntos cuadrados; la mitad son simétricos (se leen más "caracter")
float glyph(vec2 f, float seed) {
    vec2 g = f * vec2(7.0, 9.0) - 1.0;
    if (g.x < 0.0 || g.y < 0.0 || g.x >= 5.0 || g.y >= 7.0) return 0.0;
    vec2 px = floor(g);
    if (seed > 0.5) px.x = min(px.x, 4.0 - px.x);
    float on = step(0.5, hash21(px + seed * 97.0));
    vec2 q = abs(fract(g) - 0.5);
    return on * (1.0 - smoothstep(0.3, 0.48, max(q.x, q.y)));
}

// g = (columna, fila desde arriba) en unidades de celda
vec3 rain(vec2 g, float rows, float spd, float seed, float lo, float kick) {
    vec2 id = floor(g);
    float hc = hash21(vec2(id.x, seed));
    float trailRows = max(rows * u_trail, 2.0);
    float P = rows + trailRows + 8.0 * hash21(vec2(id.x, seed + 3.1));   // periodo de la columna
    float head = mod(u_time * spd * mix(0.55, 1.6, hc) * 9.0 + hc * P, P);
    float d = mod(head - id.y, P);                    // filas detrás de la cabeza
    float tail = d < trailRows ? pow(1.0 - d / trailRows, 1.6) : 0.0;
    float isHead = 1.0 - step(1.0, d);

    float rate = 0.5 + u_glitch * 14.0 * hash21(id + 7.0);
    float gs = hash21(id + floor(u_time * rate) * 13.1 + seed);
    float gl = glyph(fract(g), gs);

    vec3 c = pick(hash21(vec2(id.x, seed + 11.0)));
    float lvl = tail * (0.9 + 0.5 * lo) + 0.025 + kick * 0.4 * step(0.4, tail);
    vec3 col = c * gl * lvl;
    col += mix(c, u_color1, 0.55) * gl * isHead * (1.6 + kick);
    return col;
}

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float lo = clamp(u_low, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    float cols = max(floor(u_columns + 0.5), 1.0);

    vec2 g;
    float rows, mask = 1.0;
    if (u_surface > 0.5) {
        // techo: columnas alrededor del centro, la lluvia cae hacia la corona
        vec2 p = uv - 0.5;
        float r = length(p) * 2.0;
        float a = atan(p.y, p.x) / 6.28318 + 0.5;
        float around = cols * 8.0;
        float cwPx = 3.14159 * u_res.x / around;
        float chPx = cwPx * 1.35;
        rows = 0.72 * u_res.x / chPx;
        g = vec2(a * around, (1.44 - r) * 0.5 * u_res.x / chPx);
        mask = smoothstep(0.08, 0.22, r);
    } else {
        float N = max(floor(u_panels + 0.5), 1.0);
        float total = N * cols;
        float cwPx = u_res.x / total;
        rows = u_res.y / (cwPx * 1.35);
        g = vec2(uv.x * total, (1.0 - uv.y) * rows);
    }

    // glitch: filas que se corren de lado por un instante
    float band = floor(g.y);
    float jt = floor(u_time * 9.0);
    if (hash21(vec2(band, jt)) < u_glitch * (0.08 + 0.15 * kick))
        g.x += (hash21(vec2(band, jt + 1.0)) - 0.5) * 4.0 * u_glitch;

    vec3 col = rain(g, rows, u_speed, 0.0, lo, kick);
    // capas lejanas: más chicas, más lentas, más tenues
    col += rain(g * 1.8 + vec2(0.37, 0.0), rows * 1.8, u_speed * 0.6, 1.0, lo, kick * 0.5) * 0.25 * u_depth;
    col += rain(g * 3.0 + vec2(0.71, 0.0), rows * 3.0, u_speed * 0.4, 2.0, lo, 0.0) * 0.1 * u_depth;

    col *= mask * u_intensity * (0.75 + 0.35 * e);
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
