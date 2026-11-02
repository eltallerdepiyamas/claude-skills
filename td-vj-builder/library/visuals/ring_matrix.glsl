// ring_matrix.glsl — base14 · Matriz de anillos (CORONA x FUTURE x ULTRA)
// Ref. cliente pinterest3: pantalla LED de puntos; las celdas activas se vuelven anillos brillantes
// en racimos que cambian a saltos (como LED), alrededor puntos medios y puntitos apagados.
// Paleta del cliente por racimo: 70% azul · 20% amarillo · 10% blanco (Accent / White la ajustan).
// u_surface: 0 = columnas (puntos alineados a las 8 tiras) · 1 = techo (retícula cuadrada, misma lógica).
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
uniform float u_speed;       // 2 velocidad  · 0–3    saltos del patrón
uniform float u_morph;       // 3 distorsión · 0–1    deformación de los racimos
uniform float u_accent;      // 4 color      · 0–1    fracción de racimos amarillos (0.2 = paleta)
uniform float u_pitch;       // 5 firma      · 6–40   puntos a lo ancho de cada tira

// extras
uniform float u_density;     // 0–1    celdas encendidas
uniform float u_glow;        // 0–1    halo de los anillos
uniform float u_white;       // 0–0.5  fracción de racimos blancos (0.1 = paleta)
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

    float N = u_surface > 0.5 ? 1.0 : max(floor(u_panels + 0.5), 1.0);
    float pitchPx = (u_surface > 0.5 ? u_res.x / 4.0 : u_res.x / N) / max(floor(u_pitch + 0.5), 2.0);
    vec2 frag = uv * u_res;
    vec2 id = floor(frag / pitchPx);
    vec2 fp = (fract(frag / pitchPx) - 0.5) * pitchPx;   // px desde el centro del punto
    float L = length(fp);

    // campo de racimos: cambia a saltos, como un panel LED
    float step_ = floor(u_time * u_speed * 3.0);
    vec2 q = id * 0.16;
    q += u_morph * 2.0 * vec2(vnoise(q * 0.5 + step_ * 0.07), vnoise(q * 0.5 + 9.1 - step_ * 0.05)) ;
    float n = vnoise(q + vec2(step_ * 0.21, step_ * 0.13)) * 0.65 + vnoise(q * 2.3 - step_ * 0.3) * 0.35;
    n += (hash21(id + step_) - 0.5) * 0.12;                                 // grano por celda
    float thr = 0.8 - u_density * 0.3 - lo * 0.08 - kick * 0.1;

    float ring  = step(thr, n);
    float mid   = step(thr - 0.06, n) * (1.0 - ring);
    float spark = step(0.995 - u_density * 0.01, hash21(id * 1.7 + floor(u_time * u_speed * 8.0)));
    ring = max(ring, spark);

    float r = pitchPx * 0.33, th = max(pitchPx * 0.09, 1.0);
    float ringV = 1.0 - smoothstep(th * 0.5 - 0.7, th * 0.5 + 0.7, abs(L - r));
    float inner = (1.0 - smoothstep(r * 0.55, r * 0.55 + 1.0, L)) * 0.25;
    float midV  = 1.0 - smoothstep(pitchPx * 0.14, pitchPx * 0.14 + 1.0, L);
    float tiny  = 1.0 - smoothstep(pitchPx * 0.07, pitchPx * 0.07 + 1.0, L);
    float halo  = exp(-L / (pitchPx * 0.35)) * u_glow * 0.5;

    vec3 c = pick(hash21(id + 21.0));                       // color por punto, como LED
    vec3 col = c * ring * (ringV * (1.1 + kick * 0.6) + inner + halo);
    col += u_color4 * mid * midV * 0.35;
    col += u_color4 * (1.0 - ring) * (1.0 - mid) * tiny * 0.14;

    col *= u_intensity * (0.8 + 0.3 * e);
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
