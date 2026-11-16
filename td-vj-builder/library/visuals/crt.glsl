// crt.glsl: osciladores de video vistos en un monitor CRT (recetarios 36 y 43; ref. LZX Industries (Prismatic Ray,
// DWO3, Scrolls), Hypno; Basement Vibes ANALOG_TV / Perfect Scanlines para el acabado). Distinto de Sinte LZX:
// aqui no hay rampa radial ni wavefolder: es el raster. Un oscilador horizontal (barras verticales) por uno vertical
// (barras horizontales) = rejilla/tablero; el bajo es el CV de la FM de linea. La senal pasa por un ancho de banda
// limitado (Ancho de banda, slot 5: sangrado horizontal de 9 tomas + pasa altos con ringing) y se ve en un tubo:
// barril, scanlines, mascara de fosforo en luminancia, barra de rolado que baja despacio (vertical hold).
// Kick: salto de sincronia breve (la imagen salta en vertical y unas lineas se desgarran), solo la cresta del golpe.
// Agudos: nieve fina. Medios: frecuencia del oscilador vertical.
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
uniform float u_warp;        // 3 distorsion: frecuencia/curvatura de los osciladores
uniform float u_tono;
uniform float u_firma;       // 5 firma: ancho de banda (pixeles de sangrado horizontal)
out vec4 fragColor;
#define PI 3.14159265
#define TAU 6.2831853

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float osc(float x) { return 0.5 + 0.5 * sin(TAU * x); }

// la senal de video en coordenadas de raster (x, y en 0..1); salida 0..1
float senal(vec2 r, float t, float lo, float mi, float paso) {
    float fase = paso * 0.25;                                   // cada kick salta un cuarto de ciclo
    float fH = 5.0 + 6.0 * clamp(u_warp, 0.0, 1.0);
    float fV = 3.0 + 2.0 * clamp(mi, 0.0, 1.5);
    float fm = 0.35 * lo * sin(TAU * (r.y * 7.0 - t * 0.31));  // FM de linea: el bajo dobla las barras
    float oH = osc(r.x * fH - t * 0.07 + fm + fase);
    float oV = osc(r.y * fV + t * 0.045 - fase * 0.5);
    float rejilla = oH * oV;
    // keyer: bordes duros antes del ancho de banda (asi el sangrado se nota)
    float k1 = smoothstep(0.42, 0.47, rejilla);
    float k2 = smoothstep(0.80, 0.83, rejilla);
    return k1 * 0.55 + k2 * 0.45;
}

void main() {
    vec2 uv = vUV.st;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float golpe = smoothstep(0.6, 1.0, k);
    float t = u_time * u_speed;
    float paso = floor(u_step + 0.5);
    vec3 tinta = mix(u_color1, u_color2, u_tono);

    // ---- tubo: barril + pantalla con margen negro
    vec2 c = uv * 2.0 - 1.0;
    c *= vec2(1.0 + 0.06 * c.y * c.y, 1.0 + 0.08 * c.x * c.x);
    c *= 1.09;
    vec2 sq = abs(c) - vec2(0.86, 0.80);
    float caja = length(max(sq, 0.0)) + min(max(sq.x, sq.y), 0.0) - 0.12;   // rectangulo redondeado
    float pantalla = 1.0 - smoothstep(-0.01, 0.005, caja);
    vec2 r = c * 0.5 + 0.5;                                      // coordenadas de raster

    // ---- sincronia: rolado lento + salto vertical y desgarro de lineas en el kick
    float roll = fract(t * 0.015) + golpe * 0.11 * (hash11(paso * 3.1) - 0.3);
    float lineas = 240.0;
    float ln = floor(r.y * lineas);
    float desg = golpe * step(0.55, hash11(ln * 0.13 + paso * 7.0)) * (hash11(ln + paso) - 0.5) * 0.12;
    vec2 rr = vec2(r.x + desg + (hash11(ln + floor(u_time * 30.0)) - 0.5) * 0.002 * hi, fract(r.y + roll));

    // ---- ancho de banda: 9 tomas horizontales + pasa altos (ringing de "enhance")
    float bw = clamp(u_firma, 0.0, 16.0) / u_res.x;
    float s0 = senal(rr, t, lo, mi, paso);
    float acc = s0, wsum = 1.0;
    for (int i = 1; i <= 4; i++) {
        float w = 1.0 - float(i) / 5.0;
        acc += w * (senal(rr + vec2(bw * float(i), 0.0), t, lo, mi, paso)
                  + senal(rr - vec2(bw * float(i), 0.0), t, lo, mi, paso));
        wsum += 2.0 * w;
    }
    float sb = acc / wsum;
    // mezcla: senal sangrada + realce de bordes (el pasa altos deja el ringing claro junto a cada borde)
    float sig = clamp(sb + 0.55 * (s0 - sb), 0.0, 1.1);

    // ---- barra de rolado (mas oscura) y nieve (agudos)
    float yb = (fract(r.y - t * 0.05) - 0.5) * 7.0;
    float barra = 1.0 - 0.3 * exp(-yb * yb);
    float nieve = (hash21(floor(uv * u_res * 0.5) + floor(u_time * 30.0) * 1.7) - 0.5) * 0.12 * hi;

    // ---- scanlines y mascara de fosforo (solo luminancia: nunca RGB fijo)
    float scan = 0.62 + 0.38 * pow(abs(cos(PI * r.y * lineas)), 0.6);
    float masc = 0.9 + 0.1 * cos(TAU * gl_FragCoord.x / 3.0);
    float lum = clamp((sig * barra + nieve) * scan * masc, 0.0, 1.2);

    vec3 col = tinta * lum * 0.62 + vec3(1.0) * smoothstep(0.9, 1.1, lum) * 0.12;
    // reflejo muy tenue del borde del tubo
    float canto = (1.0 - smoothstep(0.0, 0.012, abs(caja))) * 0.06;
    col = col * pantalla + tinta * canto;
    vec2 v = uv - 0.5;
    col *= 1.0 - 0.8 * dot(v, v);
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
