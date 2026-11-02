// shingle_wall.glsl — base15 · Muro de placas (CORONA x FUTURE x ULTRA)
// Ref. cliente pinterest4: muro de placas metálicas que se inclinan con una onda y atrapan la luz.
// v2 (2026-10-23, la v1 de placas chiquitas se leía aplastada): placas GRANDES en retícula alineada
// (pocas por tira), cada una prende como unidad: relleno según hacia dónde mira, una franja de brillo
// que se desliza con la inclinación y un filo claro arriba. Mucho negro entre placas.
// Paleta del cliente por placa: 70% azul · 20% amarillo · 10% blanco (Accent / White la ajustan).
// u_surface: 0 = columnas (placas alineadas a cada tira) · 1 = techo (un solo muro cuadrado).
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
uniform float u_speed;       // 2 velocidad  · 0–3    barrido de luz / onda
uniform float u_ripple;      // 3 distorsión · 0–1    amplitud de la onda que inclina las placas
uniform float u_accent;      // 4 color      · 0–1    fracción de placas amarillas (0.2 = paleta)
uniform float u_shine;       // 5 firma      · 2–40   dureza del destello (alto = pocas placas a la vez)

// extras
uniform float u_plates;      // 3–16   placas por alto
uniform float u_across;      // 1–6    placas a lo ancho de cada tira
uniform float u_white;       // 0–0.5  fracción de placas blancas (0.1 = paleta)
uniform float u_panels;      // 1–16   tiras en el canvas (8 = booth)

out vec4 fragColor;

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), f.x),
               mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), f.x), f.y);
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

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float lo = clamp(u_low, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    float t = u_time * u_speed;

    // retícula de placas: columnas = Across por tira · techo = cuadrada con Plates por lado
    float rows = max(floor(u_plates + 0.5), 1.0);
    float cols = u_surface > 0.5 ? rows
               : max(floor(u_panels + 0.5), 1.0) * max(floor(u_across + 0.5), 1.0);
    vec2 g = vec2(uv.x * cols, uv.y * rows);
    vec2 id = floor(g);
    vec2 f = fract(g);
    vec2 cellPx = u_res / vec2(cols, rows);
    float aspect = u_res.x / u_res.y;
    vec2 P = (id + 0.5) / vec2(cols, rows) * vec2(aspect, 1.0);   // centro en espacio de aspecto

    // inclinación: onda que barre el muro + ruido lento + un poco propio de cada placa
    float amp = u_ripple * (0.7 + 0.6 * lo);
    float tilt = sin(P.x * 2.2 - P.y * 1.3 - t * 1.2) * amp
               + (vnoise(P * 1.8 + t * 0.2) - 0.5) * amp
               + (hash21(id) - 0.5) * 0.5;
    tilt += kick * 0.6 * sin(length(P - vec2(aspect * 0.5, 0.5)) * 6.0 - u_time * 8.0);   // onda del kick
    float light = sin(t * 0.31) * 0.9;
    float facing = max(0.0, cos((tilt - light) * 1.4));
    float spec = pow(facing, u_shine);

    // forma de la placa: margen negro en px (siempre legible), franja de brillo que se desliza, filo arriba
    vec2 px = f * cellPx;
    float m = min(cellPx.x, cellPx.y) * 0.09 + 2.0;
    float body = step(m, px.x) * step(px.x, cellPx.x - m) * step(m, px.y) * step(px.y, cellPx.y - m);
    vec2 q = (px - m) / max(cellPx - 2.0 * m, vec2(1.0));          // 0..1 dentro de la placa
    float bandY = 0.5 + 0.45 * sin(tilt * 2.2 + 0.6);
    float band = exp(-pow((q.y - bandY) / 0.16, 2.0));
    float rim = 1.0 - smoothstep(0.0, 0.05, 1.0 - q.y);            // filo superior
    float grad = 0.55 + 0.45 * q.y;                                // la placa se aclara hacia arriba

    vec3 c = pick(hash21(id + 5.3));
    vec3 col = c * body * (facing * 0.18 * grad * (0.7 + 0.5 * e)  // cuerpo: reflejo amplio
                           + spec * (0.55 * grad + 1.1 * band));   // destello
    col += mix(c, u_color1, 0.5) * body * rim * (0.15 + 0.9 * spec);   // filo claro

    col *= u_intensity;
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
