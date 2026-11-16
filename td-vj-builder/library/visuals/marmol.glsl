// marmol.glsl: vetas de marmol / humo por domain warping (recetario 12; ref. Inigo Quilez, "warping").
// f = fbm(p + A*r), r = fbm(p + A*q), q = fbm(p): el campo se dobla sobre si mismo. No se pinta el campo (eso es
// el plasma de 2005): solo sus curvas de nivel finas (fwidth = 1 px), y solo donde el warp es fuerte (vetas); el
// resto queda negro con un humo muy tenue. Torsion (slot 5) gira el vector de warp segun el propio campo: de vetas
// largas a remolinos. El bajo empuja la amplitud del warp, los agudos ponen grano en las vetas y cada kick enciende
// UNA veta (la que toca por Step) con un destello corto.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_mid;
uniform float u_high;
uniform float u_kick;
uniform float u_step;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: profundidad del warp
uniform float u_tono;
uniform float u_firma;       // 5 firma: torsion (radianes que gira el warp segun el campo)
out vec4 fragColor;
#define PI 3.14159265
#define NVETAS 9.0

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    float a = hash21(i), b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0)), d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}
// 4 octavas para las capas de warp, 5 para el campo final (recetario: no subir a 8)
float fbm4(vec2 p) {
    float v = 0.0, a = 0.5;
    mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
    for (int i = 0; i < 4; i++) { v += a * vnoise(p); p = m * p; a *= 0.5; }
    return v;
}
float fbm5(vec2 p) {
    float v = 0.0, a = 0.5;
    mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
    for (int i = 0; i < 5; i++) { v += a * vnoise(p); p = m * p; a *= 0.5; }
    return v;
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5) * 2.4;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float golpe = smoothstep(0.6, 1.0, k);                      // corto: solo la cresta del kick
    float t = u_time * u_speed * 0.06;
    float tor = clamp(u_firma, 0.0, 3.0);
    vec3 tinta = mix(u_color1, u_color2, u_tono);

    // ---- domain warping (IQ): q -> r -> f, con torsion
    float amp = 1.0 + 2.2 * clamp(u_warp, 0.0, 1.0) + 1.1 * lo;  // el bajo empuja el warp
    vec2 q = vec2(fbm4(p + vec2(0.0, t)), fbm4(p + vec2(5.2, 1.3) - vec2(t * 0.7, 0.0))) - 0.5;
    q = rot(tor * q.x * 3.0) * q;
    vec2 r = vec2(fbm4(p + amp * q + vec2(1.7, 9.2) + t * 0.6),
                  fbm4(p + amp * q + vec2(8.3, 2.8) - t * 0.4)) - 0.5;
    r = rot(tor * r.y * 3.0) * r;
    float f = fbm5(p + amp * r + vec2(0.0, t * 0.3));

    // ---- vetas: curvas de nivel finas del campo (1 px con fwidth)
    float x = f * NVETAS * 2.2 + 0.04 * hi * (vnoise(p * 24.0 + u_time * 6.0) - 0.5);   // agudos = grano
    float fw = max(fwidth(x), 1e-4);
    float idx = floor(x + 0.5);
    float dl = abs(fract(x + 0.5) - 0.5);
    float sel = 6.0 + mod(floor(u_step + 0.5) * 5.0, NVETAS);   // la veta que enciende este kick (las del medio del campo)
    bool esSel = abs(idx - sel) < 0.5;
    float ancho = 0.9 + (esSel ? 1.4 * golpe : 0.0);
    float linea = 1.0 - smoothstep(0.0, fw * ancho, dl);
    // subvetas (mitad de paso) con los medios: el medio hace el marmol mas fino
    float dl2 = abs(fract(x * 2.0) - 0.5);
    float sub = (1.0 - smoothstep(0.0, max(fwidth(x * 2.0), 1e-4) * 0.8, dl2)) * (0.15 + 0.25 * mi);

    // solo donde el warp es fuerte hay vetas: lo demas es negro
    float turb = length(r);
    float mascara = smoothstep(0.12, 0.38, turb);
    float peso = 0.35 + 0.5 * hash11(idx * 7.13 + 3.0);
    float luz = linea * peso * mascara + sub * mascara * 0.6;
    float destello = esSel ? golpe * linea * (0.4 + 0.6 * mascara) : 0.0;

    // humo: el campo apenas visible donde se dobla mas
    float humo = smoothstep(0.55, 0.85, f) * smoothstep(0.2, 0.45, turb) * 0.07;

    vec3 col = tinta * (luz * 0.55 + humo) + mix(tinta, vec3(1.0), 0.6) * destello * 0.75;
    vec2 v = uv - 0.5;
    col *= 1.0 - 0.6 * dot(v, v) * 2.0;
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
