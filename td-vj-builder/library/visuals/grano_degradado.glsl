// base1 · grano_degradado — fondo continuo
// Degradado de tres colores con grano analógico y drift lentísimo.
// El fondo que puede estar puesto toda la noche sin cansar.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_grain;      // intensidad (slot 1)
uniform float u_drift;      // velocidad (slot 2)
uniform float u_warp;       // distorsión (slot 3)
uniform float u_blend;      // color (slot 4)      — desplaza el midpoint del blend
uniform float u_angle;      // firma (slot 5)      — ángulo del degradado
uniform float u_vignette;   // extra
uniform vec3  u_color1;     // crema
uniform vec3  u_color2;     // rosa
uniform vec3  u_color3;     // violeta

out vec4 fragColor;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void main() {
    vec2 uv = vUV.st;
    vec2 p = uv - 0.5;
    p.x *= u_res.x / max(u_res.y, 1.0);

    // drift lentísimo
    float t = u_time * (0.05 + u_drift * 0.35);
    vec2 warp = vec2(
        noise(p * 1.7 + vec2(t, 0.0)),
        noise(p * 1.7 + vec2(0.0, t) + 17.3)
    ) - 0.5;
    p += warp * u_warp * 0.6;

    // rotar
    float ca = cos(u_angle), sa = sin(u_angle);
    vec2 pr = mat2(ca, -sa, sa, ca) * p;

    // parámetro del degradado
    float g = clamp(pr.y * 0.7 + 0.5, 0.0, 1.0);

    // midpoint del blend según u_blend
    float mid = mix(0.28, 0.72, u_blend);
    float sh1 = smoothstep(0.0, mid, g);
    float sh2 = smoothstep(mid, 1.0, g);
    vec3 col = mix(u_color1, u_color2, sh1);
    col = mix(col, u_color3, sh2);

    // grano analógico
    float gr = hash(uv * u_res + fract(u_time * 60.0)) - 0.5;
    col += gr * u_grain * 0.55;

    // vignette
    float d = length(uv - 0.5);
    col *= 1.0 - u_vignette * smoothstep(0.32, 0.86, d);

    // audio como respiración suave
    col *= 1.0 + u_bass * 0.12;

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
