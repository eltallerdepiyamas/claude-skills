// red_nodos.glsl: plexus. Nodos que derivan en una rejilla suelta y se conectan con lineas finas
// cuando estan cerca; el kick abre el radio de conexion y enciende los nodos. Negro dominante.
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
uniform float u_warp;        // 3 distorsion: cuanto se alejan los nodos de su celda
uniform float u_tono;
uniform float u_firma;       // 5 firma: densidad (celdas por alto de pantalla)
out vec4 fragColor;

vec2 hash22(vec2 p) { vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973)); q += dot(q, q.yzx + 33.33); return fract((q.xx + q.yz) * q.zy); }
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }

vec2 nodo(vec2 c, float t) {
    vec2 h = hash22(c);
    float a = 0.35 + 0.6 * u_warp;
    return c + 0.5 + a * 0.5 * vec2(sin(t * (0.6 + h.x) + h.y * 6.28), cos(t * (0.5 + h.y) + h.x * 6.28));
}

float segmento(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2(uv.x * asp, uv.y) * u_firma;
    float t = u_time * u_speed * 0.5;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    vec2 c0 = floor(p);
    vec2 pts[9];
    int n = 0;
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        pts[n] = nodo(c0 + vec2(i, j), t);
        n++;
    }
    float radio = 1.25 + 0.35 * lo + 0.4 * k;          // en celdas
    float px = u_firma / u_res.y;                        // un pixel en unidades de celda
    float lineas = 0.0, nodos = 0.0, chispa = 0.0;
    for (int a = 0; a < 9; a++) {
        float d = length(p - pts[a]);
        nodos += exp(-d * d / (px * px * (14.0 + 20.0 * k)));
        vec2 ca = floor(pts[a]);
        chispa += step(0.97 - 0.05 * hi, hash21(ca + floor(t * 4.0))) * exp(-d * d / (px * px * 40.0));
        for (int b = a + 1; b < 9; b++) {
            float L = length(pts[a] - pts[b]);
            if (L > radio) continue;
            float s = segmento(p, pts[a], pts[b]);
            float w = 1.0 - smoothstep(px * 0.4, px * 1.8, s);
            lineas += w * pow(1.0 - L / radio, 1.2);
        }
    }
    // mascara lenta: la red se ve por zonas, no pareja en toda la pantalla
    float zona = smoothstep(0.15, 0.85, 0.5 + 0.5 * sin(p.x * 0.23 + t * 0.4) * cos(p.y * 0.31 - t * 0.3));
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    vec3 col = tono * min(lineas, 1.5) * 1.6 * (0.5 + 0.5 * zona) * (0.8 + 0.6 * lo)
             + mix(tono, vec3(1.0), 0.3) * nodos * (0.5 + 0.8 * k)
             + otro * chispa * 0.8;
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
