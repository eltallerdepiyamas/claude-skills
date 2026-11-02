// industrial_grid.glsl — base1 · Rejilla industrial (CORONA x FUTURE x ULTRA)
// Rejilla de acero sobre placas metálicas cepilladas. Una segunda rejilla casi igual,
// apenas girada, crea moiré. El audio enciende celdas, abre cortes horizontales
// (interferencia de señal) y empuja el brillo de las líneas. Barrido vertical tipo escáner.
// Techno industrial: negro, acero, blanco; Color2 = acento (pendiente de definir).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy: bandas activas, suavizadas (página Audio)
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo general
uniform float u_speed;       // 2 velocidad  · 0–4    scroll, barrido, ritmo de cortes
uniform float u_warp;        // 3 distorsión · 0–1    cortes horizontales + ondulación
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_cells;       // 5 firma      · 4–48   densidad de la rejilla (celdas en vertical)

// extras
uniform float u_moire;       // 0–1      presencia de la segunda rejilla (moiré)
uniform float u_line;        // 0.02–0.3 grosor de línea (fracción de celda)

uniform float u_white;       // 0–0.5  fracción blanca (0.1 = paleta)

out vec4 fragColor;

// paleta del cliente por elemento: White → blanco · Accent → amarillo · resto → azul
vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

float hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i),                 hash21(i + vec2(1.0, 0.0)), u.x),
               mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), u.x), u.y);
}

mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

// líneas de rejilla con antialias: p en unidades de pantalla, cells por unidad
float grid(vec2 p, float cells, float width, float px) {
    vec2 g = abs(fract(p * cells) - 0.5);
    float d = 0.5 - max(g.x, g.y);              // distancia a la línea más cercana (en celdas)
    float aa = px * cells * 1.5;
    return 1.0 - smoothstep(width * 0.5, width * 0.5 + aa, d);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = u_res.x / u_res.y;
    vec2 p = (uv - 0.5) * vec2(aspect, 1.0);    // alto = 1 → celdas cuadradas en cualquier aspecto
    float px = 1.0 / u_res.y;
    float t = u_time * u_speed;
    float e = clamp(u_bass, 0.0, 2.0);

    // ── interferencia: bandas horizontales que se desplazan (cortes de señal)
    float rows = mix(10.0, 46.0, hash11(floor(t * 1.5)));
    float band = floor(uv.y * rows);
    float tick = floor(t * 8.0);
    float on = step(1.0 - (u_warp * 0.35 + e * 0.25), hash21(vec2(band, tick)));
    float shift = (hash21(vec2(band, tick + 17.0)) - 0.5) * (0.08 + 0.5 * e) * u_warp;
    p.x += shift * on;
    // ondulación lenta, como chapa que vibra
    p += u_warp * 0.025 * vec2(sin(p.y * 7.0 + t * 0.9), sin(p.x * 5.0 - t * 0.6));

    vec2 q = p + vec2(0.0, t * 0.04);           // scroll vertical lento
    float cells = max(u_cells, 1.0);

    // ── placas metálicas: tono por celda + cepillado horizontal
    vec2 cid = floor(q * cells);
    float plate = hash21(cid);
    float brushed = noise(vec2(q.x * 3.0, q.y * u_res.y * 0.35));
    float metal = 0.035 + 0.05 * plate + 0.035 * brushed;

    // celdas encendidas por el audio (y unas pocas al azar)
    float lit = step(1.0 - (0.015 + e * 0.11), hash21(cid + floor(t * 3.0) * 7.31));

    // ── líneas: rejilla principal + subrejilla fina + rejilla girada (moiré)
    float g1 = grid(q, cells, u_line, px);
    float g2 = grid(q, cells * 4.0, u_line * 0.5, px) * 0.22;
    float g3 = grid(rot(0.035 + 0.015 * sin(t * 0.21)) * q * 1.025, cells, u_line * 0.8, px) * u_moire;
    float lines = max(max(g1, g2), g3 * 0.8);

    // barrido vertical tipo escáner
    float scanY = fract(t * 0.12) * 1.4 - 0.2;
    float scan = exp(-pow((uv.y - scanY) * 18.0, 2.0));

    vec3 lineCol = pick(hash21(cid + 3.7));                  // cada celda elige color (70/20/10)
    vec3 col = u_color3 + metal * mix(vec3(0.75, 0.8, 0.88), u_color4, 0.5);
    col += pick(hash21(cid + 5.1)) * lit * (0.35 + 0.65 * e);
    col += lineCol * lines * (0.45 + 0.9 * e + 1.2 * scan);
    col += u_color1 * scan * 0.06;
    col = mix(col, pick(hash21(vec2(band, tick + 3.0))) * 1.4, on * u_warp * 0.12);   // tinte en los cortes
    col *= u_intensity;

    // viñeta + grano
    vec2 v = uv - 0.5;
    col *= 1.0 - 0.6 * dot(v, v);
    col += (hash21(uv * u_res + fract(u_time) * 311.0) - 0.5) * 0.025;

    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
