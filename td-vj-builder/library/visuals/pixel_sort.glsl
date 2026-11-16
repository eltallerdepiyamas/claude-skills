// pixel_sort.glsl: formas de luz que se derriten en chorros de pixeles (pixel sort falso con feedback).
// Lo que pasa el umbral gotea hacia abajo; cada columna de 6 px cae a su velocidad (look ordenado/digital).
// El kick suelta los chorros mas largos. sTD2DInputs[0] = cuadro anterior.
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
uniform float u_warp;        // 3 distorsion: 0 cae vertical, 1 se va de lado
uniform float u_tono;
uniform float u_firma;       // 5 firma: umbral (que tanto se derrite)
out vec4 fragColor;

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1, 0)), u.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), u.x), u.y);
}
float fbm(vec2 p) { float v = 0.0, a = 0.5; for (int i = 0; i < 4; i++) { v += a * noise(p); p = p * 2.03 + 11.0; a *= 0.5; } return v; }
float lum(vec3 c) { return dot(c, vec3(0.3, 0.59, 0.11)); }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    float t = u_time * u_speed;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);

    // fuente: crestas de luz lentas + barras que aparecen con los agudos
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y) * 2.2;
    float n = fbm(p + vec2(t * 0.12, t * 0.05));
    float cresta = pow(1.0 - abs(2.0 * fbm(p * 0.8 - t * 0.07 + n) - 1.0), 14.0);
    float barra = step(0.975 - 0.05 * hi, hash21(vec2(floor(uv.y * 40.0), floor(t * 2.0)))) *
                  step(0.5, hash11(floor(uv.x * 12.0) + floor(t * 2.0)));
    vec3 src = tono * cresta * (0.6 + 0.6 * lo) + otro * barra * 0.35;

    // chorros: cada columna cae a su velocidad
    vec2 px = 1.0 / u_res;
    float col6 = floor(uv.x * u_res.x / 6.0);
    float vel = (2.0 + 10.0 * hash11(col6 + floor(t * 0.5) * 3.1)) * (0.5 + u_speed);
    vec2 dir = normalize(vec2(u_warp, 1.0 - u_warp * 0.7));
    vec3 arriba = texture(sTD2DInputs[0], uv + dir * px * vel).rgb;
    float largo = 0.90 + 0.08 * k;
    vec3 chorro = lum(arriba) > u_firma ? arriba * largo : arriba * 0.5;
    vec3 c = max(src * u_intensity, chorro);
    c = min(c, vec3(1.3));
    fragColor = TDOutputSwizzle(vec4(c + u_color3, 1.0));
}
