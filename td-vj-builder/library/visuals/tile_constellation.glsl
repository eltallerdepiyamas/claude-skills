// tile_constellation.glsl — base2 · Constelación de tiles (CORONA x FUTURE x ULTRA)
// De las referencias (torres de andamio con paneles sueltos): pocos tiles de luz —cuadros y
// rombos— en la oscuridad, cada uno se enciende entero y se apaga solo, con halo de humo.
// El audio sube la cantidad; el kick prende un grupo al mismo tiempo. Mucho negro.
// u_surface: 0 = columnas (retícula alineada a cada columna) · 1 = techo (retícula cuadrada).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–3    ritmo de encendidos
uniform float u_drift;       // 3 distorsión · 0–1    los tiles saltan de lugar con el kick
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_rows;        // 5 firma      · 3–16   tiles por alto

// extras
uniform float u_density;     // 0–1    cuántos tiles se encienden
uniform float u_haze;        // 0–1    halo de humo
uniform float u_diamond;     // 0–1    fracción de rombos (vs cuadros)
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
    float kick = clamp(u_kick, 0.0, 1.5);

    // retícula alineada a las columnas (o cuadrada en el techo)
    float N = u_surface > 0.5 ? 1.0 : max(floor(u_panels + 0.5), 1.0);
    float rows = max(floor(u_rows + 0.5), 1.0);
    float panelW = u_res.x / N;
    float cellH = u_res.y / rows;
    float cpp = max(1.0, floor(panelW / cellH + 0.5));
    vec2 g = vec2(uv.x * N * cpp, uv.y * rows);
    vec2 id = floor(g);
    vec2 cs = vec2(panelW / cpp, cellH);               // tamaño de celda en px
    vec2 fp = (fract(g) - 0.5) * cs;                   // posición en px desde el centro de la celda
    float s = min(cs.x, cs.y);

    // cada tile tiene su propio ciclo: se enciende (o no) y decae
    float r = u_speed * (0.25 + 0.75 * hash21(id + 1.3));
    float ph = u_time * r + hash21(id) * 7.0;
    float cyc = floor(ph);
    float on = step(1.0 - u_density * (0.25 + 0.45 * e), hash21(id + cyc * 13.1));
    float env = exp(-fract(ph) * 5.0) * on;
    // kick: un grupo al mismo tiempo
    float kgrp = step(1.0 - 0.18 * kick, hash21(id + floor(u_time * 4.0) * 3.7));
    env = max(env, kgrp * kick);

    // salto de lugar con el kick
    fp += (vec2(hash21(id + cyc), hash21(id - cyc)) - 0.5) * s * 0.4 * u_drift * kick;

    // forma: cuadro o rombo
    vec2 q = fp;
    if (hash21(id + 5.5) < u_diamond) q = vec2(q.x + q.y, q.y - q.x) * 0.7071;
    float half_ = s * 0.18;
    float tile = 1.0 - smoothstep(half_ - 1.0, half_ + 1.0, max(abs(q.x), abs(q.y)));
    float glow = exp(-length(fp) / (s * mix(0.08, 0.4, u_haze))) * u_haze;

    vec3 tc = pick(hash21(id + 9.1));
    vec3 col = tc * (tile * env * 1.3 + glow * env * 0.7) + u_color4 * tile * 0.025;   // tile apagado apenas visible
    col *= u_intensity;
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
