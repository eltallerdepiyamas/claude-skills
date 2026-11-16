// feedback_analogico.glsl: feedback de video analogico con frame delay (recetario 40; ref. Hypno / Andrei Jay VIDEO_WAAAVES, LZX Memory Palace).
// Una voz fina (arco de anillo + punto, como un oscilador de forma) entra al loop; el cuadro anterior vuelve con
// rotacion, zoom que alterna y desplazamiento, con sangrado horizontal. Un eco de N cuadros atras (Texture 3D +
// Time Machine) se cruza con transformacion opuesta. En cada kick la ganancia se vuelve negativa UNA vuelta dentro
// del disco: destello negativo en la tinta que se desvanece, no strobe.
// sTD2DInputs[0] = cuadro anterior (feedback1) / sTD2DInputs[1] = cuadro de hace N (eco, 960x540).
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
uniform float u_warp;        // 3 distorsion: rotacion / desplazamiento por vuelta
uniform float u_tono;
uniform float u_firma;       // 5 firma: retardo del eco en cuadros (lo usa el Time Machine; aqui pesa el eco)
uniform float u_ganancia;    // extra: ganancia del loop (<1)
uniform float u_negativo;    // extra: cuanto invierte el kick
out vec4 fragColor;
#define PI 3.14159265
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }
float dentroUV(vec2 u) { vec2 b = step(vec2(0.0), u) * step(u, vec2(1.0)); return b.x * b.y; }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    vec3 tinta = mix(u_color1, u_color2, u_tono);

    // ---- transformacion de cada vuelta (el zoom alterna: nunca un tunel continuo)
    float ang = 0.004 + 0.022 * u_warp * sin(t * 0.13 + 1.0);
    float zoom = 1.0 + 0.007 * sin(t * 0.21) - 0.006 * lo;
    vec2 off = vec2(0.0022 * sin(t * 0.17), 0.0014 * cos(t * 0.11)) * (1.0 + 2.0 * u_warp);
    vec2 q = rot(ang) * p * zoom + off;
    // ruido de sincronia: cada linea se corre un poco con los agudos
    float linea = floor(uv.y * u_res.y * 0.5);
    q.x += (hash11(linea + floor(u_time * 24.0) * 7.0) - 0.5) * 0.0025 * hi;
    vec2 uq = vec2(q.x / asp + 0.5, q.y + 0.5);
    float px = 1.0 / u_res.x;
    vec3 prev = texture(sTD2DInputs[0], uq).rgb * 0.5
              + texture(sTD2DInputs[0], uq + vec2(1.5 * px, 0.0)).rgb * 0.25
              + texture(sTD2DInputs[0], uq - vec2(1.5 * px, 0.0)).rgb * 0.25;   // pasa bajos horizontal, como analogico
    prev *= dentroUV(uq);

    // ---- eco de N cuadros, con la transformacion al reves: se cruza con el loop
    vec2 qe = rot(-ang * 3.0) * p / zoom - off * 2.0;
    vec2 ue = vec2(qe.x / asp + 0.5, qe.y + 0.5);
    vec3 eco = texture(sTD2DInputs[1], ue).rgb * dentroUV(ue);
    float pesoEco = 0.45 + 0.25 * clamp(u_firma / 15.0, 0.0, 1.0);
    vec3 col = max(prev, eco * pesoEco) * clamp(u_ganancia, 0.0, 0.985);

    // ---- voz: arco fino de anillo que gira + punto que orbita (oscilador de forma)
    float r = length(p), a = atan(p.y, p.x);
    float r0 = 0.15 + 0.03 * sin(t * 0.3) + 0.05 * lo;
    float w = 1.6 / u_res.y;
    float anillo = smoothstep(w * 1.5, 0.0, abs(r - r0));
    float arco = smoothstep(-0.2, 0.6, sin(a - t * 0.7));
    vec2 pd = r0 * 1.6 * vec2(cos(t * 0.45), sin(t * 0.45));
    float punto = smoothstep(w * 3.0, 0.0, length(p - pd));
    float voz = anillo * arco * (0.45 + 0.4 * lo) + punto * 0.6;
    col = max(col, tinta * voz * clamp(u_intensity, 0.0, 2.0));   // S1 = nivel de entrada al loop (la ganancia no cambia)

    // ---- ganancia negativa en el kick: una sola vuelta (se detecta el cambio de Step guardado en el pixel 0,0)
    float codigo = mod(floor(u_step + 0.5), 64.0);
    float antes = (texelFetch(sTD2DInputs[0], ivec2(0, 0), 0).a - 0.5) * 128.0;
    float golpe = abs(codigo - antes) > 0.5 ? 1.0 : 0.0;
    float disco = smoothstep(0.43, 0.38, r);
    vec3 inv = clamp(tinta * 0.5 - col, 0.0, 1.0);
    col = mix(col, inv, golpe * clamp(u_negativo, 0.0, 1.0) * disco);

    col = clamp(col, 0.0, 1.0);
    ivec2 ij = ivec2(gl_FragCoord.xy);
    float alfa = (ij.x == 0 && ij.y == 0) ? 0.5 + codigo / 128.0 : 1.0;
    // la salida ES la memoria del loop: nada la amplifica aqui (si no, se satura)
    fragColor = TDOutputSwizzle(vec4(max(col, u_color3), alfa));
}
