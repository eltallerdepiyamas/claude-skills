// datamatics.glsl — base3 · Datamatics (CORONA x FUTURE x ULTRA)
// Estilo de instalación de datos (en la línea de Ryoji Ikeda): blanco y negro puro, pixel exacto,
// números que corren, códigos de barras, líneas finísimas, gráficas y estrobo binario.
// Cada columna es una "pantalla de datos"; en cada kick (u_step) cada columna cambia de modo:
//   0 números · 1 código de barras · 2 líneas finas · 3 gráfica (onda sobre retícula de puntos)
// En los picos el estrobo invierte columnas sueltas. u_surface 1 (techo): una sola pantalla cuadrada
// que mezcla retícula de puntos, cruz de medición y números.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_high;        // agudos suavizados
uniform float u_kick;        // kick crudo
uniform float u_step;        // paso (página Secuencia: kick o BPM)
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–4    corrimiento de datos
uniform float u_glitch;      // 3 distorsión · 0–1    cortes horizontales y saltos
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_density;     // 5 firma      · 0.1–1  densidad de datos

// extras
uniform float u_glyph;       // 1–6   tamaño del pixel de los números (px)
uniform float u_strobe;      // 0–1   inversión binaria en los picos
uniform float u_panels;      // 1–16  columnas en el canvas (8 = booth)

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

// dígito 3x5 (bit 14 = arriba-izquierda)
int digitMask(int d) {
    if (d == 0) return 31599;
    if (d == 1) return 9362;
    if (d == 2) return 29671;
    if (d == 3) return 29391;
    if (d == 4) return 23497;
    if (d == 5) return 31183;
    if (d == 6) return 31215;
    if (d == 7) return 29257;
    if (d == 8) return 31727;
    return 31695;
}

// px = posición en pixeles dentro del área; gp = tamaño de pixel del glifo
float numbers(vec2 px, float gp, vec2 seed, float t, float dens) {
    vec2 cell = vec2(4.0, 7.0) * gp;                       // 3x5 + separación
    float row = floor(px.y / cell.y);
    float rs = (hash21(vec2(row, seed.x)) - 0.5) * 2.0;     // velocidad / sentido por renglón
    px.x += t * rs * 60.0 * gp;
    vec2 cid = floor(px / cell);
    vec2 gpx = floor(mod(px, cell) / gp);                   // pixel del glifo (0..3, 0..6)
    if (gpx.x > 2.0 || gpx.y > 4.0) return 0.0;
    float on = step(1.0 - dens, hash21(cid + seed * 7.0 + floor(cid.x / 6.0)));
    int d = int(floor(hash21(cid + floor(t * 6.0 + hash21(cid) * 4.0)) * 10.0));
    int idx = int(4.0 - gpx.y) * 3 + int(gpx.x);
    return float((digitMask(d) >> (14 - idx)) & 1) * on;
}

float barcode(vec2 px, float h, float seed, float t, float dens) {
    float y = px.y + t * 900.0 * (0.5 + hash21(vec2(seed, 2.0)));
    float unit = floor(mix(2.0, 6.0, hash21(vec2(seed, 5.0))));
    float b = floor(y / unit);
    return step(1.0 - dens * 0.8, hash21(vec2(b, seed)));
}

float thinLines(vec2 px, vec2 size, float seed, float t) {
    float v = 0.0;
    for (int k = 0; k < 6; k++) {
        float fk = float(k);
        float sp = (hash21(vec2(fk, seed)) - 0.5) * 2.0;
        float y = fract(hash21(vec2(seed, fk)) + t * sp * 0.15) * size.y;
        v += step(abs(px.y - y), 0.5);                      // línea de 1 px
        // marcas pequeñas sobre la línea
        v += step(abs(px.y - y - 4.0), 2.0) * step(mod(px.x + fk * 7.0, 24.0), 1.0);
    }
    return min(v, 1.0);
}

float plot(vec2 px, vec2 size, float seed, float t, float e) {
    vec2 uv = px / size;
    float f = mix(4.0, 18.0, hash21(vec2(seed, 9.0)));
    float x = 0.5 + 0.38 * sin(uv.y * f + t * 3.0) * (0.4 + 0.6 * e) * sin(uv.y * 2.3 - t);
    float line = step(abs(uv.x - x) * size.x, 0.75);
    vec2 g = mod(px, 12.0);
    float dots = step(g.x, 0.9) * step(g.y, 0.9) * 0.5;
    float axis = step(abs(uv.x - 0.5) * size.x, 0.5) * 0.4;
    return max(line, max(dots, axis));
}

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    float t = u_time * u_speed;
    float st = floor(u_step);
    float gp = max(floor(u_glyph + 0.5), 1.0);
    float dens = clamp(u_density * (0.7 + 0.4 * e), 0.0, 1.0);

    float N = u_surface > 0.5 ? 1.0 : max(floor(u_panels + 0.5), 1.0);
    float i = floor(uv.x * N);
    vec2 size = vec2(u_res.x / N, u_res.y);
    vec2 px = vec2(fract(uv.x * N), uv.y) * size;

    // cortes horizontales (glitch): bandas que saltan de lado
    float band = floor(px.y / 24.0);
    float gt = floor(u_time * 12.0);
    float cut = step(1.0 - u_glitch * (0.1 + 0.3 * hi), hash21(vec2(band + i * 31.0, gt)));
    px.x = mod(px.x + cut * (hash21(vec2(band, gt + 3.0)) - 0.5) * size.x, size.x);

    float v;
    if (u_surface > 0.5) {
        // techo: retícula de puntos + cruz de medición + números en las esquinas + barras en los bordes
        vec2 c = px - size * 0.5;
        vec2 g = mod(px, 16.0);
        float dots = step(g.x, 0.9) * step(g.y, 0.9) * 0.45;
        float cross = step(min(abs(c.x), abs(c.y)), 0.5) * 0.8;
        float ring = step(abs(max(abs(c.x), abs(c.y)) - mod(t * 120.0, size.x * 0.5)), 0.6);
        float nums = numbers(px, gp, vec2(st, 1.0), t, dens) * step(0.3, max(abs(c.x), abs(c.y)) / size.x);
        v = max(max(dots, cross), max(ring, nums));
    } else {
        float m = floor(hash21(vec2(i, st)) * 4.0);
        vec2 seed = vec2(i + st * 0.37, i);
        if (m < 1.0)      v = numbers(px, gp, seed, t, dens);
        else if (m < 2.0) v = barcode(px, size.y, seed.x, t, dens);
        else if (m < 3.0) v = thinLines(px, size, seed.x, t);
        else              v = plot(px, size, seed.x, t, e);
    }

    // estrobo binario en los picos: columnas sueltas se invierten
    float inv = step(1.0 - u_strobe * smoothstep(0.6, 1.2, kick) * 0.5, hash21(vec2(i, floor(u_time * 15.0))));
    v = abs(v - inv);

    // borde de 1 px entre columnas (la retícula siempre se lee)
    float edge = step(px.x, 0.5) * 0.25;
    vec3 dc = pick(hash21(vec2(i, st + 2.0)));               // cada columna de datos, un color por paso
    vec3 col = dc * max(v, edge) * u_intensity;
    col = min(col, vec3(1.0));
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
