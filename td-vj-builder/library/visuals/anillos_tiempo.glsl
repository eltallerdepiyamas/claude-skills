// anillos_tiempo.glsl: la Cordillera en polar. Cada anillo es el audio de un momento: el centro es AHORA
// y hacia afuera es el pasado, como los anillos de un arbol. Son las bandas concentricas del sello hechas
// con el track. sTD2DInputs[0] = historia de audio 1 x 128 (cordillera_hist.glsl).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: rugosidad de los anillos
uniform float u_tono;
uniform float u_firma;       // 5 firma: numero de anillos
out vec4 fragColor;
#define PI 3.14159265
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}
vec4 historia(float z) { return texture(sTD2DInputs[0], vec2(0.5, (z * 120.0 + 0.5) / 128.0)); }
// ruido periodico en el angulo (sin costura en -pi / pi)
float nang(float a, float f, float z) { vec2 c = vec2(cos(a), sin(a)) * f; return noise(c + vec2(z * 3.1, z * 1.7)); }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float r = length(p), a = atan(p.y, p.x);
    float N = floor(clamp(u_firma, 8.0, 60.0));
    float t = u_time * u_speed;
    float px = 1.0 / u_res.y;
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    float r0 = 0.04, r1 = 0.47;
    // anillo mas cercano a este pixel (y sus vecinos, porque los anillos se deforman)
    float zc = clamp((r - r0) / (r1 - r0), 0.0, 1.0) * (N - 1.0);
    vec3 col = vec3(0.0);
    for (int d = -2; d <= 2; d++) {
        float i = floor(zc) + float(d);
        if (i < 0.0 || i > N - 1.0) continue;
        float z = i / (N - 1.0);                       // 0 ahora (centro) · 1 pasado (afuera)
        vec4 h = historia(z);
        float rug = 1.0 + 3.0 * u_warp;
        float tr = t * 0.3 - z * 5.0;                  // el relieve viaja con su anillo
        float desp = h.x * 0.035 * nang(a + tr * 0.2, 1.5 * rug, z)
                   + h.y * 0.020 * nang(a - tr * 0.3, 4.0 * rug, z + 3.0)
                   + h.z * 0.010 * nang(a, 12.0 * rug, z + 7.0);
        float ri = mix(r0, r1, z) + desp * (1.0 - 0.4 * z);
        float g = px * mix(1.1, 0.8, z);
        float lin = 1.0 - smoothstep(g * 0.4, g * 1.6, abs(r - ri));
        float brillo = mix(1.0, 0.3, z) * (0.6 + 0.7 * h.x + 1.3 * h.w);
        col += mix(tono, otro, clamp(h.z * 0.5, 0.0, 0.45)) * lin * brillo;
    }
    float nucleo = exp(-r * r / 0.0006) * (0.4 + 0.8 * historia(0.0).x);   // el ahora, en el centro
    col += mix(tono, vec3(1.0), 0.3) * nucleo;
    fragColor = TDOutputSwizzle(vec4(u_color3 + col * u_intensity, 1.0));
}
