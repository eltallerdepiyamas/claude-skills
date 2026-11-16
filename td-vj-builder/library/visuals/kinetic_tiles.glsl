// kinetic_tiles.glsl: reticula de tiles cineticos (recetario 28; ref. Matthew Ragan "instancing", tutorial Ikeda de
// Jack DiLaura, paneles cineticos tipo flip-dot / Truchet). Version en shader: cada tile es una pieza Truchet (dos
// arcos de cuarto de circulo de 1 px) con una orientacion en cuartos de vuelta. Los arcos de tiles vecinos se unen
// y forman recorridos largos; al girar un tile el recorrido se reconecta.
// Kick: Step sortea una orientacion nueva para cada tile y la ola de volteo sale del centro mientras el kick cae
// (frente = (1 - kick)): cada tile se voltea (se aplasta de canto, destello en el canto) al pasarle el frente.
// Audio por anillos: bajos al centro, medios en el anillo medio, agudos afuera (ondulan y se iluminan).
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
uniform float u_warp;        // 3 distorsion: ola continua de giro
uniform float u_tono;
uniform float u_firma;       // 5 firma: tamano del tile en pixeles
out vec4 fragColor;
#define PI 3.14159265

float hash21(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

void main() {
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    float paso = floor(u_step + 0.5);
    vec3 tinta = mix(u_color1, u_color2, u_tono);

    float ts = floor(clamp(u_firma, 24.0, 160.0));
    vec2 px = gl_FragCoord.xy - 0.5 * u_res;                // pixeles desde el centro
    vec2 id = floor(px / ts);
    vec2 q = (px - (id + 0.5) * ts) / ts;                   // -0.5..0.5 dentro del tile
    vec2 cpos = (id + 0.5) * ts / u_res.y;                  // centro del tile en alturas de pantalla
    float r = length(cpos);

    // ---- orientaciones: la de antes del ultimo kick y la nueva (cuartos de vuelta)
    float a0 = floor(hash21(id + (paso - 1.0) * 13.17) * 4.0);
    float a1 = floor(hash21(id + paso * 13.17) * 4.0);
    float dif = a1 - a0;
    if (dif > 2.0) dif -= 4.0;
    if (dif < -2.0) dif += 4.0;
    // ola de volteo: el frente sale del centro mientras el kick cae
    float frente = (1.0 - k) * 1.3;
    float pr = smoothstep(0.0, 1.0, clamp((frente - r) / 0.14, 0.0, 1.0));
    float canto = sin(PI * pr);                             // 1 a media vuelta (tile de canto)

    // ---- audio por anillos: el audio se lee por radio
    float aLo = lo * (1.0 - smoothstep(0.12, 0.3, r));
    float aMi = mi * smoothstep(0.15, 0.3, r) * (1.0 - smoothstep(0.42, 0.58, r));
    float aHi = hi * smoothstep(0.45, 0.65, r);
    float banda = aLo + aMi + aHi;
    float ola = 0.12 * clamp(u_warp, 0.0, 1.0) * sin(t * 1.1 - r * 9.0) + 0.22 * banda * sin(t * 2.3 - r * 14.0);

    float ang = (a0 + dif * pr) * 0.5 * PI + ola;
    vec2 qr = rot(ang) * q;
    // volteo 3D: el tile se aplasta de canto al pasar el frente
    float aplasta = max(abs(cos(PI * pr)), 0.12);
    qr.y /= aplasta;

    // ---- Truchet: dos arcos de radio 0.5 centrados en esquinas opuestas
    float d = min(abs(length(qr - vec2(0.5)) - 0.5), abs(length(qr + vec2(0.5)) - 0.5));
    float w = 1.1 / ts * (1.0 + 0.8 * banda);
    float linea = 1.0 - smoothstep(w * 0.5, w * 1.5, d);
    linea *= step(abs(qr.y), 0.5) * step(abs(qr.x), 0.5);   // no salir del tile al aplastarse

    // punto fino en cada esquina de la reticula
    vec2 esq = abs(fract(px / ts + 0.5) - 0.5) * ts;
    float punto = 1.0 - smoothstep(0.6, 1.6, length(esq));

    float luz = linea * (0.4 + 0.45 * banda + 0.5 * canto) + punto * 0.12;
    float blanco = linea * canto * 0.35 * smoothstep(0.05, 0.4, k);
    float vin = 1.0 - smoothstep(0.55, 1.05, r);            // los bordes se apagan: el negro manda
    vec3 col = (tinta * luz * 0.6 + vec3(1.0) * blanco * 0.5) * vin;
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
