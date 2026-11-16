// ron_liquido.glsl (v2, con Cristal): luz atravesando un vaso de ron con hielo.
// Cuerpo liquido oscuro + red de causticas (dos capas de voronoi deformadas) + destellos en los nudos.
// v1 queda en ron_liquido_v1.glsl.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (pagina Audio)
uniform float u_low;
uniform float u_high;
uniform float u_kick;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;      // fondo negro
uniform float u_intensity;   // 1 intensidad
uniform float u_speed;       // 2 velocidad
uniform float u_warp;        // 3 distorsion: cuanto ondula el liquido
uniform float u_tono;        // 4 color: 0 A, 1 B
uniform float u_escala;      // 5 firma: tamano de las causticas (hielo grande / fino)
out vec4 fragColor;

float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
vec2 hash22(vec2 p) { vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973)); q += dot(q, q.yzx + 33.33); return fract((q.xx + q.yz) * q.zy); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}
float fbm(vec2 p) { float v = 0.0, a = 0.5; for (int i = 0; i < 4; i++) { v += a * noise(p); p = p * 2.03 + 11.0; a *= 0.5; } return v; }

// distancia al borde de celda (dB - dA): 0 en las lineas de la caustica
float borde(vec2 x, float t) {
    vec2 n = floor(x), f = fract(x);
    float dA = 8.0, dB = 8.0;
    for (int j = -2; j <= 2; j++)
    for (int i = -2; i <= 2; i++) {
        vec2 g = vec2(i, j);
        vec2 o = hash22(n + g);
        o = 0.5 + 0.42 * sin(t + 6.2831 * o);
        vec2 r = g + o - f;
        float d = dot(r, r);
        if (d < dA) { dB = dA; dA = d; } else if (d < dB) { dB = d; }
    }
    return sqrt(dB) - sqrt(dA);
}

void main() {
    vec2 uv = vUV.st;
    vec2 p = (uv - 0.5) * vec2(u_res.x / u_res.y, 1.0) * u_escala;
    float t = u_time * u_speed;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);

    // el liquido: la superficie ondula y deforma lo que se ve a traves
    vec2 w = vec2(fbm(p * 0.7 + t * 0.15), fbm(p * 0.7 + vec2(4.1, 2.3) - t * 0.12)) - 0.5;
    vec2 q = p + w * (0.6 + 1.6 * u_warp + 0.6 * lo);

    // dos capas de causticas a distinta escala; donde se cruzan brillan mas
    float e1 = borde(q * 1.0, t * 0.9);
    float e2 = borde(q * 1.9 + 7.3, -t * 0.7);
    float ancho = 0.06 + 0.04 * lo;
    float c1 = pow(1.0 - smoothstep(0.0, ancho, e1), 2.5);
    float c2 = pow(1.0 - smoothstep(0.0, ancho * 0.8, e2), 2.5);
    float caus = c1 * 0.75 + c2 * 0.45 + c1 * c2 * 1.4;

    // cuerpo del ron: profundidad oscura que respira
    float n = fbm(q * 0.5 - t * 0.05);
    float cuerpo = smoothstep(0.3, 0.9, n);

    // destellos en los nudos con los agudos
    float nudo = c1 * c2;
    float chispa = step(0.985 - 0.04 * hi, hash21(floor(q * 18.0) + floor(t * 6.0))) * nudo;

    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 col = u_color3
             + tono * cuerpo * 0.16
             + tono * caus * (0.55 + 0.6 * lo + 0.5 * k)
             + mix(tono, vec3(1.0), 0.3) * (nudo * 0.5 + chispa * 1.5);
    col *= u_intensity;
    vec2 v = uv - 0.5;
    col *= 1.0 - 0.85 * dot(v, v);
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
