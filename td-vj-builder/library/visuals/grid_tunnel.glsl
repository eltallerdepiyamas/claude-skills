// grid_tunnel.glsl — base17 · Túnel de rejilla (CORONA x FUTURE x ULTRA)
// Ref. cliente pinterest6: corredor cuadrado de rejilla de neón visto de frente, avanzando; bloques
// oscuros detrás de las líneas, punto de fuga brillante. Los anillos del túnel vienen hacia ti.
// Paleta del cliente: líneas largas azules; cada anillo / bloque elige 70% azul · 20% amarillo · 10% blanco.
// u_surface: 0 = columnas (un túnel por tira, con la forma de la tira) · 1 = techo: el techo escalonado es el
// túnel; anillos que salen de la corona y suben por los escalones, ver tunnelTecho().
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
uniform float u_speed;       // 2 velocidad  · 0–3    avance
uniform float u_twist;       // 3 distorsión · 0–1    giro del túnel con la profundidad
uniform float u_accent;      // 4 color      · 0–1    fracción de anillos amarillos (0.2 = paleta)
uniform float u_cells;       // 5 firma      · 2–16   divisiones de cada pared

// extras
uniform float u_blocks;      // 0–1    bloques rellenos en las paredes
uniform float u_glow;        // 0–1    brillo del punto de fuga
uniform float u_white;       // 0–0.5  fracción de anillos blancos (0.1 = paleta)
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

vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

float gridLine(float x, float w) {
    float d = abs(fract(x) - 0.5) * 2.0;           // 1 en la línea
    float aa = min(fwidth(x) * 2.0, 0.3);           // en la costura entre paredes fwidth se dispara
    return smoothstep(1.0 - w - aa, 1.0 - w, d);
}

// techo (booth_geo.techo): la corona es lo más bajo y los escalones suben hacia afuera → el techo YA es el
// túnel. Anillos cuadrados a paso constante (≈1 por escalón) salen de la corona hacia el borde (subiendo),
// líneas rectas a lo largo de cada brazo parten las barras en celdas. Sin perspectiva: no se amontona al centro.
vec3 tunnelTecho(vec2 uv, float e, float lo, float kick) {
    vec2 c = uv - 0.5;
    float ang = u_twist * 0.6 * sin(u_time * 0.4);
    c = mat2(cos(ang), -sin(ang), sin(ang), cos(ang)) * c;
    float d = max(abs(c.x), abs(c.y));
    bool side = abs(c.x) > abs(c.y);
    float wall = side ? (c.x > 0.0 ? 0.0 : 2.0) : (c.y > 0.0 ? 1.0 : 3.0);
    float tg = side ? c.y : c.x;
    float cells = max(floor(u_cells + 0.5), 1.0);
    float v = d * 11.0 - u_time * u_speed * 0.9;               // ≈1 anillo por escalón, salen de la corona
    float gu = (tg + 0.5) * cells * 1.5;                        // pocas celdas grandes a lo ancho del brazo

    float lu = gridLine(gu, 0.06);
    float lv = gridLine(v, 0.09);
    vec2 cid = vec2(floor(gu) + wall * 31.0, floor(v));
    float ringId = floor(v + 0.5);
    vec3 cRing = pick(hash21(vec2(ringId, 7.0)));
    float flash = kick * step(0.6, hash21(vec2(ringId, floor(u_time * 4.0))));
    float block = step(1.0 - u_blocks * 0.6, hash21(cid)) * (0.06 + 0.12 * hash21(cid + 3.0));
    float lit = step(0.97, hash21(cid + 9.0 + floor(u_time * u_speed * 2.0))) * (0.6 + lo);

    vec3 col = u_color4 * lu * 0.8;
    col += cRing * lv * (1.0 + flash * 1.5);
    col += pick(hash21(cid + 1.7)) * (block * (0.6 + 0.5 * e) + lit * 0.5) * (1.0 - max(lu, lv));
    col += mix(u_color4, u_color1, 0.35) * (1.0 - smoothstep(0.05, 0.062, d)) * u_glow * (0.8 + 0.6 * e + kick);   // corona
    return col;
}

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float lo = clamp(u_low, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    if (u_surface > 0.5) {
        vec3 tc = tunnelTecho(uv, e, lo, kick) * u_intensity;
        fragColor = TDOutputSwizzle(vec4(tonemap(tc, 1.3) + u_color3, 1.0));
        return;
    }

    float N = u_surface > 0.5 ? 1.0 : max(floor(u_panels + 0.5), 1.0);
    vec2 p = vec2(fract(uv.x * N), uv.y) * 2.0 - 1.0;   // -1..1 en el marco (túnel con la forma de la tira)
    float d0 = max(abs(p.x), abs(p.y));
    float z0 = 1.0 / max(d0, 1e-3);
    float ang = u_twist * 0.35 * z0 + u_twist * 0.3 * sin(u_time * 0.4);
    p = mat2(cos(ang), -sin(ang), sin(ang), cos(ang)) * p;

    float d = max(abs(p.x), abs(p.y));
    float z = 1.0 / max(d, 1e-3);                      // profundidad
    bool side = abs(p.x) > abs(p.y);
    float u = side ? p.y / abs(p.x) : p.x / abs(p.y);  // -1..1 a lo ancho de la pared
    float wall = side ? (p.x > 0.0 ? 0.0 : 2.0) : (p.y > 0.0 ? 1.0 : 3.0);
    float cells = max(floor(u_cells + 0.5), 1.0);
    float travel = u_time * u_speed * 1.5;
    float v = z * cells * 0.5 + travel;                 // anillos: celdas cuadradas en la pared
    float gu = (u * 0.5 + 0.5) * cells;

    float lu = gridLine(gu, 0.08);                     // líneas largas (hacia el fondo), incluye las esquinas
    float lv = gridLine(v + 0.5, 0.07);                // anillos
    vec2 cid = vec2(floor(gu) + wall * 31.0, floor(v));
    float ringId = floor(v + 0.5);

    vec3 cRing = pick(hash21(vec2(ringId, 7.0)));
    float flash = kick * step(0.6, hash21(vec2(ringId, floor(u_time * 4.0))));
    float hb = hash21(cid);
    float block = step(1.0 - u_blocks * 0.6, hb) * (0.06 + 0.12 * hash21(cid + 3.0));
    float lit = step(0.985, hash21(cid + 9.0 + floor(u_time * u_speed * 2.0))) * (0.6 + lo);

    vec3 col = u_color4 * lu * 0.9;
    col += cRing * lv * (1.0 + flash * 1.5);
    col += pick(hash21(cid + 1.7)) * (block * (0.6 + 0.5 * e) + lit * 0.5) * (1.0 - max(lu, lv));

    float fog = smoothstep(0.02, 0.25, d);             // al fondo se funde en el brillo
    col *= fog * (0.55 + 0.45 * smoothstep(0.0, 0.6, d));
    col += mix(u_color4, u_color1, 0.35) * exp(-d * 9.0) * u_glow * (0.8 + 0.6 * e);

    col *= u_intensity;
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
