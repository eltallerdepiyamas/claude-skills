// pulso_neon.glsl (v2): liston de lineas de luz que sube, baja y se abre con el audio (la v1 en pulso_neon_v1.glsl).
// Nuevo: halo neon suave · pulsos de luz que corren por las lineas (cada kick suelta uno) · cada linea escucha
// su banda (abajo low, centro mid, arriba high) · dos ecos tenues detras para dar profundidad.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (pagina Audio)
uniform float u_low;
uniform float u_mid;
uniform float u_high;
uniform float u_kick;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;      // fondo negro
uniform float u_intensity;   // 1 intensidad
uniform float u_speed;       // 2 velocidad
uniform float u_warp;        // 3 distorsion
uniform float u_tono;        // 4 color: 0 A, 1 B
uniform float u_lineas;      // 5 firma: cuantas lineas
uniform float u_grosor;      // extra: grosor
out vec4 fragColor;
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}

// el liston completo a un tiempo dado: devuelve (lineas, halo, pulsos)
vec3 liston(vec2 p, float t, float aspect, float e, float lo, float mi, float hi, float k, float n) {
    float centro = 1.0 - smoothstep(0.0, 0.9, abs(p.x) / (0.5 * aspect));
    float ancho = 0.10 + 0.20 * e + 0.06 * k;
    float eje = (noise(vec2(p.x * 1.1, t * 0.35)) - 0.5) * (0.25 + 0.55 * u_warp)
              + sin(p.x * 11.0 - t * 4.0) * centro * e * 0.07;
    float abajo = eje - ancho, arriba = eje + ancho;
    float lineas = 0.0, halo = 0.0, pulsos = 0.0;
    for (float i = 0.0; i < 24.0; i += 1.0) {
        if (i >= n) break;
        float f = n > 1.0 ? i / (n - 1.0) : 0.5;
        // banda de esta linea: abajo low, centro mid, arriba high
        float banda = f < 0.5 ? mix(lo, mi, f * 2.0) : mix(mi, hi, f * 2.0 - 1.0);
        float onda = sin(p.x * (6.0 + 10.0 * f) - t * (2.0 + 3.0 * f) + i) * 0.02 * banda * centro;
        float y = mix(abajo, arriba, f) + (noise(vec2(p.x * 2.6 + i * 3.1, t * 0.5)) - 0.5) * 0.05 + onda;
        float d = abs(p.y - y);
        float g = u_grosor * 6.0 * (1.0 + 0.8 * e);
        lineas = max(lineas, 1.0 - smoothstep(g, g * 2.2, d));
        halo += exp(-d * d / (g * g * 40.0)) * 0.12;
        // pulso: un paquete de luz que corre por la linea; su salida la marca el ultimo kick
        float vel = 0.6 + 0.8 * hash11(i * 7.3);
        float pos = fract(t * vel * 0.25 + hash11(i)) * (aspect + 0.6) - (aspect * 0.5 + 0.3);
        float dx = p.x - pos;
        pulsos += exp(-dx * dx * 60.0) * exp(-d * d / (g * g * 6.0)) * (0.3 + 1.2 * k);
    }
    return vec3(lineas, halo, pulsos);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * aspect, uv.y - 0.5);
    float t = u_time * u_speed;
    float e = clamp(u_bass, 0.0, 2.0);
    float lo = clamp(max(u_low, u_bass), 0.0, 2.0), mi = clamp(u_mid, 0.0, 2.0), hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float n = clamp(floor(u_lineas), 1.0, 24.0);
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);

    vec3 a = liston(p, t, aspect, e, lo, mi, hi, k, n);
    // ecos: el mismo liston un instante antes, mas tenue y un poco abajo (profundidad)
    vec3 e1 = liston(p + vec2(0.0, 0.035), t - 0.35, aspect, e, lo, mi, hi, 0.0, n);
    vec3 e2 = liston(p + vec2(0.0, 0.07), t - 0.7, aspect, e, lo, mi, hi, 0.0, n);

    vec3 col = u_color3;
    col += tono * (e1.x * 0.16 + e2.x * 0.07);
    col += tono * a.y * (0.6 + 0.6 * e);                                    // halo neon
    col += mix(tono, vec3(1.0), 0.12 + 0.2 * e) * a.x * (0.85 + 0.5 * e);   // lineas
    col += mix(otro, vec3(1.0), 0.35) * a.z;                                // pulsos que corren
    vec2 q = uv - 0.5;
    col *= 1.0 - 0.5 * dot(q, q);
    fragColor = TDOutputSwizzle(vec4(max(col * u_intensity, 0.0), 1.0));
}
