// radar_sweep.glsl — base10 · Radar (CORONA x FUTURE x ULTRA)
// Dos versiones (u_surface), sincronizadas:
//  TECHO (1): barrido que gira alrededor de la corona e ilumina los escalones por segmentos;
//             blips amarillos que se apagan; el kick enciende el contorno de los escalones.
//  COLUMNAS (0): cada columna se enciende cuando el barrido pasa por SU dirección (azimut real
//             de booth_geo.columnas()), con su estela; los blips son tiles a distintas alturas.
//             El giro se lee en todo el booth. Reverse invierte el sentido en columnas por si
//             en el montaje real queda al revés que el techo.
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
uniform float u_speed;       // 2 velocidad  · 0–2    vueltas por segundo
uniform float u_twist;       // 3 distorsión · 0–1    cada escalón gira a otra velocidad
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_segments;    // 5 firma      · 4–64   segmentos por vuelta

// extras
uniform float u_blips;       // 0–1     cantidad de blips
uniform float u_tail;        // 0.05–1  largo de la estela (fracción de vuelta)
uniform float u_reverse;     // 0/1     columnas: invierte el orden del azimut

uniform float u_white;       // 0–0.5  fracción blanca (0.1 = paleta)

out vec4 fragColor;

// paleta del cliente por elemento: White → blanco · Accent → amarillo · resto → azul
vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

#define TAU 6.2831853
// escalones en distancia de Chebyshev desde el centro (uv), igual que tier_pulse
const vec2 T1 = vec2(0.087, 0.179);
const vec2 T2 = vec2(0.184, 0.275);
const vec2 T3 = vec2(0.292, 0.384);
const float TC = 0.058;

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float band(float d, vec2 r, float aa) {
    return smoothstep(r.x - aa, r.x + aa, d) * (1.0 - smoothstep(r.y - aa, r.y + aa, d));
}

// azimut (0..1, igual que ang en el techo) de cada columna en el orden de la tira (booth_geo.columnas)
float azimuth(int i) {
    if (i == 0) return 0.651;
    if (i == 1) return 0.599;
    if (i == 2) return 0.401;
    if (i == 3) return 0.349;
    if (i == 4) return 0.151;
    if (i == 5) return 0.099;
    if (i == 6) return 0.901;
    return 0.849;
}

vec3 columns(vec2 uv, float e, float kick) {
    const float N = 8.0;
    int i = int(clamp(floor(uv.x * N), 0.0, 7.0));
    if (u_reverse > 0.5) i = 7 - i;
    vec2 lu = vec2(fract(uv.x * N), uv.y);
    float az = azimuth(i);
    float rate = u_speed * (1.0 + u_twist * 0.35);          // = escalón exterior del techo
    float sweep = fract(u_time * rate);
    float behind = fract(sweep - az);
    float tail = max(u_tail, 0.02);
    float beam = exp(-behind / (tail * 0.2)) * 0.9 + exp(-behind / tail) * 0.12;
    // lamas horizontales (segmentos) — el número sigue a Segments
    float rows = max(floor(u_segments / 3.0), 3.0);
    float ry = fract(lu.y * rows);
    float slat = step(0.12, ry) * step(ry, 0.88) * step(0.1, lu.x) * step(lu.x, 0.9);
    // blips: tiles a alturas al azar, marcados en cada vuelta
    float rev = floor(u_time * rate - az);
    float row = floor(lu.y * rows);
    float blip = step(1.0 - u_blips * (0.25 + 0.3 * e), fract(sin(dot(vec2(row + float(i) * 31.0, rev), vec2(12.9898, 78.233))) * 43758.5453));
    float blipGlow = blip * exp(-behind / max(tail * 2.5, 0.05));
    vec2 d = min(lu, 1.0 - lu) * vec2(u_res.x / N, u_res.y);
    float frame = 1.0 - smoothstep(1.5, 3.0, min(d.x, d.y));
    vec3 col = u_color4 * beam * slat * (0.7 + 0.4 * e);
    col += pick(hash21(vec2(row + float(i) * 31.0, rev + 0.5))) * blipGlow * slat * 1.2;
    col += mix(u_color4, u_color1, clamp(kick, 0.0, 1.0)) * frame * (0.06 + 0.8 * kick);
    return col;
}

void main() {
    vec2 c = vUV.st - 0.5;
    float e = clamp(u_bass, 0.0, 2.0);
    float kick = clamp(u_kick, 0.0, 1.5);
    if (u_surface < 0.5) {
        vec3 cc = columns(vUV.st, e, kick) * u_intensity;
        cc /= max(1.0, max(cc.r, max(cc.g, cc.b)));
        fragColor = TDOutputSwizzle(vec4(cc + u_color3, 1.0));
        return;
    }
    float aa = 1.5 / u_res.y;
    float d = max(abs(c.x), abs(c.y));
    float ang = atan(c.y, c.x) / TAU + 0.5;               // 0..1

    // en qué escalón estoy (1..3), 0 = fuera
    float b1 = band(d, T1, aa), b2 = band(d, T2, aa), b3 = band(d, T3, aa);
    float tierIdx = b3 > 0.5 ? 3.0 : (b2 > 0.5 ? 2.0 : (b1 > 0.5 ? 1.0 : 0.0));
    float inTier = max(b1, max(b2, b3));

    float N = max(floor(u_segments + 0.5), 1.0);
    float rate = u_speed * (1.0 + u_twist * (tierIdx - 2.0) * 0.35);
    float sweep = fract(u_time * rate);
    float seg = floor(ang * N);
    float segC = (seg + 0.5) / N;
    float behind = fract(sweep - segC);                  // 0 = recién barrido
    float tail = max(u_tail, 0.02);
    float beam = exp(-behind / (tail * 0.2)) * 0.9 + exp(-behind / tail) * 0.12;

    // separación entre segmentos (look de paneles)
    float gapA = 1.0 - smoothstep(0.0, 0.08, min(fract(ang * N), 1.0 - fract(ang * N)));
    beam *= 1.0 - gapA * 0.85;

    // blips: segmentos marcados en cada vuelta, se apagan con la estela larga
    float rev = floor(u_time * rate - segC);
    float blip = step(1.0 - u_blips * (0.12 + 0.2 * e), hash21(vec2(seg + tierIdx * 97.0, rev)));
    float blipGlow = blip * exp(-behind / max(tail * 2.5, 0.05));

    // contorno de escalones (estructura): tenue siempre, fuerte con el kick
    float edge = 0.0;
    for (int k = 0; k < 3; k++) {
        vec2 r = k == 0 ? T1 : (k == 1 ? T2 : T3);
        edge += 1.0 - smoothstep(aa * 0.5, aa * 2.0, min(abs(d - r.x), abs(d - r.y)));
    }
    float core = 1.0 - smoothstep(TC - aa, TC + aa, d);

    vec3 col = u_color4 * beam * inTier * (0.7 + 0.4 * e);
    col += pick(hash21(vec2(seg + tierIdx * 97.0, rev + 0.5))) * blipGlow * inTier * 1.2;
    col += mix(u_color4, u_color1, clamp(kick, 0.0, 1.0)) * edge * (0.08 + 0.8 * kick);
    col += u_color1 * core * (0.15 + 0.6 * kick);
    col *= u_intensity;
    col /= max(1.0, max(col.r, max(col.g, col.b)));
    col += u_color3;
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
