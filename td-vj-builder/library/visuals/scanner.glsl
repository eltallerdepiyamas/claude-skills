// scanner.glsl — base7 · Escáner (CORONA x FUTURE x ULTRA)
// Pensado para las 8 columnas en Repartido (canvas ≈ 2.4:1). Líneas horizontales que suben y
// bajan por cada columna como un escáner que mide a la gente. Phase = desfase entre columnas:
// 0 = todas juntas (anillo de luz que sube y baja) · 1 = una ola completa alrededor del booth.
// Marcas de medición en el borde de cada columna. El kick sacude las líneas.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo: un solo escáner de cuadros concéntricos

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–3    ciclos por segundo (aprox.)
uniform float u_glitch;      // 3 distorsión · 0–1    saltos de las líneas con el kick
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_phase;       // 5 firma      · 0–1    0 = en fase · 1 = ola alrededor del booth

// extras
uniform float u_lines;       // 1–6   líneas por columna
uniform float u_panels;      // 1–16  columnas en el canvas (8 = booth)
uniform float u_ticks;       // 0–1   marcas de medición

uniform float u_white;       // 0–0.5  fracción blanca (0.1 = paleta)

out vec4 fragColor;

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

#define TAU 6.2831853

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

void main() {
    vec2 uv = vUV.st;
    float N = u_surface > 0.5 ? 1.0 : max(floor(u_panels + 0.5), 1.0);
    if (u_surface > 0.5) {      // techo: las líneas son cuadros que van del borde a la corona y regresan
        vec2 c = uv - 0.5;
        uv = vec2(0.5, 1.0 - max(abs(c.x), abs(c.y)) * 2.0);
    }
    float e = clamp(u_bass, 0.0, 2.0);
    float kick = clamp(u_kick, 0.0, 1.5);
    float px = 1.0 / u_res.y;

    float i = floor(uv.x * N);
    float lx = fract(uv.x * N);
    float L = max(floor(u_lines + 0.5), 1.0);
    float t = u_time * u_speed * 0.5;

    vec3 col = vec3(0.0);
    vec3 lc = pick(colRank(i, N));                         // cada columna, un color
    for (int k = 0; k < 6; k++) {
        if (float(k) >= L) break;
        float fk = float(k);
        float ph = t * TAU + i / N * u_phase * TAU + fk / L * TAU;
        float ly = 0.5 + 0.47 * sin(ph);
        float vel = cos(ph);
        // salto con el kick: cada columna se corre distinto
        ly += (hash21(vec2(i, fk + floor(u_time * 10.0))) - 0.5) * u_glitch * kick * 0.25;

        float dy = uv.y - ly;
        float w = px * (1.2 + 3.0 * e);
        float core = exp(-dy * dy / (w * w)) + exp(-abs(dy) / (px * 12.0)) * 0.25;
        float behind = -dy * sign(vel);                     // estela del lado contrario al movimiento
        float trail = step(0.0, behind) * exp(-behind / (0.012 + 0.05 * e + 0.04 * abs(vel)));
        vec3 lk = u_surface > 0.5 ? pick(colRank(fk, L)) : lc;   // techo: cada cuadro, un color
        col += lk * core + lk * trail * 0.22;
    }

    // marcas de medición en el borde izquierdo de cada columna (cada 1/20 del alto; largas cada 1/4)
    float d20 = abs(fract(uv.y * 20.0 + 0.5) - 0.5) / 20.0;
    float d4  = abs(fract(uv.y * 4.0 + 0.5) - 0.5) / 4.0;
    float tlen = d4 < px * 1.5 ? 0.18 : 0.07;
    float tick = step(lx, tlen) * (1.0 - smoothstep(px * 0.5, px * 1.5, d20));
    col += u_color1 * tick * u_ticks * 0.25;
    // borde de columna
    float edge = 1.0 - smoothstep(0.0, 1.5 * N / u_res.x, min(lx, 1.0 - lx));
    col += u_color4 * edge * 0.04;

    col *= u_intensity * (0.8 + 0.4 * e);
    col = tonemap(col, 1.4);
    col += u_color3;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
