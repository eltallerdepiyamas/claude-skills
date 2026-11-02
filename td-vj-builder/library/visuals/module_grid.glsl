// module_grid.glsl — base12 · Módulos (CORONA x FUTURE x ULTRA)
// De la referencia cenital: una retícula de módulos de andamio; cada módulo tiene un cuadro de
// luz al centro entre humo, con la diagonal del andamio en silueta encima y tiles chicos en los
// bordes. Los centros respiran con los graves, algunos laten solos, el kick los prende todos.
// u_surface: 0 = columnas (módulos apilados por columna) · 1 = techo: el techo completo es UN módulo
// gigante, como la referencia cenital: cuadro de luz = panel central (corona), diagonales cruzando todo.
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
uniform float u_speed;       // 2 velocidad  · 0–3    respiración / latidos
uniform float u_strut;       // 3 distorsión · 0–1    silueta del andamio (diagonales y marco)
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_rows;        // 5 firma      · 2–10   módulos por alto

// extras
uniform float u_density;     // 0–1    módulos que laten solos
uniform float u_haze;        // 0–1    humo alrededor de cada centro
uniform float u_panels;      // 1–16   columnas en el canvas (8 = booth)

uniform float u_white;       // 0–0.5  fracción blanca (0.1 = paleta)

out vec4 fragColor;

// paleta del cliente por elemento: White → blanco · Accent → amarillo · resto → azul
vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 tonemap(vec3 c, float k) {
    float m = max(c.r, max(c.g, c.b));
    return m > 1e-5 ? c * (1.0 - exp(-m * k)) / m : c;
}

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float lo = clamp(u_low, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);

    float N = u_surface > 0.5 ? 1.0 : max(floor(u_panels + 0.5), 1.0);
    float rows = u_surface > 0.5 ? 1.0 : max(floor(u_rows + 0.5), 1.0);
    float panelW = u_res.x / N;
    float cellH = u_res.y / rows;
    float cpp = max(1.0, floor(panelW / cellH + 0.5));
    vec2 g = vec2(uv.x * N * cpp, uv.y * rows);
    vec2 id = floor(g);
    vec2 cs = vec2(panelW / cpp, cellH);
    vec2 fp = (fract(g) - 0.5) * cs;                // px desde el centro del módulo
    float s = min(cs.x, cs.y);

    // nivel de luz del módulo: respiración con graves + latidos sueltos + kick
    float breath = 0.25 + 0.75 * (0.5 + 0.5 * sin(u_time * u_speed * 1.3 + hash21(id) * 6.28));
    float beat = step(1.0 - u_density * (0.3 + 0.4 * e), hash21(id + floor(u_time * u_speed * 2.0)));
    float level = breath * (0.25 + 0.75 * lo) + beat * 0.8 + kick * 0.9;

    // cuadro central + humo + tiles en los bordes
    float half_ = s * (u_surface > 0.5 ? 0.058 : 0.12);   // techo: = panel central (booth_geo TC)
    float core = 1.0 - smoothstep(half_ - 1.0, half_ + 1.0, max(abs(fp.x), abs(fp.y)));
    float fog = exp(-length(fp) / (s * mix(0.1, 0.45, u_haze))) * u_haze * 0.6;
    vec2 a = abs(fp);
    float edgeTile = (1.0 - smoothstep(s * 0.035, s * 0.035 + 1.0, min(abs(a.x - s * 0.42), abs(a.y - s * 0.42))))
                   * step(min(a.x, a.y), s * 0.05);
    vec3 mc = pick(hash21(id + 4.4));
    vec3 col = mc * (core * level * 1.2 + fog * level) + u_color4 * edgeTile * (0.15 + 0.5 * kick);

    // silueta del andamio encima (diagonal alternada + marco del módulo)
    float flip = mod(id.x + id.y, 2.0) > 0.5 ? -1.0 : 1.0;
    float diag = abs(fp.x * flip - fp.y * (cs.x / cs.y)) / sqrt(1.0 + (cs.x / cs.y) * (cs.x / cs.y));
    float strut = 1.0 - smoothstep(s * 0.025, s * 0.025 + 1.5, diag);
    float frame = 1.0 - smoothstep(s * 0.02, s * 0.02 + 1.5, min(cs.x * 0.5 - a.x, cs.y * 0.5 - a.y));
    col *= 1.0 - u_strut * 0.92 * max(strut, frame);

    col *= u_intensity;
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
