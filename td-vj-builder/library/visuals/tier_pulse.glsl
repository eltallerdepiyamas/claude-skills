// tier_pulse.glsl — base4 · Escalones (CORONA x FUTURE x ULTRA)
// Ecualizador arquitectónico en dos versiones (u_surface):
//  TECHO (1): anillos cuadrados alineados con los escalones físicos (planta 1:1, booth_geo.uv_planar):
//             graves → escalón exterior · medios → medio · agudos → interior · kick → panel central.
//  COLUMNAS (0): cada columna = las mismas 3 bandas apiladas (graves abajo, medios, agudos arriba)
//             con líneas que suben; el kick enciende el marco de las columnas (el "panel central").
//             Canvas = tira de u_panels columnas (repartido).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_low;         // graves suavizados
uniform float u_mid;         // medios suavizados
uniform float u_high;        // agudos suavizados
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–4    líneas que viajan hacia afuera
uniform float u_twist;       // 3 distorsión · 0–1    giro por escalón + quiebres
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_lines;       // 5 firma      · 1–12   líneas por escalón

// extras
uniform float u_floor;       // 0–0.5  brillo mínimo de los escalones sin audio
uniform float u_center;      // 0–1    flash del panel central con el kick
uniform float u_panels;      // 1–16   columnas en el canvas (8 = booth)

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

// bordes de cada escalón en distancia de Chebyshev desde el centro (uv), de booth_geo.techo():
// centro 0–0.058 · escalón 1: 0.087–0.179 · escalón 2: 0.184–0.275 · escalón 3: 0.292–0.384
const vec2 T1 = vec2(0.087, 0.179);
const vec2 T2 = vec2(0.184, 0.275);
const vec2 T3 = vec2(0.292, 0.384);
const float TC = 0.058;

mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

float hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

// un escalón: líneas cuadradas que viajan hacia afuera dentro de [r0, r1]
float tier(vec2 c, vec2 r, float level, float idx, float t, float aa) {
    vec2 q = rot(u_twist * 0.35 * (idx - 2.0) + u_twist * 0.15 * sin(t * 0.4 + idx)) * c;
    float d = max(abs(q.x), abs(q.y));
    float inside = smoothstep(r.x - aa, r.x + aa, d) * (1.0 - smoothstep(r.y - aa, r.y + aa, d));
    float x = (d - r.x) / (r.y - r.x);              // 0..1 a través del escalón
    float n = max(floor(u_lines + 0.5), 1.0);
    float f = fract(x * n - t * (0.4 + 0.3 * idx));
    float w = 0.12 + 0.5 * level;                   // más audio = líneas más gruesas
    float lines = smoothstep(0.0, 0.08, f) * (1.0 - smoothstep(w, w + 0.08, f));
    // quiebre: un lado del cuadrado se apaga a ratos
    float side = (abs(q.x) > abs(q.y)) ? (q.x > 0.0 ? 0.0 : 1.0) : (q.y > 0.0 ? 2.0 : 3.0);
    float brk = step(1.0 - u_twist * 0.4, hash11(side + idx * 7.0 + floor(t * 3.0)));
    float lit = u_floor + level;
    return inside * (lines * lit + 0.15 * lit) * (1.0 - brk);
}

// COLUMNAS: tres bandas apiladas por columna, líneas que suben; marco con el kick
vec3 columns(vec2 uv, float t, float lo, float mi, float hi, float kick) {
    float N = max(floor(u_panels + 0.5), 1.0);
    float i = floor(uv.x * N);
    vec2 lu = vec2(fract(uv.x * N), uv.y);
    float aa = 1.5 / u_res.y;
    float z = floor(lu.y * 3.0);                    // 0 graves · 1 medios · 2 agudos
    float zy = fract(lu.y * 3.0);
    float level = z < 0.5 ? lo : (z < 1.5 ? mi : hi);
    float n = max(floor(u_lines + 0.5), 1.0);
    float f = fract(zy * n - t * (0.4 + 0.3 * (3.0 - z)) - i * u_twist * 0.13);
    float w = 0.12 + 0.5 * level;
    float lines = smoothstep(0.0, 0.08, f) * (1.0 - smoothstep(w, w + 0.08, f));
    float gap = step(0.04, zy) * step(zy, 0.96);    // separación entre bandas
    float side = step(0.08, lu.x) * step(lu.x, 0.92);
    float lit = u_floor + level;
    float band = (lines * lit + 0.15 * lit) * gap * side;
    // marco de la columna con el kick (eco del panel central del techo)
    vec2 d = min(lu, 1.0 - lu) * vec2(u_res.x / N, u_res.y);
    float frame = 1.0 - smoothstep(1.5, 3.0, min(d.x, d.y));
    float lid = floor(zy * n - t * (0.4 + 0.3 * (3.0 - z)) - i * u_twist * 0.13);   // cada línea elige color
    vec3 col = pick(hash21(vec2(i * 7.0 + z, lid))) * band
             + u_color1 * frame * (0.08 + u_center * kick);
    return col;
}

void main() {
    vec2 uv = vUV.st;
    vec2 c = uv - 0.5;
    float t = u_time * u_speed;
    float aa = 1.5 / u_res.y;

    float lo = clamp(u_low, 0.0, 1.5);
    float mi = clamp(u_mid, 0.0, 1.5);
    float hi = clamp(u_high, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);

    if (u_surface < 0.5) {
        vec3 cc = columns(uv, t, lo, mi, hi, kick) * u_intensity;
        cc /= max(1.0, max(cc.r, max(cc.g, cc.b)));
        fragColor = TDOutputSwizzle(vec4(cc + u_color3, 1.0));
        return;
    }

    float a3 = tier(c, T3, lo, 3.0, t, aa);         // exterior ← graves
    float a2 = tier(c, T2, mi, 2.0, t, aa);         // medio    ← medios
    float a1 = tier(c, T1, hi, 1.0, t, aa);         // interior ← agudos

    float dc = max(abs(c.x), abs(c.y));
    float core = 1.0 - smoothstep(TC - aa, TC + aa, dc);
    float centre = core * (0.12 + u_center * kick + 0.2 * u_bass);

    // halo tenue fuera de los escalones (lee la forma aunque no haya audio)
    float halo = exp(-abs(dc - T3.y) * 40.0) * 0.08 * (0.5 + lo);

    float sec = floor((atan(c.y, c.x) / 6.28318 + 0.5) * 24.0);   // escalones en 24 sectores, cada uno elige color
    vec3 col = pick(hash21(vec2(sec, 1.0))) * a1
             + pick(hash21(vec2(sec, 2.0))) * a2
             + pick(hash21(vec2(sec, 3.0))) * a3
             + u_color1 * centre
             + u_color4 * halo;
    col *= u_intensity;
    col /= max(1.0, max(col.r, max(col.g, col.b)));   // satura sin lavar el acento
    col += u_color3;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
