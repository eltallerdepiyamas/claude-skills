// data_barcode.glsl — base9 · Código de datos (CORONA x FUTURE x ULTRA)
// Bandas horizontales de código de barras que corren a distintas velocidades y sentidos;
// con los agudos algunas bandas se vuelven flicker binario; el kick invierte bandas al azar.
// Blanco/negro preciso, acento amarillo en pocas barras. Estética de datos (instalación).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_high;        // agudos suavizados
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–4    corrimiento de las bandas
uniform float u_jitter;      // 3 distorsión · 0–1    saltos horizontales de bandas
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_rows;        // 5 firma      · 2–40   bandas por alto

// extras
uniform float u_density;     // 0.1–0.9  qué tan llenas van las barras
uniform float u_flicker;     // 0–1      bandas en flicker binario con los agudos

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

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    float t = u_time * u_speed;

    float rows = max(floor(u_rows + 0.5), 1.0);
    float band = floor(uv.y * rows);
    float by = fract(uv.y * rows);
    float hb = hash21(vec2(band, 3.7));

    // velocidad y sentido por banda; ancho de módulo 2–8 px
    float dir = hb > 0.5 ? 1.0 : -1.0;
    float sp = dir * mix(0.2, 1.0, hash21(vec2(band, 9.1)));
    float unit = floor(mix(2.0, 8.0, hash21(vec2(band, 1.3)))) / u_res.x;
    float jump = (hash21(vec2(band, floor(u_time * 6.0))) - 0.5) * 0.2 * u_jitter
               * step(1.0 - 0.3 * u_jitter - 0.2 * e, hash21(vec2(band, floor(u_time * 6.0) + 0.5)));
    float x = uv.x + t * sp * 0.05 + jump;
    float cell = floor(x / unit);

    // barras: códigos con "palabras" (grupos) para que no sea ruido plano
    float word = floor(cell / 12.0);
    float wordOn = step(0.25, hash21(vec2(word, band + 0.5)));
    float bar = step(1.0 - u_density, hash21(vec2(cell, band))) * wordOn;

    // flicker binario con los agudos
    float flick = step(1.0 - u_flicker * hi * 0.5, hash21(vec2(band, floor(u_time * 3.0) + 11.0)));
    float bin = step(0.5, hash21(vec2(cell, band + floor(u_time * 30.0))));
    bar = mix(bar, bin, flick);

    // kick: invierte bandas al azar
    float inv = step(1.0 - kick * 0.2, hash21(vec2(band, floor(u_time * 8.0) + 5.0)));
    bar = abs(bar - inv);

    // separación fina entre bandas + algunas bandas son solo una línea con marcas
    float gap = step(0.08, by) * step(by, 0.92);
    if (hash21(vec2(band, 7.7)) > 0.82) {
        float line = 1.0 - smoothstep(0.0, 1.5 / (u_res.y / rows), abs(by - 0.5));
        float tick = step(0.94, fract(x * 40.0)) * step(abs(by - 0.5), 0.2);
        bar = max(line, tick) * (1.0 - inv) + inv * gap;
    }
    bar *= gap;

    vec3 col = pick(hash21(vec2(band, 2.0))) * bar;          // cada banda elige color
    col *= u_intensity * (0.75 + 0.35 * e);
    col = min(col, vec3(1.0));
    col += u_color3;
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
