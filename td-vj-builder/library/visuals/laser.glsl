// laser.glsl: haces de laser en humo, con estela de fosforo (feedback). Cada kick cambia la figura.
// Figuras (u_step): 0 abanico desde abajo · 1 abanico desde arriba · 2 laminas horizontales · 3 cruce desde los lados.
// sTD2DInputs[0] = cuadro anterior.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_high;
uniform float u_step;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: cuanto se mecen los haces
uniform float u_tono;
uniform float u_firma;       // 5 firma: numero de haces
uniform float u_estela;      // extra: persistencia
out vec4 fragColor;

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}

// un haz desde o con direccion d: nucleo fino + halo
float haz(vec2 p, vec2 o, vec2 d, float w) {
    vec2 v = p - o;
    float a = dot(v, d);
    if (a < 0.0) return 0.0;
    float perp = abs(v.x * d.y - v.y * d.x);
    return exp(-perp * perp / (w * w)) + 0.12 * exp(-perp * 40.0);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float t = u_time * u_speed;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float modo = mod(u_step, 4.0);
    float sem = floor(u_step);
    float N = floor(clamp(u_firma, 1.0, 24.0));
    float w = 0.0016 * (1.0 + 0.6 * hi);
    float abre = 0.5 + 0.7 * hash11(sem * 1.7) + 0.4 * lo;

    float L = 0.0;
    for (int i = 0; i < 24; i++) {
        float fi = float(i);
        if (fi >= N) break;
        float k = N > 1.0 ? fi / (N - 1.0) - 0.5 : 0.0;
        float mece = sin(t * 0.8 + fi * 0.55 + sem) * u_warp * 0.35;
        if (modo < 1.0) {
            float a = 1.5708 + k * abre * 2.0 + mece;
            L += haz(p, vec2(0.0, -0.55), vec2(cos(a), sin(a)), w);
        } else if (modo < 2.0) {
            float a = -1.5708 + k * abre * 2.0 + mece;
            L += haz(p, vec2(0.0, 0.55), vec2(cos(a), sin(a)), w);
        } else if (modo < 3.0) {
            float y = k * 0.8 + mece * 0.3;
            float perp = abs(p.y - y);
            L += exp(-perp * perp / (w * w)) + 0.12 * exp(-perp * 40.0);
        } else {
            float lado = mod(fi, 2.0) < 1.0 ? -1.0 : 1.0;
            float a = (lado < 0.0 ? 0.0 : 3.1416) + lado * (k * abre + mece);
            L += haz(p, vec2(lado * asp * 0.5, -0.1), vec2(cos(a), sin(a)), w);
        }
    }
    // humo: el haz solo se ve donde hay particulas
    float humo = 0.45 + 0.55 * noise(p * 3.0 + vec2(t * 0.2, -t * 0.1)) * noise(p * 7.0 - t * 0.15);
    L *= humo * (0.6 + 0.5 * lo);

    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 nuevo = (tono * L + mix(tono, vec3(1.0), 0.35) * L * L * 0.15) * u_intensity;
    vec3 prev = texture(sTD2DInputs[0], uv).rgb;
    vec3 col = max(prev * u_estela, nuevo);
    col = min(col + u_color3, vec3(1.5));
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
