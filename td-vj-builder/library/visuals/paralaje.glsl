// paralaje.glsl: capas de lineas horizontales finas a distinta profundidad (recetario 26; ref. NONOTAK "Daydream").
// Seis paneles de lineas, cada uno en su profundidad (escala fija, sin zoom: nada de tunel). La camara se mece despacio
// y las capas de adelante se mueven mas que las de atras (paralaje); donde dos paneles se cruzan sale moire.
// Cada kick mueve UNA capa (la que toca segun Step): salta de lugar y brilla un instante. El bajo abre los paneles.
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
uniform float u_warp;        // 3 distorsion: separacion entre capas (cuanta profundidad / paralaje)
uniform float u_tono;
uniform float u_firma;       // 5 firma: lineas por capa
out vec4 fragColor;
#define CAPAS 6
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    float px = 1.0 / u_res.y;
    float paso = floor(max(u_step, 0.0) + 0.5);
    float sepa = mix(0.4, 2.0, clamp(u_warp, 0.0, 1.0));
    vec2 cam = vec2(sin(t * 0.1), 0.5 * sin(t * 0.07 + 1.3)) * 0.06 * (0.6 + 0.6 * clamp(u_warp, 0.0, 1.0));
    float lineas = clamp(u_firma, 10.0, 200.0);
    vec3 tinta = mix(u_color1, u_color2, u_tono);
    int toca = int(mod(paso, float(CAPAS)));

    vec3 col = vec3(0.0);
    for (int i = 0; i < CAPAS; i++) {
        float fi = float(i);
        float z = fi / float(CAPAS - 1);                         // 0 adelante / 1 atras
        float s = 1.0 / (1.0 + z * sepa);                        // escala fija por profundidad
        // epoca de esta capa: cambia solo cuando el kick le toca a ella
        float epoca = floor((paso + float(CAPAS) * 64.0 - fi) / float(CAPAS));
        vec2 h = vec2(hash21(vec2(fi, epoca)), hash21(vec2(epoca * 1.7, fi + 5.0)));
        vec2 ql = (p + cam * s) / s;                             // adelante se mueve mas con la camara
        // panel: centro y tamano al azar por epoca; el bajo lo abre
        vec2 centro = (h - 0.5) * vec2(0.9 * asp, 0.5);
        vec2 medio = vec2(0.18 + 0.3 * hash21(vec2(fi + 11.0, epoca)), 0.12 + 0.18 * hash21(vec2(epoca, fi + 23.0)));
        medio *= 1.0 + 0.35 * lo;
        vec2 dq = abs(ql - centro) - medio;
        float pxl = px / s;
        float panel = smoothstep(pxl, -pxl, dq.x) * smoothstep(pxl, -pxl, dq.y);
        // lineas horizontales finas; la fase tambien salta con la epoca
        float x = ql.y * lineas + h.x * 7.0;
        float d = abs(fract(x + 0.5) - 0.5);
        float pc = pxl * lineas;                                 // pixel en ciclos
        float lin = smoothstep(0.1 + pc, 0.1 - pc, d) * smoothstep(0.45, 0.2, pc);
        // brillo por profundidad + golpe en la capa que se movio
        float golpe = (i == toca) ? k : 0.0;
        float barrido = 0.3 * hi * smoothstep(0.08, 0.0, abs(fract(ql.x * 0.4 - t * 0.2 + fi * 0.37) - 0.5));
        float luz = mix(0.55, 0.14, z) * (1.0 + 1.2 * golpe) + barrido * (1.0 - z);
        col += mix(tinta, vec3(1.0), 0.12 * (1.0 - z) + 0.3 * golpe) * lin * panel * luz;
    }
    col = min(col, vec3(0.95));
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
