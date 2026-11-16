// campo.glsl: limaduras de hierro. Miles de trazos cortos alineados a un campo de fuerza (curl noise)
// que gira lento. El bajo alarga los trazos; el kick manda una onda que los enciende al pasar.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_high;
uniform float u_kick;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: que tan turbulento es el campo
uniform float u_tono;
uniform float u_firma;       // 5 firma: densidad (trazos por alto de pantalla)
out vec4 fragColor;

float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}
float pot(vec2 p, float t) { return noise(p + vec2(t, 0.0)) + 0.25 * noise(p * 2.0 - vec2(0.0, t)); }
vec2 campo(vec2 p, float t) {
    float e = 0.02;
    float dx = pot(p + vec2(e, 0), t) - pot(p - vec2(e, 0), t);
    float dy = pot(p + vec2(0, e), t) - pot(p - vec2(0, e), t);
    return vec2(dy, -dx) / (2.0 * e);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2(uv.x * asp, uv.y) * u_firma;
    float t = u_time * u_speed * 0.08;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float esc = (0.6 + 1.6 * u_warp) / u_firma;               // escala del campo en celdas
    float px = u_firma / u_res.y;
    float acum = 0.0;
    vec2 c0 = floor(p);
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 c = c0 + vec2(i, j);
        vec2 centro = c + 0.5 + (vec2(hash21(c), hash21(c + 17.0)) - 0.5) * 0.6;
        vec2 f = campo(centro * esc * u_firma / 22.0, t);   // campo amplio: corrientes, no ruido
        float m = length(f);
        vec2 d = f / max(m, 1e-4);
        float largo = (0.45 + 0.75 * clamp(m * 0.6, 0.0, 1.0)) * (0.8 + 0.6 * lo);
        vec2 q = p - centro;
        float a = clamp(dot(q, d), -largo, largo);
        float dist = length(q - d * a);
        float tr = 1.0 - smoothstep(px * 0.3, px * 1.2, dist);
        tr *= 1.0 - smoothstep(largo * 0.6, largo, abs(a));   // puntas finas
        acum += tr * (0.4 + 0.6 * hash21(c + 3.0));
    }
    // onda del kick que cruza la pantalla y una mascara lenta (el negro manda)
    float onda = exp(-pow((uv.x - fract(u_time * 0.25)) * 8.0, 2.0)) * k;
    float zona = smoothstep(0.45, 0.85, noise(vec2(uv.x * asp, uv.y) * 1.3 + t * 2.0));
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    vec3 col = tono * acum * (0.06 + 1.3 * zona) * (0.8 + 0.4 * lo)
             + mix(tono, vec3(1.0), 0.35) * acum * onda * 1.2
             + otro * acum * step(0.985 - 0.03 * hi, hash21(floor(p) + floor(u_time * 8.0))) * 0.8;
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
