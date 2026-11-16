// seda.glsl: hilos de humo (feedback advectado por un campo de curl noise).
// Unos emisores lentos sueltan tinta; el campo la estira en hilos. Cada kick suelta una linea horizontal
// que el campo desgarra. sTD2DInputs[0] = cuadro anterior.
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
uniform float u_warp;        // 3 distorsion: fuerza del flujo
uniform float u_tono;
uniform float u_firma;       // 5 firma: turbulencia (escala del campo)
uniform float u_estela;      // extra: cuanto dura el humo
out vec4 fragColor;

float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}
float campo(vec2 p, float t) { return noise(p + vec2(0.0, t)) + 0.5 * noise(p * 2.1 - vec2(t * 0.7, 0.0)); }
vec2 curl(vec2 p, float t) {
    float e = 0.01;
    float a = campo(p + vec2(0, e), t), b = campo(p - vec2(0, e), t);
    float c = campo(p + vec2(e, 0), t), d = campo(p - vec2(e, 0), t);
    return vec2(a - b, -(c - d)) / (2.0 * e);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2(uv.x * asp, uv.y);
    float t = u_time * u_speed * 0.15;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);

    vec2 v = curl(p * u_firma, t) + 0.3 * hi * curl(p * u_firma * 4.0, t * 3.0);
    vec2 paso = v * (0.0006 + 0.0025 * u_warp) * (0.6 + 0.8 * lo) * max(u_speed, 0.05);
    paso.x /= asp;
    vec3 prev = texture(sTD2DInputs[0], uv - paso).rgb;

    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    float tinta = 0.0, tinta2 = 0.0;
    for (int i = 0; i < 10; i++) {
        float fi = float(i);
        vec2 e = vec2(asp * (0.5 + 0.38 * sin(u_time * 0.11 * (1.0 + fi * 0.3) + fi * 2.1)),
                      0.5 + 0.36 * sin(u_time * 0.13 * (1.0 + fi * 0.21) + fi * 1.3));
        float d = length(p - e);
        float s = exp(-d * d / 0.000025) * (0.35 + 0.6 * lo);
        if (mod(fi, 5.0) > 3.5) tinta2 += s; else tinta += s;
    }
    // kick: linea horizontal fina que el flujo desgarra
    float ly = 0.5 + 0.3 * sin(floor(u_time * 2.0) * 1.7);
    tinta += k * exp(-pow((uv.y - ly) * u_res.y / 1.5, 2.0)) * 0.6;

    vec3 col = prev * u_estela + (tono * tinta + otro * tinta2 * 0.6) * u_intensity;
    col = min(col, vec3(1.2));
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
