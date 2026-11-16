// cordillera.glsl: lineas apiladas que forman una montana con el track (ridgeline).
// La linea de enfrente es el audio de ahora; cada linea hacia atras es el audio de unos cuadros antes
// (sTD2DInputs[0] = historia de cordillera_hist.glsl). Las de enfrente tapan a las de atras.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: rugosidad de la montana
uniform float u_tono;
uniform float u_firma;       // 5 firma: numero de lineas
out vec4 fragColor;

float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}

vec4 historia(float z) { return texture(sTD2DInputs[0], vec2(0.5, (z * 120.0 + 0.5) / 128.0)); }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    float x = (uv.x - 0.5) * asp;
    float N = floor(clamp(u_firma, 12.0, 90.0));
    float t = u_time * u_speed;
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    vec3 col = vec3(0.0);
    float px = 1.0 / u_res.y;

    for (int i = 0; i < 90; i++) {
        float fi = float(i);
        if (fi >= N) break;
        float z = fi / N;                              // 0 enfrente, 1 al fondo
        float yb = mix(0.10, 0.80, pow(z, 0.8));       // base de la linea en pantalla
        float esc = mix(1.0, 0.45, z);                 // perspectiva
        float xs = x / mix(1.0, 0.6, z);
        vec4 h = historia(z);
        float tr = t * 0.6 - z * 4.0;                  // el relieve viaja con su linea
        float env = exp(-xs * xs * 2.6);               // pico al centro
        float rug = 1.0 + 3.0 * u_warp;
        float perfil = env * (0.10 + 0.08 * noise(vec2(xs * 3.0, tr))
                       + h.x * 0.55 * noise(vec2(xs * 2.0 * rug, tr + 3.1))
                       + h.y * 0.35 * noise(vec2(xs * 6.0 * rug, tr + 7.7))
                       + h.z * 0.18 * noise(vec2(xs * 22.0 * rug, tr * 3.0)));
        float lado = 1.0 - smoothstep(0.55, 1.05, abs(xs));     // la linea se apaga hacia los lados
        float y = yb + perfil * 0.55 * esc;
        float grosor = px * mix(1.6, 0.9, z);
        float d = uv.y - y;
        if (d < -grosor) {                             // debajo de esta linea: la tapa
            col += tono * 0.03 * (1.0 - z);
            break;
        }
        float linea = 1.0 - smoothstep(0.0, grosor, abs(d));
        if (linea > 0.0) {
            float brillo = lado * mix(1.0, 0.25, z) * (0.7 + 0.6 * h.x + 1.2 * h.w);
            col += mix(tono, otro, clamp(h.z * 0.6, 0.0, 0.5)) * linea * brillo;
            if (d < grosor) break;
        }
    }
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
