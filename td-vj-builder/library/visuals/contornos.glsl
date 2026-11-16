// contornos.glsl: curvas de nivel (mapa topografico) de un terreno que respira.
// Lineas finas, cada 5a mas brillante (curva maestra). El kick levanta un pico que se propaga en ondas.
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
uniform float u_warp;        // 3 distorsion: que tan retorcido es el terreno
uniform float u_tono;
uniform float u_firma;       // 5 firma: numero de curvas
out vec4 fragColor;

float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}
float fbm(vec2 p) { float v = 0.0, a = 0.5; for (int i = 0; i < 5; i++) { v += a * noise(p); p = p * 2.02 + 7.0; a *= 0.5; } return v; }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5) * 2.2;
    float t = u_time * u_speed * 0.12;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    vec2 w = vec2(fbm(p * 0.7 + t), fbm(p * 0.7 - t + 3.7)) - 0.5;
    float h = fbm(p + w * (0.8 + 2.2 * u_warp) + vec2(0.0, t * 0.5));
    // pico que el kick levanta en un punto que viaja; sus ondas bajan por las curvas
    vec2 pk = vec2(sin(u_time * 0.21) * 0.9 * asp, cos(u_time * 0.17) * 0.6);
    float r = length(p - pk);
    h += (0.25 * lo + 0.35 * k) * exp(-r * r * 2.5) + 0.04 * lo * sin(r * 14.0 - u_time * 6.0) * exp(-r * 1.2);
    h += 0.015 * hi * (noise(p * 30.0 + u_time * 3.0) - 0.5);
    float N = floor(clamp(u_firma, 4.0, 60.0));
    float v = h * N;
    float f = fract(v);
    float dv = fwidth(v);
    float linea = 1.0 - smoothstep(0.0, dv * 1.3, min(f, 1.0 - f));
    float maestra = step(mod(floor(v + 0.5), 5.0), 0.5);
    float alto = smoothstep(0.35, 0.85, h);                 // las cimas brillan mas
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    vec3 col = tono * linea * mix(0.35, 1.0, maestra) * (0.45 + 0.8 * alto)
             + mix(tono, vec3(1.0), 0.3) * linea * maestra * k * 0.6
             + otro * linea * smoothstep(0.75, 0.95, h) * 0.5
             + tono * 0.05 * alto;                          // relleno muy tenue en las cimas
    vec2 q = uv - 0.5;
    col *= 1.0 - 0.7 * dot(q, q);
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
