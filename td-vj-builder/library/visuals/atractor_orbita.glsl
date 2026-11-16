// atractor_orbita.glsl: puntos del atractor de Clifford para este cuadro (recetario 14; ref. Max Cooper / Anadol, nubes de puntos).
// Cada texel (N x 1) es un punto: semilla al azar distinta cada cuadro + 40 iteraciones del mapa -> cae sobre el atractor.
// Salida rgba32float: rg = punto normalizado a [-1, 1], b = velocidad (largo del ultimo salto), a = 1.
// Los parametros (a, b, c, d) salen de 6 ramas; Atractor elige/interpola la rama, cada `Cada` kicks salta a la siguiente,
// el bajo y la distorsion los deforman despacio.
uniform float u_frame;
uniform float u_time;
uniform float u_speed;
uniform float u_warp;
uniform float u_low;
uniform float u_forma;       // firma (0..1): rama base
uniform float u_step;        // contador de kicks
uniform float u_cada;        // kicks por cambio de rama
out vec4 fragColor;

float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }

const vec4 RAMAS[6] = vec4[6](
    vec4(-1.4,  1.6,  1.0,  0.7),
    vec4( 1.7,  1.7,  0.6,  1.2),
    vec4( 1.5, -1.8,  1.6,  0.9),
    vec4(-1.7,  1.3, -0.1, -1.21),
    vec4(-1.7,  1.8, -1.9, -0.4),
    vec4(-1.8, -2.0, -0.5, -0.9)
);

void main() {
    float i = floor(gl_FragCoord.x);
    float t = u_time * max(u_speed, 0.0);
    float salto = floor(max(u_step, 0.0) / max(floor(u_cada + 0.5), 1.0));
    float base = clamp(u_forma, 0.0, 1.0) * 5.0 + salto;
    int i0 = int(mod(floor(base), 6.0));
    int i1 = int(mod(floor(base) + 1.0, 6.0));
    vec4 P = mix(RAMAS[i0], RAMAS[i1], smoothstep(0.0, 1.0, fract(base)));
    float lo = clamp(u_low, 0.0, 2.0);
    P += vec4(sin(t * 0.07), cos(t * 0.05), 0.6 * sin(t * 0.09 + 1.0), 0.6 * cos(t * 0.06 + 2.0)) * 0.12 * u_warp;
    P.xy += vec2(0.07, -0.05) * lo;                     // el bajo deforma la figura, sin saltos

    vec2 x = (vec2(hash21(vec2(i, u_frame)), hash21(vec2(u_frame * 1.37, i + 91.0))) - 0.5) * 3.0;
    vec2 antes = x;
    for (int n = 0; n < 40; n++) {
        antes = x;
        x = vec2(sin(P.x * x.y) + P.z * cos(P.x * x.x),
                 sin(P.y * x.x) + P.w * cos(P.y * x.y));
    }
    vec2 ext = 1.0 + abs(P.zw);
    fragColor = vec4(x / ext, length(x - antes) / length(ext), 1.0);
}
