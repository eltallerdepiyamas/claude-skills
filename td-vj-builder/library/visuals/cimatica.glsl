// cimatica.glsl: placa de Chladni circular. La arena se junta donde la placa no vibra (nodos) y dibuja
// anillos y radios. Cada kick cambia el modo de vibracion (otra figura) y la arena migra a la nueva
// (feedback). Los graves sacuden la arena. sTD2DInputs[0] = cuadro anterior.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_high;
uniform float u_kick;
uniform float u_step;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: cuanto se sacude la arena
uniform float u_tono;
uniform float u_firma;       // 5 firma: complejidad maxima de los modos
uniform float u_estela;      // extra: que tan lento migra la arena a la figura nueva
out vec4 fragColor;
#define PI 3.14159265
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}

// modo (n radios, m anillos) de una placa circular: cos(n*theta) * sin(m*pi*r/R) (aproximacion de Bessel)
float modo(float r, float a, float n, float m, float giro) {
    return cos(n * (a + giro)) * sin(m * PI * r / 0.46);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float r = length(p), a = atan(p.y, p.x);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float s = floor(u_step);
    float maxc = clamp(u_firma, 2.0, 14.0);
    // siempre figuras con radios y anillos (nunca el modo mas simple de una sola linea)
    float n1 = floor(2.0 + hash11(s * 3.1 + 0.37) * (maxc - 1.0)), m1 = floor(2.0 + hash11(s * 7.7 + 0.11) * (maxc * 0.8 - 1.0));
    float n2 = floor(3.0 + hash11(s * 5.3 + 0.73) * (maxc * 0.6)), m2 = floor(2.0 + hash11(s * 2.9 + 0.59) * (maxc - 1.0));
    float giro = u_time * u_speed * 0.05;
    float f = modo(r, a, n1, m1, giro) + 0.7 * modo(r, a, n2, m2, -giro * 1.3);
    // sacudida: los graves mueven la arena fuera del nodo
    f += (noise(p * 40.0 + u_time * 8.0) - 0.5) * (0.05 + 0.25 * u_warp) * lo;
    float arena = exp(-f * f / (0.0012 + 0.0015 * lo));      // linea fina de arena en los nodos
    float grano = 0.35 + 0.65 * step(0.55 - 0.15 * lo, hash21(floor(uv * u_res)));
    float placa = 1.0 - smoothstep(0.455, 0.462, r);
    float borde = exp(-pow((r - 0.462) * u_res.y / 1.2, 2.0));
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    vec3 nuevo = tono * arena * grano * placa * (0.9 + 0.5 * lo)
               + mix(tono, vec3(1.0), 0.3) * arena * placa * k * 0.4
               + otro * borde * (0.35 + 0.4 * hi);
    vec3 prev = texture(sTD2DInputs[0], uv).rgb;
    vec3 col = mix(nuevo, prev, u_estela);                   // la arena migra, no salta
    fragColor = TDOutputSwizzle(vec4(u_color3 + col * u_intensity, 1.0));
}
