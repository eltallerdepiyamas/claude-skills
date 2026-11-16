// anillo_saturno.glsl: anillo planetario visto un poco de lado. Polvo finisimo en anillos con divisiones
// (como la de Cassini) que gira mas rapido adentro (Kepler). El kick lanza una onda de densidad en espiral
// que recorre el anillo; los agudos hacen brillar el polvo. Centro en negro.
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
uniform float u_warp;        // 3 distorsion: inclinacion del anillo (0 de frente, 1 casi de canto)
uniform float u_tono;
uniform float u_firma;       // 5 firma: finura de los anillos (cuantas divisiones)
out vec4 fragColor;
#define PI 3.14159265
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float noise1(float x) { float i = floor(x), f = fract(x); return mix(hash11(i), hash11(i + 1.0), f * f * (3.0 - 2.0 * f)); }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float incl = mix(0.85, 0.18, clamp(u_warp, 0.0, 1.0));    // achatamiento por la inclinacion
    float c = cos(0.18), s = sin(0.18);
    p = mat2(c, -s, s, c) * p;
    vec2 q = vec2(p.x, p.y / incl);
    float r = length(q), a = atan(q.y, q.x);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    float rin = 0.16, rout = 0.46;
    float x = (r - rin) / (rout - rin);                      // 0 borde interior · 1 exterior
    float dentro = step(0.0, x) * step(x, 1.0);
    // perfil radial: ringlets finos + division de Cassini + huecos menores
    float fino = clamp(u_firma, 20.0, 400.0);
    float perfil = pow(0.15 + 0.85 * noise1(x * fino) * (0.55 + 0.45 * noise1(x * fino * 0.13 + 7.0)), 1.6);
    perfil *= 1.0 - 0.95 * exp(-pow((x - 0.62) * 40.0, 2.0));        // Cassini
    perfil *= 1.0 - 0.7 * exp(-pow((x - 0.88) * 90.0, 2.0));         // Encke
    perfil *= smoothstep(0.0, 0.05, x) * smoothstep(1.0, 0.93, x);
    // polvo: grano en (radio, angulo) que gira con velocidad de Kepler (adentro mas rapido)
    float w = 0.4 * pow(max(r, 0.05) / rout, -1.5);
    float ang = a + t * 0.05 * w;
    vec2 celda = floor(vec2(x * 900.0, ang * 220.0 / PI));
    float polvo = 0.55 + 0.45 * hash21(celda);
    // onda de densidad en espiral que lanza el kick y empuja el bajo
    float espiral = sin(2.0 * ang - x * 40.0 + t * 1.5);
    float onda = 1.0 + (0.25 * lo + 0.9 * k) * espiral;
    // la mitad de atras del anillo pasa detras del planeta invisible: se apaga un poco
    float atras = 1.0 - 0.45 * smoothstep(0.0, 0.25, q.y) * (1.0 - smoothstep(0.0, 0.2, abs(q.x) - rin));
    float chispa = step(0.996 - 0.01 * hi, hash21(celda + floor(t * 10.0))) * hi;
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    float d = perfil * polvo * onda * dentro * atras;
    vec3 col = mix(tono, vec3(1.0), 0.12) * d * (1.1 + 0.5 * lo) + mix(tono, vec3(1.0), 0.4) * chispa * dentro + otro * d * k * 0.25;
    col *= 1.0 - smoothstep(0.42, 0.5, length(p));           // sin bordes duros afuera
    fragColor = TDOutputSwizzle(vec4(u_color3 + col * u_intensity, 1.0));
}
